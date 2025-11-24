## Ten Days of Voice Agents — Day 2

Developer-focused README for the local project. This repo contains a LiveKit-based voice agent (backend) and a Next.js frontend for a voice-driven coffee-ordering demo.
Please note: secrets that were previously committed have been replaced with placeholders in working files. If any real API keys were exposed earlier you must rotate them in the provider consoles (Deepgram, Google/Gemini, Murf, LiveKit, Discord).

Getting started (local development)
1) Copy example env files and populate your keys:
       - `cd backend` then `Copy-Item .env.example .env.local` and edit `.env.local` with your keys.
       - `cd ../frontend` then `Copy-Item .env.example .env.local` and edit `.env.local`.

2) Backend (from repo root):
       - `cd backend`
       - `uv sync`
       - `uv run python src/agent.py dev`

3) Frontend (new terminal):
       - `cd frontend`
       - `npm install`
       - `npm run dev`
       - Open `http://localhost:3000`
Notes
- Do NOT commit `.env.local` (already in `.gitignore`).
- If you see any build artifact directories tracked (e.g. `.venv`, `node_modules`, `.next`), they will be removed from the repo as part of the cleanup.
- For production, use a proper secrets manager and rotate keys if they were exposed.

Repository layout (important parts)
- `backend/` — Python LiveKit agent and server orchestration
- `frontend/` — Next.js app with voice UI
- `orders/` — saved order JSONs

If you want me to proceed, I will:
1. Remove tracked build artifacts and virtualenvs (`.venv`, `node_modules`, `.next`, `livekit-server*`) and the `backend/tests` folder.
2. Commit the cleanup and push to `https://github.com/dayanandXdarpan/ten-days-of-voice-agents-2025-day2` on `main`.

If you prefer a different remote/branch or want tests preserved, tell me before I push.

— Maintainer
# ☕ Murf's Coffee House - AI Voice Ordering System

🎯 **Day 2 Challenge - PRODUCTION READY** ✅ | Complete Coffee Shop Solution with Real-Time Notifications

## 🚀 What Makes This Special?

This isn't just a challenge completion - it's a **fully production-ready coffee shop ordering system** you can deploy today!

### Beyond the Challenge Requirements

✅ **Challenge Requirements (Day 2)**:
- Coffee order state management (drink, size, milk, extras, name)
- Clarifying questions one at a time
- Save orders to JSON

🚀 **Production Enhancements Added**:
- 📍 **Delivery address collection** with landmarks
- 💳 **Payment method selection** (Cash, UPI, Card, etc.)
- 💰 **Real-time price calculation** with menu pricing
- 🔔 **Discord webhook integration** for instant owner notifications
- 📱 **Telegram bot integration** for mobile order alerts
- 🆔 **Unique order ID generation** (MCC-YYYYMMDD-XXX)
- ✅ **Explicit order confirmation** - waits for customer approval
- 📊 **Complete order summaries** before finalization
- 🏪 **Ready for multi-location** deployment

## ⚡ Quick Start (5 Minutes!)

### New to This Project?
**Start here**: [QUICK_START.md](./QUICK_START.md) - Get running in 5 minutes!

### Want Full Details?
**Read this**: [PRODUCTION_README.md](./PRODUCTION_README.md) - Complete documentation

### Setting Up Notifications?
**Follow this**: [WEBHOOK_SETUP_GUIDE.md](./WEBHOOK_SETUP_GUIDE.md) - Discord & Telegram setup

## 📊 Progress Tracker

- ✅ **Day 1**: Basic Voice Agent - **COMPLETED**
- ✅ **Day 2**: Coffee Shop Barista Agent - **PRODUCTION READY** ✨
- ⏳ **Day 3-10**: Coming soon...

## 🎯 What You Get

### Customer Experience
1. **Natural voice ordering** - Talk to Emma, your friendly AI barista
2. **Menu browsing** - 10 drinks, 3 sizes, 6 milk options, 8 extras
3. **Price transparency** - See total before confirming
4. **Order confirmation** - Review everything before finalizing
5. **Order tracking** - Get unique order ID instantly

