import json
import logging
import multiprocessing
import os
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Annotated
import aiohttp

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
from pydantic import BaseModel, Field

logger = logging.getLogger("coffee-shop-agent")

load_dotenv(".env.local")

# Phonetic correction mappings for common STT errors
PHONETIC_CORRECTIONS = {
    # Payment methods
    "cats on delivery": "cash on delivery",
    "cast on delivery": "cash on delivery",
    "cash delivery": "cash on delivery",
    "cod": "cash on delivery",
    "google pay": "google pay",
    "phone pay": "phonepe",
    "phone pe": "phonepe",
    "paytm": "paytm",
    "pay tm": "paytm",
    
    # Locations (India-specific corrections)
    "patna jungson": "patna junction",
    "jungson": "junction",
    "patna junction": "patna junction",
    "behar": "bihar",
    "bihar": "bihar",
    
    # Coffee terms
    "latte": "latte",
    "latay": "latte",
    "cappuccino": "cappuccino",
    "capuccino": "cappuccino",
    "expresso": "espresso",
    "macchiato": "macchiato",
    "mocha": "mocha",
    "moka": "mocha",
    
    # Milk options
    "oat milk": "oat milk",
    "ot milk": "oat milk",
    "almond milk": "almond milk",
    "alman milk": "almond milk",
    "coconut milk": "coconut milk",
    "cocoanut milk": "coconut milk",
    
    # Sizes
    "medium": "medium",
    "midium": "medium",
    "large": "large",
    "small": "small",
}

def apply_phonetic_corrections(text: str) -> str:
    """Apply phonetic corrections to user transcript"""
    if not text:
        return text
    
    text_lower = text.lower().strip()
    
    # Check for full phrase matches first
    if text_lower in PHONETIC_CORRECTIONS:
        corrected = PHONETIC_CORRECTIONS[text_lower]
        logger.debug(f"Corrected '{text}' -> '{corrected}'")
        return corrected
    
    # Check for partial matches
    for incorrect, correct in PHONETIC_CORRECTIONS.items():
        if incorrect in text_lower:
            text_lower = text_lower.replace(incorrect, correct)
            logger.debug(f"Partial correction applied: '{text}' -> '{text_lower}'")
    
    return text_lower

def clean_spelled_name(text: str) -> str:
    """Clean up spelled-out names like 'D a y a n a n d' -> 'Dayanand'"""
    if not text:
        return text
    
    # Check if text contains single letters with spaces (spelling pattern)
    words = text.split()
    
    # If most words are single letters, it's likely a spelled name
    single_letters = [w for w in words if len(w) == 1 and w.isalpha()]
    if len(single_letters) >= 3 and len(single_letters) > len(words) * 0.5:
        # Join letters without spaces and capitalize
        cleaned = ''.join(single_letters).capitalize()
        logger.debug(f"Cleaned spelled name '{text}' -> '{cleaned}'")
        return cleaned
    
    return text.strip()


