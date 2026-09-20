<![CDATA[# ✈️ AI Flight Tracker

An AI-powered flight tracking chatbot built with **Streamlit**, **LangChain**, and **OpenRouter**. Ask natural-language questions about live flights, aircraft, airlines, and prices — the agent autonomously selects the right tools and streams back an answer in real time.

![Python](https://img.shields.io/badge/Python-3.11+-3776AB?logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-Chat_UI-FF4B4B?logo=streamlit&logoColor=white)
![LangChain](https://img.shields.io/badge/LangChain-Agent-1C3C3C?logo=langchain&logoColor=white)
![License](https://img.shields.io/badge/License-Open_Source-green)

---

## 🚀 Features

| Feature | Description |
|---------|-------------|
| 🔍 **Callsign Tracking** | Look up live flight data by callsign (e.g. `UAL123`) |
| 🛩️ **Aircraft Lookup** | Query aircraft details by registration number or Mode S transponder code |
| 🏢 **Airline Info** | Retrieve airline details by ICAO or IATA code |
| 🌐 **Live State Vectors** | Fetch all currently airborne aircraft via the OpenSky Network API |
| 📊 **Flights by Airline** | Filter live flights by airline ICAO prefix (e.g. all `AAL` flights) |
| 💰 **Flight Prices** | Search one-way or round-trip fares via Google Flights (SerpAPI) |
| 🎫 **Booking Options** | Retrieve booking links and options for a selected flight |
| 🗓️ **Relative Dates** | Say "tomorrow" or "next Friday" — the agent resolves the exact date automatically |
| ⚡ **Streaming Responses** | Token-by-token streaming directly in the chat UI |

---

## 🏗️ Architecture

### High-Level System Architecture

```mermaid
flowchart TD
    subgraph User["👤 User"]
        Browser["Web Browser"]
    end

    subgraph App["Streamlit Application"]
        UI["app.py\nChat Interface"]
        Agent["LangChain Agent\n(agent_tools.py)"]
        PriceTools["Flight Price Tools\n(flight_price.py)"]
    end

    subgraph LLM["LLM Provider"]
        OpenRouter["OpenRouter API\n(GPT / Free models)"]
    end

    subgraph ExternalAPIs["External APIs"]
        ADSB["adsbdb.com\nCallsign & Aircraft Data"]
        OpenSky["OpenSky Network\nLive State Vectors"]
        SerpAPI["SerpAPI\nGoogle Flights Pricing"]
    end

    Browser -->|"Chat message"| UI
    UI -->|"Invokes"| Agent
    Agent -->|"LLM Inference\n(streaming)"| OpenRouter
    OpenRouter -->|"Tool calls / Response"| Agent
    Agent -->|"callsign_tracker\nget_aircraft_type\nget_aircraft_all_details\nget_airline"| ADSB
    Agent -->|"fetch_all_states\nget_active_flights_by_airline"| OpenSky
    Agent -->|"flight_prices\nbooking_options"| SerpAPI
    Agent --- PriceTools
    Agent -->|"Streamed tokens"| UI
    UI -->|"Real-time response"| Browser

    style User fill:#1a1a2e,stroke:#a855f7,color:#e0e0e0
    style App fill:#0d0d1a,stroke:#a855f7,color:#e0e0e0
    style LLM fill:#1a1a2e,stroke:#a855f7,color:#e0e0e0
    style ExternalAPIs fill:#1a1a2e,stroke:#a855f7,color:#e0e0e0
```

### Agent Tool Routing Flow

```mermaid
flowchart LR
    UserQuery["🗣️ User Query"] --> Agent["🤖 LangChain Agent"]

    Agent -->|"Callsign mentioned"| T1["callsign_tracker"]
    Agent -->|"Registration / Mode S"| T2["get_aircraft_type"]
    Agent -->|"Both reg + callsign"| T3["get_aircraft_all_details"]
    Agent -->|"Airline ICAO/IATA"| T4["get_airline"]
    Agent -->|"All live aircraft"| T5["fetch_all_states"]
    Agent -->|"Airline active flights"| T6["get_active_flights_by_airline"]
    Agent -->|"Price search"| T7["flight_prices"]
    Agent -->|"Booking request"| T8["booking_options"]
    Agent -->|"OAuth2 token"| T9["get_access_token"]

    T1 --> API1["adsbdb.com"]
    T2 --> API1
    T3 --> API1
    T4 --> API1
    T5 --> API2["OpenSky Network"]
    T6 --> API2
    T7 --> API3["SerpAPI"]
    T8 --> API3
    T9 --> API2

    API1 --> Response["📝 Streamed Response"]
    API2 --> Response
    API3 --> Response

    style UserQuery fill:#a855f7,stroke:#fff,color:#fff
    style Agent fill:#1a1a2e,stroke:#a855f7,color:#e0e0e0
    style Response fill:#a855f7,stroke:#fff,color:#fff
```

### Data Flow Sequence

```mermaid
sequenceDiagram
    participant U as 👤 User
    participant S as Streamlit UI
    participant A as LangChain Agent
    participant LLM as OpenRouter LLM
    participant API as External API

    U->>S: Types question in chat
    S->>A: Passes message to agent.stream()
    A->>LLM: Sends user message + tool definitions
    LLM->>A: Returns tool call decision
    A->>API: Executes selected tool (HTTP GET)
    API-->>A: Returns JSON data
    A->>LLM: Sends tool result for synthesis
    LLM-->>A: Streams natural language response
    A-->>S: Yields AIMessageChunk tokens
    S-->>U: Renders streaming response in chat
```

---

## 📂 Project Structure

```
ai-flight-tracker/
├── app.py                  # Streamlit chat UI & streaming logic
├── agent_tools.py          # LangChain agent, LLM config & tool definitions
├── flight_price.py         # SerpAPI-based flight price & booking tools
├── requirements.txt        # Python dependencies
├── .env                    # API keys (not committed)
├── .gitignore              # Git ignore rules
├── .streamlit/
│   └── config.toml         # Custom dark purple theme
└── .devcontainer/
    └── devcontainer.json   # GitHub Codespaces / VS Code configuration
```

---

## 🔌 APIs Used

| API | Purpose | Auth Required | Used By |
|-----|---------|---------------|---------|
| [adsbdb.com](https://www.adsbdb.com/) | Callsign, aircraft & airline lookup | None | `agent_tools.py` |
| [OpenSky Network](https://opensky-network.org/) | Live aircraft state vectors | Optional (OAuth2 for higher rate limits) | `agent_tools.py` |
| [SerpAPI](https://serpapi.com/) | Google Flights prices & booking | API Key (`SERPAPI_KEY`) | `flight_price.py` |
| [OpenRouter](https://openrouter.ai/) | LLM inference (GPT, Claude, etc.) | API Key (`OPENROUTER_API_KEY`) | `agent_tools.py` |

---

## 🛠️ Setup

### Prerequisites

- **Python 3.11+**
- An [OpenRouter](https://openrouter.ai/) API key (free tier available)
- A [SerpAPI](https://serpapi.com/) API key (for flight pricing features)

### 1. Clone the repository

```bash
git clone https://github.com/iamkavin1674/ai-flight-tracker.git
cd ai-flight-tracker
```

### 2. Create a virtual environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file in the project root:

```env
OPENROUTER_API_KEY=your_openrouter_api_key_here
SERPAPI_KEY=your_serpapi_key_here
```

> [!NOTE]
> The `.env` file is listed in `.gitignore` and will never be committed to source control.

### 5. Run the app

```bash
streamlit run app.py
```

The app will be available at **http://localhost:8501** 🎉

---

## ☁️ GitHub Codespaces

This project is fully configured for **GitHub Codespaces** via the `.devcontainer` setup:

1. Click the green **"Code"** button on the repo → **"Open with Codespaces"**
2. Dependencies install automatically via `requirements.txt`
3. Streamlit launches on port `8501` with auto-preview

> [!TIP]
> Remember to add your `OPENROUTER_API_KEY` and `SERPAPI_KEY` as [Codespaces Secrets](https://docs.github.com/en/codespaces/managing-your-codespaces/managing-encrypted-secrets-for-your-codespaces) for a seamless experience.

---

## 💬 Example Queries

| Query | Tool(s) Invoked |
|-------|-----------------|
| `Track flight UAL123` | `callsign_tracker` |
| `What aircraft is registration N12345?` | `get_aircraft_type` |
| `Tell me about airline DLH` | `get_airline` |
| `Show me all active Air India flights` | `get_active_flights_by_airline` |
| `Cheapest flights from JFK to LAX tomorrow?` | `flight_prices` |
| `I want to book that flight` | `booking_options` |
| `Show all flights in the sky right now` | `fetch_all_states` |

---

## 📦 Dependencies

| Package | Purpose |
|---------|---------|
| `streamlit` | Web UI framework with chat components |
| `langchain` | Agent & tool orchestration framework |
| `langchain-core` | Core LangChain primitives (`AIMessageChunk`, etc.) |
| `langchain-openrouter` | OpenRouter LLM integration for LangChain |
| `langchain-ollama` | Local Ollama LLM support (alternative backend) |
| `openrouter` | OpenRouter Python SDK & error types |
| `python-dotenv` | `.env` file loading |
| `requests` | HTTP calls to flight APIs |

---

## 🎨 Theme

The app uses a custom dark purple theme defined in [`.streamlit/config.toml`](.streamlit/config.toml):

| Property | Value | Preview |
|----------|-------|---------|
| Background | `#0d0d1a` | 🟣 Deep navy |
| Secondary BG | `#1a1a2e` | 🔵 Dark indigo |
| Primary Accent | `#a855f7` | 💜 Purple |
| Text | `#e0e0e0` | ⚪ Light gray |
| Font | `sans serif` | — |

---

## 🤝 Contributing

Contributions are welcome! Here's how to get started:

1. **Fork** the repository
2. **Create** a feature branch: `git checkout -b feature/my-feature`
3. **Commit** your changes: `git commit -m 'Add my feature'`
4. **Push** to your branch: `git push origin feature/my-feature`
5. **Open** a Pull Request

---

## 📄 License

This project is open-source. Feel free to use, fork, and contribute!

---

<p align="center">
  Built with ❤️ using <b>LangChain</b>, <b>Streamlit</b>, and <b>OpenRouter</b>
</p>
]]>
