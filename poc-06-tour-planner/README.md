# POC 06: Intelligent Tour Planner - Your AI Travel Collaborator

This POC demonstrates an **intelligent, context-aware travel planning assistant** that maintains conversation memory and collaborates with you throughout the entire trip planning journey. Unlike simple query-response systems, this agent remembers your preferences, builds on previous discussions, and provides personalized, continuous assistance.

## 🌟 Key Features

### 🧠 **Intelligent Conversation Memory**
- **Remembers Everything**: Keeps track of all trip details discussed across the conversation
- **Context-Aware Responses**: References previous messages and builds upon earlier discussions
- **Continuous Planning**: Maintains state across multiple interactions for seamless collaboration
- **Proactive Assistance**: Suggests next steps and improvements based on conversation history

### 🤝 **Collaborative Experience**
- **Natural Conversation**: Chat naturally as if talking to a travel expert friend
- **Multi-Turn Planning**: Iteratively refine your trip based on feedback and new information
- **Flexible Adjustments**: Easily modify budget, dates, activities, or destinations mid-planning
- **Personalized Recommendations**: Tailored suggestions based on your stated interests and preferences

### 🏗️ **Multi-Agent Architecture**
Five specialized sub-agents work together seamlessly:
- **Destination Research Agent** - Searches for attractions, activities, and travel guides
- **Budget Calculator Agent** - Estimates costs with detailed breakdowns
- **Itinerary Builder Agent** - Creates day-by-day schedules based on your interests
- **Weather Agent** - Provides seasonal information and packing recommendations
- **Recommendations Agent** - Offers tips for food, safety, culture, and activities

### 🔧 **Session & State Management**
- **Persistent Trip State**: Saves destination, budget, traveler count, dates, and preferences
- **Cross-Message Context**: Maintains awareness throughout the planning session
- **Intelligent Retrieval**: Automatically recalls relevant details when needed

## 🚀 Setup

1. **Install dependencies** (from the root directory):
```bash
cd ..
pip install -r requirements.txt
```

2. **Set your Groq API key**:
```bash
export GROQ_API_KEY="your-groq-api-key"
```

## 🎯 Running the Agent

Navigate to this directory first:
```bash
cd poc-06-tour-planner
```

### Option 1: Terminal Interface (Recommended)
```bash
adk run .
```

### Option 2: Web Browser UI
```bash
adk web
```

### Option 3: API Server
```bash
adk api_server
```

## 💬 Example Conversation Flow

Here's how the intelligent conversation memory works:

```
You: I'm thinking about visiting Japan next spring

Agent: That's exciting! Japan in spring is beautiful with cherry blossoms.
       Let me help you plan this trip. A few questions:
       - How many days are you planning?
       - Will you be traveling solo or with others?
       - What's your approximate budget?
       - Any specific cities you want to visit?

You: 10 days, 2 people, around $5000

Agent: Perfect! I've saved those details. For a 10-day Japan trip for 2 people
       with a $5000 budget, you'll have a comfortable experience. Let me:
       1. Calculate a detailed budget breakdown
       2. Research top destinations and activities
       3. Check spring weather conditions

       [Agent uses budget calculator and research tools...]

       Based on my calculations, here's a breakdown:
       - Accommodation (mid-range): $1200
       - Food: $1000
       - Activities: $800
       - Transportation: $200
       Total: $3200, leaving $1800 for flights and extras

       What interests you most? Culture, food, nature, technology?

You: Definitely culture and food!

Agent: Excellent! I've noted your interests in culture and food. Given your
       10-day trip, I'd recommend splitting time between:
       - Tokyo (4 days) - Modern culture, diverse food scene
       - Kyoto (3 days) - Traditional temples, authentic cuisine
       - Osaka (2 days) - Food paradise, historic sites
       - Day trip to Nara (1 day)

       Would you like me to create a detailed day-by-day itinerary?

You: Yes please! And what should I pack?

Agent: I'll create that itinerary focused on culture and food experiences!

       [Agent creates itinerary and checks weather...]

       For spring in Japan (March-May):
       - Weather: Mild, 10-20°C, occasional rain
       - Pack: Light layers, comfortable walking shoes, light jacket, umbrella
       - Don't forget: Power adapter, JR Pass (great for your budget!)

       Here's your cultural & food-focused itinerary:

       Day 1-2 (Tokyo): Arrival, explore Asakusa temples, food tour in Tsukiji
       Day 3-4 (Tokyo): Museums, traditional tea ceremony, ramen tasting
       ...

       Want me to adjust anything or add specific activities?

You: Can we add more temple visits?

Agent: Absolutely! Since you want more temple visits and I know you're interested
       in culture, let me enhance your Kyoto portion (days 5-7) with additional
       temples:

       Updated Kyoto days:
       - Day 5: Fushimi Inari, Kiyomizu-dera, Gion district
       - Day 6: Kinkaku-ji, Ryoan-ji zen garden, Arashiyama bamboo grove
       - Day 7: Nijo Castle, temple meditation session, traditional kaiseki dinner

       This keeps you within your $5000 budget. Sound good?
```

**Notice how the agent:**
- ✅ Remembers all details (10 days, 2 people, $5000, spring, Japan)
- ✅ Builds on previous context (culture & food interests)
- ✅ Proactively suggests next steps
- ✅ Makes adjustments while maintaining budget awareness
- ✅ Provides personalized recommendations