### Shop Owner Experience
1. **Instant notifications** - Discord and Telegram alerts when orders arrive
2. **Complete order details** - Drink, size, milk, extras, customer info, address
3. **Payment information** - Know how customer wants to pay
4. **Order IDs** - Track and manage orders easily
5. **JSON storage** - Easy integration with any system

## 🏗️ Tech Stack

- **Voice Framework**: LiveKit Agents (real-time audio)
- **Speech-to-Text**: Deepgram Nova-3 (optimized for coffee terms)
- **LLM**: Google Gemini 2.5 Flash (friendly barista personality)
- **Text-to-Speech**: Murf Falcon ⚡ (fastest TTS, 50-150ms)
- **Backend**: Python 3.11+ with async webhooks
- **Frontend**: Next.js 15 with voice UI
- **Notifications**: Discord & Telegram webhooks

## 📁 Key Files

```
ten-days-of-voice-agents-2025-day2/
├── backend/src/
│   └── agent.py              ← 🌟 MAIN AGENT (600+ lines, 10 tools!)
├── orders/                    ← Order JSON files saved here
├── QUICK_START.md             ← Start here!
├── PRODUCTION_README.md       ← Full documentation
├── WEBHOOK_SETUP_GUIDE.md     ← Notification setup
└── README.md                  ← This file
```

## 🎤 Example Ordering Flow

```
Emma: "Hi! Welcome to Murf's Coffee House! What can I get for you?"
Customer: "I'd like a latte"
Emma: "Perfect! What size?"
Customer: "Medium"
Emma: "Great! What milk?"
Customer: "Oat milk"
Emma: "Want any extras?"
Customer: "Extra shot"
Emma: "What name?"
Customer: "Alex"
Emma: "Where should we deliver?"
Customer: "123 Main Street"
Emma: "Payment method?"
Customer: "UPI"
Emma: "Your total is $6.25. One medium oat milk latte with extra shot 
       for Alex at 123 Main Street, paying by UPI. Say YES to confirm!"
Customer: "Yes"
Emma: "Order confirmed! Your order ID is MCC-20251124-456. 
       The owner will join you soon!"
```

**At the same time:**
- 🎮 Discord notification sent to #orders channel
- 📱 Telegram message sent to shop owner's group
- 💾 JSON file saved to `orders/` directory

## 🔔 Notification Example

### Discord Message
```
🔔 NEW ORDER RECEIVED! Owner, please check and confirm.

🆕 New Coffee Order - MCC-20251124-456
☕ Drink: Latte (Medium)
🥛 Milk: Oat Milk
➕ Extras: Extra Shot
👤 Customer: Alex
📍 Address: 123 Main Street, near Central Park
💳 Payment: UPI
💰 Total: $6.25

⏰ 3:30 PM
```

### Telegram Message
```
🔔 **NEW ORDER RECEIVED**

📦 Order ID: `MCC-20251124-456`
☕ Drink: Latte (Medium)
🥛 Milk: Oat Milk
➕ Extras: Extra Shot
👤 Customer: Alex
📍 Address: 123 Main Street, near Central Park
💳 Payment: UPI
💰 Total: $6.25

👨‍💼 Owner, please confirm and prepare!
```

## 💡 Features Breakdown

### 10 Function Tools Implemented

1. **update_drink_type** - Set coffee type with menu validation
2. **update_size** - Small, medium, or large
3. **update_milk** - 6 milk options
4. **add_extras** - Shots, syrups, toppings
5. **update_name** - Customer name
6. **update_address** - Full delivery address
7. **update_payment** - Payment method
8. **calculate_price** - Real-time total calculation
9. **check_order_status** - See what's missing
10. **save_order** - Finalize with webhooks

### Smart Order Management

