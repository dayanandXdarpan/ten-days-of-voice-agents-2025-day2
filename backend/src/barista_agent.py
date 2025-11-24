import json
import logging
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Annotated, Any

from dotenv import load_dotenv
from livekit.agents import (
    Agent,
    AgentSession,
    JobContext,
    JobProcess,
    MetricsCollectedEvent,
    RoomInputOptions,
    RunContext,
    WorkerOptions,
    cli,
    function_tool,
    metrics,
    tokenize,
)
from livekit.plugins import deepgram, google, murf, silero
from livekit.plugins.turn_detector.multilingual import MultilingualModel
from pydantic import BaseModel, Field

logger = logging.getLogger("barista-agent")

load_dotenv(".env.local")


# Order State Model
class CoffeeOrder(BaseModel):
    """Represents a customer's coffee order"""
    drink_type: str | None = Field(None, description="Type of drink (e.g., 'latte', 'cappuccino', 'espresso')")
    size: str | None = Field(None, description="Size of drink ('small', 'medium', 'large')")
    milk: str | None = Field(None, description="Type of milk ('whole', 'skim', 'oat', 'almond', 'soy')")
    extras: list[str] = Field(default_factory=list, description="Extra additions (e.g., 'extra shot', 'whipped cream', 'caramel drizzle')")
    name: str | None = Field(None, description="Customer name for the order")

    def is_complete(self) -> bool:
        """Check if all required fields are filled"""
        return all([
            self.drink_type,
            self.size,
            self.milk,
            self.name
        ])

    def get_missing_fields(self) -> list[str]:
        """Get list of missing required fields"""
        missing = []
        if not self.drink_type:
            missing.append("drink type")
        if not self.size:
            missing.append("size")
        if not self.milk:
            missing.append("milk preference")
        if not self.name:
            missing.append("name")
        return missing


@dataclass
class BaristaUserdata:
    """User data for barista agent session"""
    current_order: Any = None
    orders_saved: int = 0

    def __post_init__(self):
        # Lazily create a CoffeeOrder instance to avoid static analysis issues
        if self.current_order is None:
            self.current_order = CoffeeOrder(**{})


# Coffee Shop Menu
COFFEE_MENU = {
    "drinks": [
        "Espresso", "Americano", "Latte", "Cappuccino", "Mocha", 
        "Macchiato", "Flat White", "Cortado", "Cold Brew", "Iced Coffee"
    ],
    "sizes": ["Small", "Medium", "Large"],
    "milk_options": ["Whole Milk", "Skim Milk", "Oat Milk", "Almond Milk", "Soy Milk", "Coconut Milk"],
    "extras": [
        "Extra Shot", "Whipped Cream", "Caramel Drizzle", "Chocolate Syrup",
        "Vanilla Syrup", "Hazelnut Syrup", "Cinnamon", "Honey"
    ]
}


