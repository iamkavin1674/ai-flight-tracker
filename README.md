# ✈️ AI Flight Tracker

An AI-powered flight tracking chatbot built with **Streamlit**, **LangChain**, and **OpenRouter**. Ask natural-language questions about live flights, aircraft, airlines, and prices — and the agent figures out which tools to call and streams back an answer in real time.

---

## 🚀 Features

- 🔍 **Callsign Tracking** — Look up live flight data by callsign (e.g. `UAL123`)
- 🛩️ **Aircraft Lookup** — Query aircraft details by registration number or Mode S transponder code
- 🏢 **Airline Info** — Retrieve airline details by ICAO or IATA code
- 🌐 **Live State Vectors** — Fetch all currently airborne aircraft via the OpenSky Network API
- 📊 **Active Flights by Airline** — Filter live flights by airline ICAO prefix (e.g. all `AAL` flights)
- 💰 **Flight Prices** — Search one-way or round-trip fares via Google Flights (SerpAPI)
- 🎫 **Booking Options** — Retrieve booking links and options for a selected flight
- 🗓️ **Relative Date Understanding** — Say "tomorrow" or "next Friday" and the agent resolves the exact date automatically
- ⚡ **Streaming Responses** — Responses stream token-by-token directly in the chat UI

---

## 🏗️ Architecture

```
app.py               ← Streamlit UI — chat interface & streaming
agent_tools.py       ← LangChain agent + all tool definitions
flight_price.py      ← SerpAPI-based flight price & booking tools
.streamlit/
  config.toml        ← Dark purple UI theme
.devcontainer/
  devcontainer.json  ← GitHub Codespaces / VS Code dev container config
```

**APIs used:**
| API | Purpose | Auth Required |
|-----|---------|---------------|
| [adsbdb.com](https://www.adsbdb.com/) | Callsign & aircraft lookup | None |
| [OpenSky Network](https://opensky-network.org/) | Live state vectors | Optional (OAuth2 for higher rate limits) |
| [SerpAPI](https://serpapi.com/) | Google Flights prices & booking | API Key |
| [OpenRouter](https://openrouter.ai/) | LLM inference | API Key |

---

## 🛠️ Setup

### Prerequisites

- Python 3.11+
- An [OpenRouter](https://openrouter.ai/) API key
- A [SerpAPI](https://serpapi.com/) API key

### 1. Clone the repository

```bash
git clone https://github.com/your-username/ai-flight-tracker.git
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

The app will be available at **http://localhost:8501**.

---

## ☁️ GitHub Codespaces

This project is fully configured for **GitHub Codespaces** via the `.devcontainer` setup. Just click **"Open in Codespace"** and the environment will install all dependencies and launch the Streamlit app automatically on port `8501`.

---

## 💬 Example Queries

| Query | Tool(s) Used |
|-------|-------------|
| `Track flight UAL123` | `callsign_tracker` |
| `What aircraft is registration N12345?` | `get_aircraft_type` |
| `Tell me about airline DLH` | `get_airline` |
| `Show me all active Air India flights` | `get_active_flights_by_airline` |
| `What are the cheapest flights from JFK to LAX tomorrow?` | `flight_prices` |
| `I want to book that flight — show me options` | `booking_options` |

---

## 📦 Dependencies

| Package | Purpose |
|---------|---------|
| `streamlit` | Web UI framework |
| `langchain` | Agent & tool orchestration |
| `langchain-core` | Core LangChain primitives |
| `langchain-openrouter` | OpenRouter LLM integration |
| `langchain-ollama` | Local Ollama LLM support |
| `openrouter` | OpenRouter Python SDK |
| `python-dotenv` | `.env` file loading |
| `requests` | HTTP calls to flight APIs |

---

## 🎨 Theme

The app uses a custom dark purple theme defined in [`.streamlit/config.toml`](.streamlit/config.toml):

- **Background:** `#0d0d1a` (deep navy)
- **Secondary Background:** `#1a1a2e`
- **Primary Accent:** `#a855f7` (purple)
- **Text:** `#e0e0e0`

---

## 📄 License

This project is open-source. Feel free to use, fork, and contribute!