- **Validation**: Won't save incomplete orders
- **Confirmation**: Requires explicit YES from customer
- **Price Preview**: Shows total before confirmation
- **Order Summary**: Complete review before finalizing
- **Unique IDs**: Every order gets tracked
- **Async Webhooks**: Non-blocking notifications

## 💰 Menu & Pricing

**10 Drinks** | Small: $3-$5 | Medium: $4-$6 | Large: $5-$7

**6 Milk Options** | No extra charge

**8 Extras** | $0.25-$0.75 each

**6 Payment Methods** | Cash, Card, UPI, Google Pay, PhonePe, Paytm

See [PRODUCTION_README.md](./PRODUCTION_README.md) for full menu.

## 🚀 Deployment Ready

This system is ready for:

✅ **Local coffee shops** - Single location ordering  
✅ **Food trucks** - Mobile ordering at events  
✅ **Pop-up shops** - Temporary installations  
✅ **Multi-location chains** - Easy to extend  
✅ **Cloud deployment** - Docker & cloud-ready  

### Next Steps for Production

1. **Database**: Replace JSON with PostgreSQL
2. **Admin Panel**: Build order management dashboard
3. **Real Payments**: Integrate Stripe/Razorpay
4. **SMS Updates**: Add Twilio for customer texts
5. **Analytics**: Track popular drinks, revenue, trends

## 🛠️ Installation

### Super Quick (5 min)
```powershell
# Backend
cd backend
Copy-Item .env.example .env.local
# Add your API keys to .env.local
uv sync
uv run python src/agent.py dev

# Frontend (new terminal)
cd frontend
npm install
npm run dev

# Visit http://localhost:3000
```

**Full instructions**: [QUICK_START.md](./QUICK_START.md)

## 📚 Documentation

| Document | What It Covers | When to Use |
|----------|---------------|-------------|
| **[QUICK_START.md](./QUICK_START.md)** | 5-minute setup | Getting started fast |
| **[PRODUCTION_README.md](./PRODUCTION_README.md)** | Everything! Architecture, features, deployment | Complete reference |
| **[WEBHOOK_SETUP_GUIDE.md](./WEBHOOK_SETUP_GUIDE.md)** | Discord & Telegram | Setting up notifications |

## 🏆 Challenge Completion

### Day 2 Requirements ✅

- [x] Coffee order state management (drinkType, size, milk, extras, name)
- [x] Ask clarifying questions one at a time
- [x] Save completed orders to JSON files
- [x] Natural conversational flow
- [x] Emma barista persona

### Production Enhancements 🚀

- [x] Delivery address collection
- [x] Payment method integration
- [x] Real-time price calculation
- [x] Discord webhook notifications
- [x] Telegram bot integration
- [x] Unique order ID generation
- [x] Order confirmation with approval
- [x] Complete order summaries
- [x] Comprehensive documentation
- [x] Production-ready architecture

## 🎉 What Makes This Different?

Most Day 2 submissions will have:
- Basic order state ✅
- Simple questions ✅
- JSON saving ✅

**This implementation also has**:
- Complete customer journey (address, payment) 🌟
- Real-time notifications (Discord + Telegram) 🔔
- Production-ready pricing system 💰
- Explicit order confirmation flow ✅
- Shop owner integration 🏪
- Comprehensive documentation 📚
- Ready to deploy today! 🚀

## 📱 Share Your Order!

Completed an order? Share on LinkedIn:

```
Just placed my first order at an AI-powered coffee shop! ☕

Built with:
🎤 LiveKit Agents
🧠 Gemini 2.5 Flash
🗣️ Deepgram Nova-3
⚡ Murf Falcon TTS

Features:
✅ Voice ordering
✅ Real-time notifications (Discord & Telegram!)
✅ Complete delivery & payment flow
✅ Production-ready architecture

This is Day 2 of #10DaysofAIVoiceAgents Challenge by @Murf AI
Building with the fastest TTS API - Murf Falcon! ⚡

GitHub: [your-repo-link]

#VoiceAI #MurfFalcon #LiveKit #ProductionReady
```

## 🐛 Issues?