class CoffeeBaristaAgent(Agent):
    def __init__(self) -> None:
        # Create friendly barista persona with menu knowledge
        menu_text = self._format_menu()
        
        super().__init__(
            instructions=f"""You are Emma, a friendly and enthusiastic barista at Murf's Coffee House, a cozy artisan coffee shop known for using Murf Falcon - the fastest coffee brewing technology!

{menu_text}

YOUR PERSONALITY:
- Warm, friendly, and genuinely excited about coffee
- Use a conversational, natural tone (avoid formal language)
- Show enthusiasm when customers order
- Be patient and helpful with questions

YOUR JOB:
1. Greet customers warmly and ask what they'd like to order
2. Guide them through building their perfect coffee order
3. Ask clarifying questions ONE AT A TIME to fill in missing information:
   - What type of drink? (if not specified)
   - What size? (if not specified)
   - What kind of milk? (if not specified)
   - Would they like any extras? (always ask, even if they don't mention any)
   - What name for the order? (always ask at the end)
4. Confirm the complete order before finalizing
5. Use the save_order tool ONLY when all fields are confirmed

IMPORTANT RULES:
- Ask ONE question at a time - don't overwhelm customers
- If they mention a drink, immediately ask about size if they didn't specify
- If they mention size, ask about milk preference if they didn't specify
- Always suggest popular extras but don't push
- Get their name at the very end before saving
- Confirm the full order verbally before calling save_order
- Keep responses SHORT and conversational (1-2 sentences max)
- Don't use markdown, asterisks, or emoji in your speech

EXAMPLE FLOW:
Customer: "I'd like a coffee"
You: "Great! What kind of coffee would you like? We have lattes, cappuccinos, americanos, and more."
Customer: "A latte"
You: "Perfect! What size - small, medium, or large?"
Customer: "Medium"
You: "Excellent! What type of milk would you prefer? We have whole, oat, almond, soy, and skim."
Customer: "Oat milk please"
You: "Love it! Would you like to add anything extra? Maybe an extra shot, whipped cream, or flavored syrup?"
Customer: "No thanks"
You: "Sounds good! And what name should I put on this order?"
Customer: "Sarah"
You: "Perfect! So that's one medium oat milk latte for Sarah. Does that sound right?"
Customer: "Yes!"
You: "Awesome! Let me get that started for you."
[Then call save_order tool]

Remember: You're here to make every customer feel welcome and help them find their perfect coffee!""",
        )

    def _format_menu(self) -> str:
        """Format the coffee menu for the agent's instructions"""
        return f"""
OUR MENU:
Drinks: {', '.join(COFFEE_MENU['drinks'])}
Sizes: {', '.join(COFFEE_MENU['sizes'])}
Milk Options: {', '.join(COFFEE_MENU['milk_options'])}
Popular Extras: {', '.join(COFFEE_MENU['extras'])}
"""

    @function_tool()
    async def update_drink_type(
        self,
        context: RunContext[BaristaUserdata],
        drink_type: Annotated[str, Field(description="The type of coffee drink the customer wants")],
    ) -> str:
        """Updates the drink type in the customer's order.
        
        Call this when the customer specifies what kind of coffee they want.
        The drink type should match one from our menu (case-insensitive).
        """
        userdata = context.userdata
        
        # Normalize and validate drink type
        drink_type_normalized = drink_type.lower().strip()
        
        # Check if it matches any menu item (case-insensitive)
        valid_drinks = [d.lower() for d in COFFEE_MENU['drinks']]
        if drink_type_normalized not in valid_drinks:
            return f"I'm sorry, we don't have {drink_type} on our menu. Our drinks are: {', '.join(COFFEE_MENU['drinks'])}"
        
        userdata.current_order.drink_type = drink_type.title()
        logger.info(f"Updated drink type: {userdata.current_order.drink_type}")
        
        return f"Got it, {userdata.current_order.drink_type}!"

    @function_tool()
    async def update_size(
        self,
        context: RunContext[BaristaUserdata],
        size: Annotated[str, Field(description="The size of the drink: small, medium, or large")],
    ) -> str:
        """Updates the size in the customer's order.
        
        Call this when the customer specifies the size they want.
        Valid sizes: small, medium, large (case-insensitive).
        """
        userdata = context.userdata
        
        # Normalize size
        size_normalized = size.lower().strip()
        if size_normalized not in ['small', 'medium', 'large']:
            return f"I didn't catch that size. We have small, medium, or large."
        
        userdata.current_order.size = size_normalized
        logger.info(f"Updated size: {userdata.current_order.size}")
        
        return f"Perfect, {userdata.current_order.size} size!"

    @function_tool()
    async def update_milk(
        self,
        context: RunContext[BaristaUserdata],
        milk: Annotated[str, Field(description="The type of milk: whole, skim, oat, almond, soy, coconut")],
    ) -> str:
        """Updates the milk preference in the customer's order.
        
        Call this when the customer specifies their milk choice.
        Common options: whole milk, skim milk, oat milk, almond milk, soy milk, coconut milk.
        """
        userdata = context.userdata
        
        # Normalize milk type
        milk_normalized = milk.lower().strip()
        
        # Handle common variations
        if 'oat' in milk_normalized:
            milk_normalized = 'oat milk'
        elif 'almond' in milk_normalized:
            milk_normalized = 'almond milk'
        elif 'soy' in milk_normalized:
            milk_normalized = 'soy milk'
        elif 'skim' in milk_normalized:
            milk_normalized = 'skim milk'
        elif 'whole' in milk_normalized:
            milk_normalized = 'whole milk'
        elif 'coconut' in milk_normalized:
            milk_normalized = 'coconut milk'
        
        userdata.current_order.milk = milk_normalized
        logger.info(f"Updated milk: {userdata.current_order.milk}")
        
        return f"Great choice, {userdata.current_order.milk}!"

    @function_tool()
    async def add_extras(
        self,
        context: RunContext[BaristaUserdata],
        extras: Annotated[list[str], Field(description="List of extra additions the customer wants")],
    ) -> str:
        """Adds extra items to the customer's order.
        
        Call this when the customer wants to add extras like:
        - Extra shot
        - Whipped cream
        - Flavored syrups (vanilla, caramel, hazelnut, chocolate)
        - Toppings (cinnamon, honey)
        
        The extras list should be the complete list of all extras they want.
        """
        userdata = context.userdata
        
        # Normalize extras
        normalized_extras = [extra.lower().strip() for extra in extras]
        userdata.current_order.extras = normalized_extras
        
        logger.info(f"Updated extras: {userdata.current_order.extras}")
        
        if not extras:
            return "No extras, got it!"
        
        extras_str = ', '.join(normalized_extras)
        return f"Adding {extras_str}!"

    @function_tool()
    async def update_name(
        self,
        context: RunContext[BaristaUserdata],
        name: Annotated[str, Field(description="The customer's name for the order")],
    ) -> str:
        """Updates the customer name for the order.
        
        Call this when the customer provides their name.
        This should be one of the last pieces of information collected.
        """
        userdata = context.userdata
        
        userdata.current_order.name = name.strip().title()
        logger.info(f"Updated name: {userdata.current_order.name}")
        
        return f"Perfect, {userdata.current_order.name}!"

    @function_tool()
    async def check_order_status(
        self,
        context: RunContext[BaristaUserdata],
    ) -> str:
        """Checks what information is still needed for the order.
        
        Call this to see what fields are missing and what's been filled in so far.
        Useful for reminding yourself what to ask next.
        """
        userdata = context.userdata
        order = userdata.current_order
        
        status = "Current order status:\n"
        status += f"Drink: {order.drink_type or 'NOT SET'}\n"
        status += f"Size: {order.size or 'NOT SET'}\n"
        status += f"Milk: {order.milk or 'NOT SET'}\n"
        status += f"Extras: {', '.join(order.extras) if order.extras else 'none'}\n"
        status += f"Name: {order.name or 'NOT SET'}\n"
        
        missing = order.get_missing_fields()
        if missing:
            status += f"\nStill need to ask about: {', '.join(missing)}"
        else:
            status += "\nOrder is complete! Ready to save."
        
        return status

    @function_tool()
    async def save_order(
        self,
        context: RunContext[BaristaUserdata],
    ) -> str:
        """Saves the completed order to a JSON file.
        
        ONLY call this when:
        1. All required fields are filled (drink_type, size, milk, name)
        2. You've confirmed the order with the customer verbally
        3. The customer has approved the order
        
        Do NOT call this if any required field is missing!
        """
        userdata = context.userdata
        order = userdata.current_order
        
        # Validate order is complete
        if not order.is_complete():
            missing = order.get_missing_fields()
            return f"Cannot save order yet! Still missing: {', '.join(missing)}. Please collect this information first."
        
        # Create orders directory if it doesn't exist
        orders_dir = Path("orders")
        orders_dir.mkdir(exist_ok=True)
        
        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_name = (order.name or "unknown").replace(' ', '_')
        filename = orders_dir / f"order_{timestamp}_{safe_name}.json"
        
        # Prepare order data with metadata
        order_data = {
            "timestamp": datetime.now().isoformat(),
            "order_number": userdata.orders_saved + 1,
            "order": {
                "drinkType": order.drink_type,
                "size": order.size,
                "milk": order.milk,
                "extras": order.extras,
                "name": order.name
            }
        }
        
        # Save to JSON file
        try:
            with open(filename, 'w') as f:
                json.dump(order_data, f, indent=2)
            
            userdata.orders_saved += 1
            logger.info(f"Order saved successfully: {filename}")
            logger.info(f"Order details: {json.dumps(order_data, indent=2)}")
            
            # Reset order for next customer (explicit empty kwargs to help type checkers)
            userdata.current_order = CoffeeOrder(**{})
            
            return f"Order saved successfully! Order #{order_data['order_number']} for {order.name} is all set. File saved as {filename.name}"
            
        except Exception as e:
            logger.error(f"Error saving order: {e}")
            return f"Sorry, there was an error saving the order: {str(e)}"


