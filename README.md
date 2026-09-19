# ✈️ AI Flight Tracker

An intelligent, conversational flight tracking application powered by **LangChain**, **Ollama**, and **Streamlit**. It integrates real-time ADS-B and aviation APIs to provide live tracking, aircraft metadata, and airline insights through natural language.

---

## 🌟 Features

- **Natural Language Flight Inquiries**: Ask questions in plain English (e.g., *"What is the status of flight IGO1045?"* or *"Show me active flights operated by Air India"*).
- **Multi-Source Aviation Data**:
  - **ADSBdb Integration**: Look up flight callsigns, aircraft registration details, Mode S transponder codes, and airline ICAO/IATA records.
  - **OpenSky Network Integration**: Access live global aircraft state vectors and filter airborne flights by airline callsign prefix.
- **Local LLM Powered**: Uses **Ollama** (`qwen2.5:3b`) with tool-calling capabilities for low-latency, private, and offline-capable reasoning.
- **Interactive Web UI**: Clean, responsive interface built with **Streamlit** featuring real-time token streaming.

---

## 🏗️ Architecture

```
                      +-------------------+
                      |   Streamlit UI    |
                      |     (app.py)      |
                      +---------+---------+
                                |
                                v
                      +-------------------+
                      |  LangChain Agent  |  <--- ChatOllama (qwen2.5:3b)
                      | (agent_tools.py)  |
                      +----+---------+----+
                           |         |
              +------------+         +------------+
              v                                   v
    +-------------------+               +-------------------+
    |    ADSBdb API     |               |  OpenSky Network  |
    | (Callsign, Regis- |               | (Live States &    |
    | tration, Airline) |               |  Active Flights)  |
    +-------------------+               +-------------------+
```

---

## 🛠️ Available Agent Tools

| Tool | Source | Description |
|---|---|---|
| `callsign_tracker` | ADSBdb | Fetches flight status, route, and aircraft details for a specific callsign. |
| `get_aircraft_type` | ADSBdb | Queries aircraft specifications by registration number or Mode S code. |
| `get_aircraft_all_details` | ADSBdb | Performs a combined query for both aircraft registration and callsign. |
| `get_airline` | ADSBdb | Retrieves airline details based on ICAO or IATA short code. |
| `get_active_flights_by_airline` | OpenSky | Fetches live airborne flights matching an airline's ICAO prefix. |
| `get_access_token` | OpenSky | Authenticates OAuth2 client credentials for higher OpenSky rate limits (optional). |

---

## 🚀 Getting Started

### Prerequisites

- **Python 3.10+**
- **[Ollama](https://ollama.com/)** installed and running on your system.

### 1. Clone the Repository

```bash
git clone https://github.com/iamkavin1674/ai-flight-tracker.git
cd ai-flight-tracker
```

### 2. Set Up Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install streamlit langchain langchain-ollama langchain-openrouter requests python-dotenv
```

### 4. Pull the LLM Model

Make sure Ollama is running, then pull the model configured in `agent_tools.py`:

```bash
ollama pull qwen2.5:3b
```

### 5. Configure Environment Variables (Optional)

Create a `.env` file in the root directory if you plan to use OpenRouter or authenticated OpenSky credentials:

```env
# Optional: OpenRouter API key if switching LLM provider
OPENROUTER_API_KEY=your_openrouter_api_key_here
```

---

## 🖥️ Running the Application

Launch the Streamlit web app:

```bash
streamlit run app.py
```

Open your browser at `http://localhost:8501` to start tracking flights!

---

## 💡 Example Queries

- *"What is the status of flight IGO1045?"*
- *"Look up aircraft information for registration VT-IFN."*
- *"Show me active airborne flights for airline code AIC."*
- *"Can you give me information about airline DLH?"*

---

## 📁 Project Structure

```
ai-flight-tracker/
├── agent_tools.py   # LangChain tools, LLM configuration, and agent setup
├── app.py           # Streamlit web application with streaming support
├── debug.py         # Testing script for isolated tool verification
├── .gitignore       # Git ignore patterns for Python & environments
└── README.md        # Project documentation
```

---

⚠️ Usage Notice

This application relies on third-party, open-source aviation APIs such as ADSBdb and OpenSky Network. Availability, response times, rate limits, and data completeness may vary, so the app may not always work reliably.

Frequent or repeated requests can also generate significant network traffic and may be subject to API/provider rate limits. Please use the application responsibly and respect the terms and usage limits of the underlying services.

---

## 📄 License

This project is open source and available under the [MIT License](LICENSE).