# Order State Model with Enhanced Fields
class CoffeeOrder(BaseModel):
    """Represents a complete customer coffee order"""
    drink_type: str | None = Field(None, description="Type of drink (e.g., 'Latte', 'Cappuccino')")
    size: str | None = Field(None, description="Size: Small, Medium, or Large")
    milk: str | None = Field(None, description="Type of milk (Whole, Oat, Almond, etc.)")
    extras: list[str] = Field(default_factory=list, description="Extra additions")
    name: str | None = Field(None, description="Customer name")
    name_confirmed: bool = Field(False, description="Whether name spelling was confirmed")
    delivery_address: str | None = Field(None, description="Delivery address for the order")
    address_confirmed: bool = Field(False, description="Whether address was confirmed")
    payment_method: str | None = Field(None, description="Payment method (Cash, Card, UPI, etc.)")
    order_id: str | None = Field(None, description="Generated order ID")
    total_price: float = Field(0.0, description="Total order price")
    confirmation_attempts: int = Field(0, description="Number of confirmation attempts")
    
    def is_complete(self) -> bool:
        """Check if all required fields are filled"""
        return all([
            self.drink_type,
            self.size,
            self.milk,
            self.name,
            self.delivery_address,
            self.payment_method
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
        if not self.delivery_address:
            missing.append("delivery address")
        if not self.payment_method:
            missing.append("payment method")
        return missing
    
    def get_order_summary(self) -> str:
        """Generate a readable order summary"""
        summary = f"""
ORDER SUMMARY:
- Drink: {self.drink_type} ({self.size})
- Milk: {self.milk}
- Extras: {', '.join(self.extras) if self.extras else 'None'}
- Customer: {self.name}
- Delivery Address: {self.delivery_address}
- Payment: {self.payment_method}
- Total Price: ${self.total_price:.2f}
"""
        if self.order_id:
            summary = f"Order ID: {self.order_id}\n" + summary
        return summary.strip()


@dataclass
class BaristaUserdata:
    """User data for barista agent session"""
    current_order: CoffeeOrder = field(default_factory=lambda: CoffeeOrder(
        drink_type=None, size=None, milk=None, name=None, 
        name_confirmed=False, delivery_address=None, address_confirmed=False,
        payment_method=None, order_id=None, total_price=0.0, confirmation_attempts=0
    ))
    orders_saved: int = 0
    conversation_history: list[str] = field(default_factory=list)


# Enhanced Coffee Shop Menu with Pricing
COFFEE_MENU = {
    "drinks": {
        "Espresso": {"small": 3.50, "medium": 4.50, "large": 5.50},
        "Americano": {"small": 3.00, "medium": 4.00, "large": 5.00},
        "Latte": {"small": 4.50, "medium": 5.50, "large": 6.50},
        "Cappuccino": {"small": 4.50, "medium": 5.50, "large": 6.50},
        "Mocha": {"small": 5.00, "medium": 6.00, "large": 7.00},
        "Macchiato": {"small": 4.00, "medium": 5.00, "large": 6.00},
        "Flat White": {"small": 4.50, "medium": 5.50, "large": 6.50},
        "Cortado": {"small": 3.50, "medium": 4.50, "large": 5.50},
        "Cold Brew": {"small": 4.00, "medium": 5.00, "large": 6.00},
        "Iced Coffee": {"small": 3.50, "medium": 4.50, "large": 5.50}
    },
    "sizes": ["Small", "Medium", "Large"],
    "milk_options": ["Whole Milk", "Skim Milk", "Oat Milk", "Almond Milk", "Soy Milk", "Coconut Milk"],
    "extras": {
        "Extra Shot": 0.75,
        "Whipped Cream": 0.50,
        "Caramel Drizzle": 0.50,
        "Chocolate Syrup": 0.50,
        "Vanilla Syrup": 0.50,
        "Hazelnut Syrup": 0.50,
        "Cinnamon": 0.25,
        "Honey": 0.25
    },
    "payment_methods": ["Cash on Delivery", "Card", "UPI", "Google Pay", "PhonePe", "Paytm"]
}


def calculate_price(order: CoffeeOrder) -> float:
    """Calculate total price for an order"""
    total = 0.0
    
    # Base drink price
    if order.drink_type and order.size:
        drink = order.drink_type.title()
        size = order.size.lower()
        if drink in COFFEE_MENU["drinks"] and size in COFFEE_MENU["drinks"][drink]:
            total += COFFEE_MENU["drinks"][drink][size]
    
    # Add extras
    for extra in order.extras:
        extra_normalized = extra.title()
        if extra_normalized in COFFEE_MENU["extras"]:
            total += COFFEE_MENU["extras"][extra_normalized]
    
    return round(total, 2)


def generate_order_id() -> str:
    """Generate unique order ID in format: MCC-YYYYMMDD-XXX"""
    now = datetime.now()
    date_str = now.strftime("%Y%m%d")
    time_str = now.strftime("%H%M%S")[-3:]  # Last 3 digits of time
    return f"MCC-{date_str}-{time_str}"


async def send_order_webhook(order: CoffeeOrder, webhook_type: str = "discord"):
    """Send order notification to Discord or Telegram via webhook"""
    try:
        if webhook_type == "discord":
            webhook_url = os.getenv("DISCORD_WEBHOOK_URL")
            if not webhook_url:
                logger.warning("DISCORD_WEBHOOK_URL not configured")
                return
            
            # Create Discord embed
            embed = {
                "title": f"🆕 New Coffee Order - {order.order_id}",
                "color": 0x8B4513,  # Brown color
                "fields": [
                    {"name": "☕ Drink", "value": f"{order.drink_type} ({order.size})", "inline": True},
                    {"name": "🥛 Milk", "value": order.milk, "inline": True},
                    {"name": "➕ Extras", "value": ', '.join(order.extras) if order.extras else "None", "inline": True},
                    {"name": "👤 Customer", "value": order.name, "inline": True},
                    {"name": "📍 Address", "value": order.delivery_address, "inline": False},
                    {"name": "💳 Payment", "value": order.payment_method, "inline": True},
                    {"name": "💰 Total", "value": f"${order.total_price:.2f}", "inline": True},
                ],
                "footer": {"text": "Murf's Coffee House - Powered by Murf Falcon AI"},
                "timestamp": datetime.now().isoformat()
            }
            
            payload = {
                "content": "🔔 **NEW ORDER RECEIVED!** Owner, please check and confirm.",
                "embeds": [embed]
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(webhook_url, json=payload) as resp:
                    if resp.status == 204:
                        logger.info(f"Order {order.order_id} sent to Discord successfully")
                    else:
                        logger.error(f"Discord webhook failed: {resp.status}")
        
        elif webhook_type == "telegram":
            bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
            chat_id = os.getenv("TELEGRAM_CHAT_ID")
            
            if not bot_token or not chat_id:
                logger.warning("TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID not configured")
                return
            
            # Create Telegram message
            message = f"""
🔔 **NEW ORDER RECEIVED**

📦 Order ID: `{order.order_id}`
☕ Drink: {order.drink_type} ({order.size})
🥛 Milk: {order.milk}
➕ Extras: {', '.join(order.extras) if order.extras else 'None'}

👤 Customer: {order.name}
📍 Address: {order.delivery_address}
💳 Payment: {order.payment_method}
💰 Total: ${order.total_price:.2f}

⏰ Time: {datetime.now().strftime('%I:%M %p')}

👨‍💼 Owner, please confirm and prepare this order!
"""
            
            url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
            payload = {
                "chat_id": chat_id,
                "text": message,
                "parse_mode": "Markdown"
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload) as resp:
                    if resp.status == 200:
                        logger.info(f"Order {order.order_id} sent to Telegram successfully")
                    else:
                        logger.error(f"Telegram webhook failed: {resp.status}")
                        
    except Exception as e:
        logger.error(f"Webhook error: {e}")


class CoffeeBaristaAgent(Agent):
    def __init__(self) -> None:
        menu_text = self._format_menu()
        
        super().__init__(
            instructions=f"""You are Emma, an enthusiastic and professional barista at Murf's Coffee House! 🎉{menu_text}

YOUR PERSONALITY:
- Warm, friendly, conversational, and genuinely excited about coffee
- Professional but approachable - like chatting with a friend
- Patient and helpful with customer questions
- ALWAYS stay responsive and engaged - never go silent
- Celebrate each order completion with enthusiasm!

YOUR ORDERING PROCESS (Follow this EXACT sequence):
1. **Greet** warmly and ask what they'd like
2. **Drink Type** - Ask what coffee they want (if not specified)
3. **Size** - Ask size preference (if not specified)
4. **Milk** - Ask milk preference (if not specified)
5. **Extras** - Suggest popular additions (whipped cream, shots, syrups)
6. **Customer Name** - Ask for their name ONCE, then IMMEDIATELY spell it back: "Let me confirm - that's spelled [spell name letter by letter]. Is that correct?"
7. **Delivery Address** - Ask where to deliver, then REPEAT back exactly: "Just to confirm, [full address]. Is that right?"
8. **Payment Method** - Ask how they'd like to pay (Cash, Card, UPI, etc.)
9. **Calculate Price** - Use calculate_price tool to get total
10. **CONFIRMATION** - Show COMPLETE order summary with price and ask "Does everything look correct? Say YES to confirm!"
11. **Wait for YES** - Only save order when customer explicitly confirms
12. **Save & Notify** - Call save_order to finalize and notify owner

CRITICAL RULES:
- Ask ONE question at a time - don't overwhelm
- ALWAYS call calculate_price BEFORE asking for confirmation
- MUST get explicit "yes" or "confirm" before calling save_order
- Show full order summary including price before confirmation
- Keep responses SHORT (1-2 sentences maximum)
- No markdown, asterisks, or emojis in speech
- For address, ask for full details: "What's your delivery address? Please include area or landmark"

NAME & ADDRESS HANDLING:
- When customer gives name, IMMEDIATELY spell it back letter-by-letter for confirmation
- If name sounds like spelling (single letters), join them together
- For addresses, REPEAT the full address back and ask "Is that correct?"
- Common errors: "Cats" or "Cast" means "Cash" (on delivery)
- "Jungson" usually means "Junction"
- Always stay engaged - if there's a pause, prompt gently: "I'm still here! Ready when you are."

ERROR RECOVERY:
- If system is slow, acknowledge: "Just a moment, processing..."
- If rate limited, say: "One second please..." and wait
- Never go completely silent - always acknowledge you're listening
- If customer repeats themselves, acknowledge: "Yes, I heard that!"

EXAMPLE COMPLETE FLOW:
Customer: "I want a coffee"
You: "Great! What type of coffee - latte, cappuccino, americano, or something else?"
Customer: "Latte please"
You: "Perfect! What size - small, medium, or large?"
Customer: "Medium"
You: "Excellent! What milk would you like? We have whole, oat, almond, soy, skim, and coconut."
Customer: "Oat milk"
You: "Love it! Want to add anything extra? Maybe whipped cream, an extra shot, or flavored syrup?"
Customer: "Extra shot please"
You: "Great choice! What name should I put on the order?"
Customer: "Sarah"
You: "Perfect! Where should we deliver this, Sarah? Please include your area or a landmark."
Customer: "123 Main Street, near Central Park"
You: "Got it! How would you like to pay? We accept cash on delivery, card, UPI, Google Pay, PhonePe, and Paytm."
Customer: "UPI"
You: [Call calculate_price tool, then say] "Awesome! Let me confirm your order. One medium oat milk latte with an extra shot for Sarah, delivering to 123 Main Street near Central Park. Payment by UPI. Your total is $6.25. Does everything look correct? Say YES to confirm!"
Customer: "Yes"
You: [Call save_order] "Perfect! Your order is confirmed! Your order ID is MCC-20251124-123. The owner will join you soon to prepare your coffee. Thank you!"

Remember: ALWAYS wait for explicit confirmation before saving! 🚀
""",
        )

    def _format_menu(self) -> str:
        """Format the coffee menu for the agent's instructions"""
        drinks = ', '.join(COFFEE_MENU['drinks'].keys())
        return f"""
OUR MENU:
☕ Drinks: {drinks}
📏 Sizes: Small, Medium, Large
🥛 Milk: Whole, Skim, Oat, Almond, Soy, Coconut
➕ Extras: Extra Shot ($0.75), Whipped Cream ($0.50), Syrups ($0.50), Cinnamon ($0.25), Honey ($0.25)
💳 Payment: Cash on Delivery, Card, UPI, Google Pay, PhonePe, Paytm
"""

    @function_tool()
    async def update_drink_type(
        self,
        context: RunContext[BaristaUserdata],
        drink_type: Annotated[str, Field(description="The type of coffee drink")],
    ) -> str:
        """Updates the drink type in the customer's order"""
        userdata = context.userdata
        drink_normalized = drink_type.title()
        
        if drink_normalized not in COFFEE_MENU['drinks']:
            available = ', '.join(COFFEE_MENU['drinks'].keys())
            return f"Sorry, we don't have {drink_type}. Choose from: {available}"
        
        userdata.current_order.drink_type = drink_normalized
        logger.info(f"Updated drink: {drink_normalized}")
        return f"Got it, {drink_normalized}!"

    @function_tool()
    async def update_size(
        self,
        context: RunContext[BaristaUserdata],
        size: Annotated[str, Field(description="Size: small, medium, or large")],
    ) -> str:
        """Updates the size in the customer's order"""
        userdata = context.userdata
        size_normalized = size.lower().strip()
        
        if size_normalized not in ['small', 'medium', 'large']:
            return "Please choose small, medium, or large"
        
        userdata.current_order.size = size_normalized
        logger.info(f"Updated size: {size_normalized}")
        return f"Perfect, {size_normalized}!"

    @function_tool()
    async def update_milk(
        self,
        context: RunContext[BaristaUserdata],
        milk: Annotated[str, Field(description="Type of milk")],
    ) -> str:
        """Updates the milk preference in the customer's order"""
        userdata = context.userdata
        milk_normalized = milk.lower().strip()
        
        # Handle variations
        milk_map = {
            'oat': 'oat milk', 'almond': 'almond milk', 'soy': 'soy milk',
            'skim': 'skim milk', 'whole': 'whole milk', 'coconut': 'coconut milk'
        }
        
        for key, value in milk_map.items():
            if key in milk_normalized:
                milk_normalized = value
                break
        
        userdata.current_order.milk = milk_normalized
        logger.info(f"Updated milk: {milk_normalized}")
        return f"Great, {milk_normalized}!"

    @function_tool()
    async def add_extras(
        self,
        context: RunContext[BaristaUserdata],
        extras: Annotated[list[str], Field(description="List of extra additions")],
    ) -> str:
        """Adds extras to the customer's order"""
        userdata = context.userdata
        normalized = [e.lower().strip() for e in extras]
        userdata.current_order.extras = normalized
        
        logger.info(f"Added extras: {normalized}")
        
        if not extras:
            return "No extras, got it!"
        return f"Adding {', '.join(normalized)}!"

    @function_tool()
    async def update_name(
        self,
        context: RunContext[BaristaUserdata],
        name: Annotated[str, Field(description="Customer's name - may be spelled out letter by letter")],
    ) -> str:
        """Updates the customer name for the order. Handles spelled-out names."""
        userdata = context.userdata
        
        # Clean up spelled names (e.g., "D a y a n a n d" -> "Dayanand")
        cleaned_name = clean_spelled_name(name)
        userdata.current_order.name = cleaned_name.strip().title()
        
        logger.info(f"Customer name: {userdata.current_order.name} (from input: {name})")
        
        # If name was spelled out, spell it back for confirmation
        if cleaned_name != name:
            spelled_out = ' '.join(list(userdata.current_order.name))
            return f"Got it! Let me confirm - that's {spelled_out}. Correct?"
        
        return f"Perfect! So that's {userdata.current_order.name}, right?"

    @function_tool()
    async def update_address(
        self,
        context: RunContext[BaristaUserdata],
        address: Annotated[str, Field(description="Full delivery address with area/landmark")],
    ) -> str:
        """Updates the delivery address for the order. Applies phonetic corrections."""
        userdata = context.userdata
        
        # Apply phonetic corrections (e.g., "Patna Jungson" -> "Patna Junction")
        corrected_address = apply_phonetic_corrections(address)
        userdata.current_order.delivery_address = corrected_address.strip().title()
        
        logger.info(f"Delivery address: {userdata.current_order.delivery_address} (from input: {address})")
        
        # Always repeat back for confirmation
        return f"Perfect! Just to confirm - {userdata.current_order.delivery_address}. Is that correct?"

    @function_tool()
    async def update_payment(
        self,
        context: RunContext[BaristaUserdata],
        payment_method: Annotated[str, Field(description="Payment method")],
    ) -> str:
        """Updates the payment method for the order. Handles phonetic errors like 'cats/cast' -> 'cash'."""
        userdata = context.userdata
        
        # Apply phonetic corrections for payment methods
        corrected_payment = apply_phonetic_corrections(payment_method)
        payment_normalized = corrected_payment.title()
        
        # Map to standard payment methods
        payment_map = {
            "Cash On Delivery": "Cash On Delivery",
            "Cod": "Cash On Delivery",
            "Card": "Card",
            "Upi": "UPI",
            "Google Pay": "Google Pay",
            "Phonepe": "PhonePe",
            "Paytm": "Paytm"
        }
        
        final_payment = payment_map.get(payment_normalized, payment_normalized)
        userdata.current_order.payment_method = final_payment
        
        logger.info(f"Payment method: {final_payment} (from input: {payment_method})")
        return f"Perfect, {final_payment}!"

    @function_tool()
    async def calculate_price(
        self,
        context: RunContext[BaristaUserdata],
    ) -> str:
        """Calculates the total price for the current order"""
        userdata = context.userdata
        order = userdata.current_order
        
        total = 0.0
        
        # Base price
        if order.drink_type and order.size:
            drink = order.drink_type
            size = order.size
            if drink in COFFEE_MENU['drinks'] and size in COFFEE_MENU['drinks'][drink]:
                total += COFFEE_MENU['drinks'][drink][size]
        
        # Extras
        for extra in order.extras:
            extra_title = extra.title()
            if extra_title in COFFEE_MENU['extras']:
                total += COFFEE_MENU['extras'][extra_title]
        
        order.total_price = round(total, 2)
        logger.info(f"Calculated price: ${order.total_price}")
        
        return f"Your total is ${order.total_price:.2f}"

    @function_tool()
    async def check_order_status(
        self,
        context: RunContext[BaristaUserdata],
    ) -> str:
        """Checks what information is still needed"""
        userdata = context.userdata
        order = userdata.current_order
        
        status = f"""
Current order:
- Drink: {order.drink_type or 'NOT SET'}
- Size: {order.size or 'NOT SET'}
- Milk: {order.milk or 'NOT SET'}
- Extras: {', '.join(order.extras) if order.extras else 'none'}
- Name: {order.name or 'NOT SET'}
- Address: {order.delivery_address or 'NOT SET'}
- Payment: {order.payment_method or 'NOT SET'}
- Price: ${order.total_price:.2f}
"""
        
        missing = order.get_missing_fields()
        if missing:
            status += f"\nStill need: {', '.join(missing)}"
        else:
            status += "\n✅ Ready to confirm!"
        
        return status

    @function_tool()
    async def save_order(
        self,
        context: RunContext[BaristaUserdata],
    ) -> str:
        """Saves the order and notifies the owner. ONLY call after customer confirms with YES!"""
        userdata = context.userdata
        order = userdata.current_order
        
        # Validate completeness
        if not order.is_complete():
            missing = order.get_missing_fields()
            return f"Cannot save! Missing: {', '.join(missing)}"
        
        # Generate order ID
        order.order_id = generate_order_id()
        
        # Create orders directory
        orders_dir = Path("orders")
        orders_dir.mkdir(exist_ok=True)
        
        # Save to JSON
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_name = (order.name or "Unknown").replace(' ', '_')
        filename = orders_dir / f"order_{timestamp}_{safe_name}.json"
        
        order_data = {
            "order_id": order.order_id,
            "timestamp": datetime.now().isoformat(),
            "order_number": userdata.orders_saved + 1,
            "customer": {
                "name": order.name,
                "delivery_address": order.delivery_address,
                "payment_method": order.payment_method
            },
            "order_details": {
                "drink_type": order.drink_type,
                "size": order.size,
                "milk": order.milk,
                "extras": order.extras,
                "total_price": order.total_price
            },
            "status": "pending",
            "notes": "Awaiting owner confirmation"
        }
        
        try:
            # Save JSON file
            with open(filename, 'w') as f:
                json.dump(order_data, f, indent=2)
            
            logger.info(f"✅ Order saved: {filename}")
            logger.info(f"Order data: {json.dumps(order_data, indent=2)}")
            
            # Send webhooks (Discord and Telegram)
            await send_order_webhook(order, "discord")
            await send_order_webhook(order, "telegram")
            
            userdata.orders_saved += 1
            
            # Reset for next order
            userdata.current_order = CoffeeOrder(
                drink_type=None, size=None, milk=None, name=None,
                name_confirmed=False, delivery_address=None, address_confirmed=False,
                payment_method=None, order_id=None, total_price=0.0, confirmation_attempts=0
            )
            
            return f"Order confirmed! Your order ID is {order.order_id}. The owner will join you soon to prepare and deliver your coffee. Thank you, {order.name}!"
            
        except Exception as e:
            logger.error(f"Error saving order: {e}")
            return f"Sorry, error saving order: {str(e)}"


def prewarm(proc: JobProcess):
    """Prewarm the VAD model for faster startup"""
    proc.userdata["vad"] = silero.VAD.load()


async def entrypoint(ctx: JobContext):
    """Main entry point for the coffee shop barista agent"""
    
    # Logging setup
    ctx.log_context_fields = {
        "room": ctx.room.name,
        "agent": "coffee-shop-barista",
    }

    # Initialize userdata with conversation history
    userdata = BaristaUserdata()

    # Set up voice AI pipeline
    session = AgentSession[BaristaUserdata](
        userdata=userdata,
        # Speech-to-text with coffee-specific keywords and phonetic awareness
        stt=deepgram.STT(
            model="nova-3",
            # Expanded keywords for better recognition including common errors
            keyterms=[
                # Coffee drinks
                "latte", "cappuccino", "espresso", "americano", "mocha", "macchiato",
                "flat white", "cortado", "cold brew", "iced coffee",
                
                # Milk options
                "oat milk", "almond milk", "soy milk", "coconut milk", "whole milk", "skim milk",
                
                # Sizes
                "small", "medium", "large",
                
                # Extras
                "extra shot", "whipped cream", "syrup", "honey", "cinnamon",
                
                # Payment (including phonetic variations)
                "cash on delivery", "cash", "card", "UPI", "Google Pay", "PhonePe", "Paytm",
                
                # Location-specific (India)
                "Patna", "Junction", "Bihar", "India",
                
                # Common words
                "yes", "no", "correct", "proceed", "confirm"
            ],
            # Enable smart formatting for better accuracy
            smart_format=True,
            # Punctuation for better sentence detection
            punctuate=True,
            # Profanity filtering disabled to allow "cash" without issues
            profanity_filter=False
        ),
        # LLM with better retry logic and rate limit handling
        llm=google.LLM(
            model="gemini-2.5-flash",
            temperature=0.6,  # Slightly lower for more consistent responses
        ),
        # TTS with conversational style
        tts=murf.TTS(
            voice="en-US-matthew",
            style="Conversation",
            tokenizer=tokenize.basic.SentenceTokenizer(min_sentence_len=2),
            text_pacing=True
        ),
        # Turn detection disabled on Windows - MultilingualModel requires inference executor
        # which fails with Windows multiprocessing spawn mode. VAD will still work.
        vad=ctx.proc.userdata["vad"],
        preemptive_generation=True,
        max_tool_steps=20,  # Allow more steps for complete ordering process
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
        logger.info(f"Total orders completed: {userdata.orders_saved}")

    ctx.add_shutdown_callback(log_usage)

    # Start the session with our barista agent
    await session.start(
        agent=CoffeeBaristaAgent(),
        room=ctx.room,
        room_input_options=RoomInputOptions(
            # BVC commented for local dev (Day 1 fix preserved)
            # noise_cancellation=noise_cancellation.BVC(),
        ),
    )

    # Join the room
    await ctx.connect()
    
    # Keep the agent running - wait indefinitely
    await ctx.wait_for_participant()


if __name__ == "__main__":
    # Critical fix for Windows multiprocessing spawn mode
    multiprocessing.freeze_support()
    
    # Set spawn as the explicit start method (Windows default)
    try:
        multiprocessing.set_start_method('spawn', force=True)
    except RuntimeError:
        pass  # Already set
    
    cli.run_app(WorkerOptions(
        entrypoint_fnc=entrypoint,
        prewarm_fnc=prewarm,
        agent_name=os.getenv("LIVEKIT_AGENT_NAME", "coffee-barista")
    ))