def prewarm(proc: JobProcess):
    """Prewarm the VAD model for faster startup"""
    proc.userdata["vad"] = silero.VAD.load()


async def entrypoint(ctx: JobContext):
    """Main entry point for the barista agent"""
    
    # Logging setup
    ctx.log_context_fields = {
        "room": ctx.room.name,
        "agent": "coffee-barista",
    }

    # Initialize userdata
    userdata = BaristaUserdata()

    # Set up voice AI pipeline
    session = AgentSession[BaristaUserdata](
        userdata=userdata,
        # Speech-to-text with optimized settings for coffee ordering
        stt=deepgram.STT(
            model="nova-3",
            # Add coffee-related keywords for better recognition
            keywords=[
                ("latte", 1.5),
                ("cappuccino", 1.5),
                ("espresso", 1.5),
                ("americano", 1.5),
                ("mocha", 1.5),
                ("macchiato", 1.5),
                ("oat milk", 1.5),
                ("almond milk", 1.5),
            ]
        ),
        # LLM for natural conversation
        llm=google.LLM(
            model="gemini-2.5-flash",
            temperature=0.7,  # Slightly more creative for friendlier responses
        ),
        # TTS with conversational style
        tts=murf.TTS(
            voice="en-US-matthew",  # Friendly barista voice
            style="Conversation",
            tokenizer=tokenize.basic.SentenceTokenizer(min_sentence_len=2),
            text_pacing=True
        ),
        # Turn detection for natural conversation flow
        turn_detection=MultilingualModel(),
        vad=ctx.proc.userdata["vad"],
        preemptive_generation=True,
        # Limit tool steps to prevent loops
        max_tool_steps=15,
    )

    # Metrics collection
    usage_collector = metrics.UsageCollector()

    @session.on("metrics_collected")
    def _on_metrics_collected(ev: MetricsCollectedEvent):
        metrics.log_metrics(ev.metrics)
        usage_collector.collect(ev.metrics)

    async def log_usage():
        summary = usage_collector.get_summary()
        logger.info(f"Session usage: {summary}")
        logger.info(f"Total orders processed: {userdata.orders_saved}")

    ctx.add_shutdown_callback(log_usage)

    # Start the session
    await session.start(
        agent=CoffeeBaristaAgent(),
        room=ctx.room,
        room_input_options=RoomInputOptions(
            # BVC commented out for local development (Day 1 fix preserved)
            # noise_cancellation=noise_cancellation.BVC(),
        ),
    )

    # Join the room
    await ctx.connect()

    # Optional: Greet the customer
    # await session.output.speak("Hi! Welcome to Murf's Coffee House! What can I get started for you today?")


if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint, prewarm_fnc=prewarm))