## 🏛️ Architecture

```
Intelligent Tour Planner Coordinator (Context-Aware)
├── Destination Research Agent (web search, location info)
├── Budget Calculator Agent (cost estimation, currency conversion)
├── Itinerary Builder Agent (schedule creation, personalized to interests)
├── Weather Agent (seasonal data, packing recommendations)
└── Recommendations Agent (food, safety, culture, activities)
```

**State Management Tools:**
- `save_trip_state(key, value, trip_id)` - Saves trip details for later retrieval
- `get_trip_state(key, trip_id)` - Retrieves saved trip information
- Automatic session persistence via ADK runtime

## 📂 Code Structure

- **`agent.py`** - Multi-agent system with intelligent, context-aware instructions
  - Enhanced coordinator with session memory awareness
  - All sub-agents instructed to reference conversation context
  - Natural, collaborative conversation patterns

- **`tools.py`** - Custom tools for travel planning
  - Destination search (web search via DuckDuckGo)
  - Budget calculator with detailed breakdowns
  - Itinerary creation based on interests
  - Weather information lookup
  - Travel recommendations
  - **State management** (save/retrieve trip details)
  - Distance calculation

## 🎓 What's Demonstrated

### Technical Concepts:
- ✅ **Session Management**: ADK automatically maintains conversation context
- ✅ **State Persistence**: Custom tools for saving/retrieving trip planning state
- ✅ **Multi-Agent Orchestration**: Coordinator delegates to specialized agents
- ✅ **Context-Aware AI**: All agents reference previous messages and build on context
- ✅ **Tool Integration**: Multiple tools work together seamlessly
- ✅ **Groq Tool-Use Model**: `llama-3-groq-70b-8192-tool-use-preview` for function calling

### User Experience:
- ✅ **Continuous Conversation**: Not transactional, but collaborative over multiple turns
- ✅ **Intelligent Memory**: Agent remembers and references all trip details
- ✅ **Proactive Assistance**: Suggests improvements and next steps
- ✅ **Flexible Planning**: Easy to modify any aspect of the trip mid-conversation
- ✅ **Personalized Recommendations**: Tailored to stated interests and preferences

## 🧪 Example Queries

### Initial Planning:
- "I want to plan a trip to Europe next summer"
- "Help me plan a 5-day trip to Paris for 2 people with a budget of $3000"
- "I'm thinking about visiting Thailand, what should I know?"

### Refinement (Context-Aware):
- "Actually, let's make it 7 days instead" (agent remembers the destination)
- "Can we reduce the accommodation budget?" (agent recalls total budget)
- "Add more cultural activities" (agent adjusts itinerary accordingly)
- "What about weather in December instead?" (agent updates seasonal info)

### Information Gathering:
- "What's included in the budget?" (agent recalls previously calculated breakdown)
- "Remind me which cities we planned to visit?" (agent retrieves itinerary state)
- "What were your restaurant recommendations again?" (agent references previous messages)

## 🔍 Technical Details

### Session Management
The ADK runtime automatically maintains conversation context across messages. Each agent can access the full conversation history, enabling:
- Reference to previous user messages
- Awareness of earlier agent responses
- Continuous, coherent planning

### State Management Implementation
Custom tools provide explicit state storage/retrieval:

```python
# Save trip details
save_trip_state(key="destination", value="Japan", trip_id="current")
save_trip_state(key="budget", value="5000", trip_id="current")
save_trip_state(key="travelers", value="2", trip_id="current")

# Retrieve saved details
get_trip_state(key="destination", trip_id="current")
# Returns: {"trip_id": "current", "key": "destination", "value": "Japan", "found": True}

# Get all saved state
get_trip_state(trip_id="current")
# Returns: {"trip_id": "current", "state": {"destination": "Japan", "budget": "5000", ...}}
```

### Context-Aware Instructions
All agents are instructed to:
1. Reference conversation history before responding
2. Acknowledge previously mentioned details
3. Build upon earlier suggestions and feedback
4. Maintain awareness of the overall trip planning state
5. Provide continuous, coherent assistance

## 🛠️ Troubleshooting

**Issue**: Agent doesn't remember previous details
- **Solution**: ADK automatically maintains session. Ensure you're in the same session (don't restart `adk run .`)

**Issue**: State not persisting
- **Solution**: State is in-memory for this POC. For production, implement persistent storage (database, file system)

**Issue**: Poor search results
- **Solution**: Web search uses DuckDuckGo. Results quality varies. Consider using dedicated travel APIs for production

**Issue**: Tool calling errors
- **Solution**: Ensure using `groq/llama-3-groq-70b-8192-tool-use-preview` model (optimized for function calling)

## 🚀 Future Enhancements

- Persistent database storage for trip state
- Integration with real travel APIs (flights, hotels, weather)
- Multi-trip management (compare different destinations)
- Booking integration
- Collaborative planning (multiple users)
- Export itinerary to calendar/PDF

## 📚 Learn More

- [Google ADK Documentation](https://ai.google.dev/adk)
- [LiteLLM Documentation](https://docs.litellm.ai/)
- [Groq Function Calling Guide](https://console.groq.com/docs/tool-use)

---

**Built with:**
- Google ADK (Agent Development Kit)
- Groq LLM (`llama-3-groq-70b-8192-tool-use-preview`)
- LiteLLM (Multi-provider LLM integration)
- DuckDuckGo Search (Web search functionality)