**Common Solutions**:
- Can't connect? Check LiveKit server is running
- No voice? Check browser microphone permissions
- Webhooks not working? See [WEBHOOK_SETUP_GUIDE.md](./WEBHOOK_SETUP_GUIDE.md)
- Orders not saving? Check `orders/` directory exists

## 🤝 Contributing

This is an open implementation! Feel free to:
- Add more drink options
- Implement new payment methods
- Create a frontend order dashboard
- Add email notifications
- Build analytics dashboard

## 📄 License

MIT License - Use it for your coffee shop! ☕

## 🙏 Credits

- **Challenge**: Murf AI's 10 Days of Voice Agents
- **Framework**: LiveKit Agents
- **Voice Tech**: Deepgram, Google Gemini, Murf Falcon
- **Built by**: Building the future of voice commerce! 🚀

---

**⚡ Powered by Murf Falcon - The Fastest TTS API**

**Day 2 Completed**: November 24, 2025  
**Challenge**: #10DaysofAIVoiceAgents by Murf AI

**Let's revolutionize coffee ordering with voice AI!** ☕🎤🚀


## 🚀 Tech Stack

- **Voice Infrastructure**: [LiveKit Agents](https://docs.livekit.io/agents) - Real-time voice framework
- **Speech-to-Text**: [Deepgram Nova-3](https://deepgram.com/) - High-accuracy transcription (80-250ms)
- **Language Model**: [Google Gemini 2.5 Flash](https://ai.google.dev/) - Fast, intelligent responses (100-500ms)
- **Text-to-Speech**: [Murf Falcon](https://murf.ai/api) - Ultra-fast, natural voice (50-150ms) ⚡
- **Frontend**: Next.js 15.5.2 with TypeScript & React
- **Backend**: Python 3.11 with LiveKit Agents SDK

**Total Pipeline Latency**: 350-1250ms (STT + LLM + TTS)

## 📁 Repository Structure

```
murf_ai_ten-days-of-voice-agents-2025/
├── backend/              # LiveKit Agents backend with Murf Falcon TTS
│   ├── src/
│   │   ├── agent.py      # Main agent orchestration (BVC removed for local dev)
│   │   └── __init__.py
│   ├── pyproject.toml    # Python dependencies
│   ├── uv.lock           # Dependency lock file
│   ├── Dockerfile        # Production container
│   └── README.md         # Backend documentation
├── frontend/             # Next.js voice interaction UI
│   ├── app/              # Next.js app directory
│   ├── components/       # React components
│   ├── hooks/            # Custom React hooks
│   ├── package.json      # Node dependencies
│   └── README.md         # Frontend documentation
├── docs/                 # Comprehensive documentation
│   ├── START_HERE.md            # First-time setup guide
│   ├── SETUP_GUIDE.md           # Detailed configuration
│   ├── QUICK_START.md           # Rapid deployment
│   ├── TESTING_INSTRUCTIONS.md  # Testing procedures
│   ├── PIPELINE_ANALYSIS.md     # Performance metrics & optimization
│   ├── DAY_1_README.md         # Day 1 completion notes
│   └── PROJECT_ORGANIZATION.md  # Repository structure
├── challenges/           # Daily challenge descriptions
│   └── Day 1 Task.md
├── start_app.sh          # Convenience script (all services)
├── .gitignore            # Comprehensive git exclusions
└── README.md             # This file
```

## ⚡ Quick Start

### Prerequisites

- **Python 3.9+** with [uv](https://docs.astral.sh/uv/) package manager
- **Node.js 18+** with pnpm (or npm)
- **LiveKit Server** for local development
- **API Keys**: Deepgram, Murf, Google Gemini

### 1. Clone Repository

```bash
git clone https://github.com/dayanandXdarpan/murf_ai_ten-days-of-voice-agents-2025.git
cd murf_ai_ten-days-of-voice-agents-2025
```

### 2. Backend Setup

```bash
cd backend

# Install uv if not already installed
# curl -LsSf https://astral.sh/uv/install.sh | sh  # macOS/Linux
# pip install uv  # Windows

# Install dependencies
uv sync

# Create environment file
cp .env.example .env.local

# Edit .env.local and add your API keys:
# DEEPGRAM_API_KEY=your_deepgram_key
# MURF_API_KEY=your_murf_api_key
# GOOGLE_API_KEY=your_google_gemini_key

# Download required models (optional)
uv run python src/agent.py download-files
```

### 3. Frontend Setup

```bash
cd ../frontend

# Install dependencies
pnpm install
# or: npm install

# Create environment file
cp .env.example .env.local

# Edit .env.local:
# LIVEKIT_URL=ws://127.0.0.1:7880
```

### 4. Start Services

**Option A: All services at once (Unix/macOS)**
```bash
chmod +x start_app.sh
./start_app.sh
```

**Option B: Individual terminals (Windows/Unix)**

```bash
# Terminal 1: LiveKit Server
livekit-server --dev

# Terminal 2: Backend Agent
cd backend
uv run python src/agent.py dev

# Terminal 3: Frontend
cd frontend
pnpm dev
```

### 5. Test Your Agent

1. Open **http://localhost:3000** in your browser
2. Grant **microphone permissions** when prompted
3. Start speaking: *"Hello, can you hear me?"*
4. Watch the magic happen! ✨

## 📚 Complete Documentation

| Document | Description | Use Case |
|----------|-------------|----------|
| [START_HERE.md](docs/START_HERE.md) | Beginner-friendly setup guide | First-time users |
| [SETUP_GUIDE.md](docs/SETUP_GUIDE.md) | Comprehensive installation | Detailed configuration |
| [QUICK_START.md](docs/QUICK_START.md) | Rapid deployment | Get running fast |
| [TESTING_INSTRUCTIONS.md](docs/TESTING_INSTRUCTIONS.md) | Testing procedures | Validate your setup |
| [PIPELINE_ANALYSIS.md](docs/PIPELINE_ANALYSIS.md) | Performance metrics | Optimization insights |
| [DAY_1_README.md](docs/DAY_1_README.md) | Day 1 journey | Challenge completion |
| [PROJECT_ORGANIZATION.md](docs/PROJECT_ORGANIZATION.md) | Repo structure | Understanding layout |

## 🔧 Key Features & Modifications

### ✅ Day 1 Implementations

- **Complete voice agent setup** with LiveKit, Deepgram, Gemini, Murf
- **Real-time audio processing** with Silero VAD and turn detection
- **Production-ready configuration** with comprehensive .gitignore
- **Organized documentation** in dedicated docs/ folder
- **Local development optimizations**:
  - BVC (Background Voice Cancellation) disabled (lines 127-132 in `agent.py`)
  - BVC requires LiveKit Cloud; removed for local compatibility
  - All other pipeline features intact

### 🎨 Frontend Features

- Real-time voice interaction with LiveKit
- Audio visualization and level monitoring
- Light/dark theme switching
- Mobile-responsive design
- Chat transcript view

### 🧠 Backend Features

- Multi-modal agent framework (voice + optional video)
- Configurable LLM providers (Gemini, OpenAI, Anthropic)
- Multiple STT options (Deepgram, Groq)
- Murf Falcon TTS integration (fastest in class!)
- Comprehensive metrics and logging
- Production Docker support

## 📈 Performance Metrics

Based on local testing with Day 1 setup:

| Component | Latency | Notes |
|-----------|---------|-------|
| **Speech-to-Text** | 80-250ms | Deepgram Nova-3 |
| **LLM Processing** | 100-500ms | Gemini 2.5 Flash |
| **Text-to-Speech** | 50-150ms | Murf Falcon ⚡ |
| **Audio Pipeline** | ~50ms | VAD + processing |
| **Total Latency** | 350-1250ms | End-to-end response |

**Key Insight**: Murf Falcon delivers consistently fast TTS, making it ideal for real-time voice interactions!

See [PIPELINE_ANALYSIS.md](docs/PIPELINE_ANALYSIS.md) for detailed breakdown.

## 🛠️ Troubleshooting

### Backend won't connect to LiveKit
```bash
# Ensure LiveKit server is running
livekit-server --dev

# Check it's on the correct port
netstat -an | grep 7880  # Unix/macOS
netstat -an | findstr 7880  # Windows
```

### Agent not listening to microphone
1. Check browser microphone permissions
2. Verify Deepgram API key in `backend/.env.local`
3. Check backend logs for "STT transcript:" messages

### Python import errors
```bash
cd backend
# Clear cache
rm -rf __pycache__ src/__pycache__  # Unix/macOS
# Windows PowerShell:
# Get-ChildItem -Recurse -Directory -Filter "__pycache__" | Remove-Item -Recurse -Force

# Reinstall dependencies
uv sync --refresh
```

### Frontend hydration warnings
If you see warnings about `cz-shortcut-listen="true"`:
- These are **cosmetic only** from browser extensions (e.g., ColorZilla)
- They don't affect functionality
- Safe to ignore

## 🔗 Resources & Documentation

### Official Docs
- [Murf Falcon TTS API](https://murf.ai/api/docs/text-to-speech/streaming)
- [LiveKit Agents Documentation](https://docs.livekit.io/agents)
- [Deepgram API Docs](https://developers.deepgram.com/)
- [Google Gemini API](https://ai.google.dev/gemini-api/docs)

### Original Templates
- [LiveKit Python Agent Starter](https://github.com/livekit-examples/agent-starter-python)
- [LiveKit React Frontend Starter](https://github.com/livekit-examples/agent-starter-react)
- [Challenge Repository](https://github.com/murf-ai/ten-days-of-voice-agents-2025)

### Community
- [LiveKit Community Slack](https://livekit.io/join-slack)
- [Murf Discord](https://murf.ai/discord)

## 🧪 Testing

Run the comprehensive test suite:

```bash
cd backend
uv run pytest
```

Learn more: [LiveKit Agent Testing Documentation](https://docs.livekit.io/agents/build/testing/)

## 📄 License

This project builds upon MIT-licensed templates:
- Backend: [Apache 2.0](backend/LICENSE)
- Frontend: [Apache 2.0](frontend/LICENSE)

See individual LICENSE files for details.

## 🙏 Acknowledgments

- **Murf AI** for organizing this amazing challenge and building Falcon TTS
- **LiveKit** for the powerful voice agent framework
- **Deepgram** for high-quality speech recognition
- **Google** for Gemini 2.5 Flash LLM
- Original repository: [murf-ai/ten-days-of-voice-agents-2025](https://github.com/murf-ai/ten-days-of-voice-agents-2025)

## 🎯 What's Next?

Stay tuned for **Day 2-10 challenges**! Each day will add new capabilities:
- Custom personas and conversation styles
- External API integrations
- Domain-specific agents (customer service, tutoring, etc.)
- Performance optimizations
- Multi-modal interactions

## 📱 Share Your Progress

Completed Day 1? Share your achievement:

```
✅ Completed Day 1 of #10DaysofAIVoiceAgents Challenge!

Built a real-time voice agent using:
🎙️ LiveKit Agents
🧠 Google Gemini 2.5 Flash
🗣️ Deepgram Nova-3
⚡ Murf Falcon TTS (50-150ms latency!)

GitHub: https://github.com/dayanandXdarpan/murf_ai_ten-days-of-voice-agents-2025

@Murf AI #MurfAIVoiceAgentsChallenge
```

---

**Author**: [@dayanandXdarpan](https://github.com/dayanandXdarpan)  
**Challenge**: #10DaysofAIVoiceAgents by Murf AI  
**Day 1 Completed**: November 23, 2025  
**Repository**: https://github.com/dayanandXdarpan/murf_ai_ten-days-of-voice-agents-2025

Let's build amazing voice AI agents together! 🚀
