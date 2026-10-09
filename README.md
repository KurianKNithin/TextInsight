<<<<<<< HEAD
# TextInsight 🔍✨

TextInsight is a full-stack text analytics web application that extracts 5 key intelligence layers from any text in a single AI pass:
1. **Executive Summary** (concise 2–3 sentences)
2. **Sentiment Analysis** (`positive`, `negative`, or `neutral` with confidence score 0.0–1.0)
3. **Keyword & Key Phrase Extraction** (top 10 keywords/phrases)
4. **Text Classification** (categorized into `News`, `Business`, `Technology`, `Entertainment`, `Sports`, `Personal`, or `Other`)
5. **AI Reasoning Explanation** (a paragraph explaining how the sentiment and category were determined)

Powered by **Anthropic Claude API**, **Python + FastAPI**, and **React + Vite**.

---

## Project Structure

```
TextInsight/
├── backend/
│   ├── main.py              # FastAPI app with CORS & /analyze endpoint
│   ├── models.py            # Pydantic models for request, response & validation
│   ├── analyzer.py          # Claude API integration, structured prompting & retries
│   ├── config.py            # Environment configuration & settings
│   ├── requirements.txt     # Python dependencies
│   ├── .env.example         # Example environment variables
│   └── .env                 # Local environment variables with your API key
├── frontend/
│   ├── src/
│   │   ├── components/      # SummaryCard, SentimentCard, ClassificationCard, KeywordsCard, etc.
│   │   ├── App.jsx          # Main UI layout, forms, and results presentation
│   │   ├── index.css        # Clean, modern responsive design
│   │   └── main.jsx         # React DOM root
│   ├── index.html           # Single-page application entry HTML
│   ├── vite.config.js       # Vite configuration with API proxy
│   └── package.json         # Frontend dependencies & scripts
└── README.md                # Documentation & setup instructions
```

---

## Prerequisites

- **Python**: 3.10+ (tested with Python 3.13)
- **Node.js**: 18+ and **npm** (tested with Node v18.18)
- **Anthropic API Key**: Available from [Anthropic Console](https://console.anthropic.com/)

---

## 1. Backend Setup & Run

### Step 1: Open a terminal in `TextInsight/backend`
```bash
cd backend
```

### Step 2: Install Python dependencies
```bash
pip install -r requirements.txt
```

### Step 3: Configure Environment Variables
Copy `.env.example` to `.env` (or edit the existing `.env` file):
```env
# Anthropic API Key
ANTHROPIC_API_KEY=sk-ant-api03-your-actual-anthropic-key-here

# Optional: Claude model name (defaults to claude-3-5-sonnet-20241022)
ANTHROPIC_MODEL=claude-3-5-sonnet-20241022

# MOCK_MODE: "auto" | "false" | "true"
# "auto" will automatically simulate intelligent responses if ANTHROPIC_API_KEY is not set.
# Set to "false" to require live Anthropic Claude API calls.
MOCK_MODE=auto
```

### Step 4: Run the FastAPI server
```bash
python -m uvicorn backend.main:app --reload --port 8000
```
- **API Base URL**: `http://127.0.0.1:8000`
- **Interactive Swagger Docs**: `http://127.0.0.1:8000/docs`
- **Health Check**: `http://127.0.0.1:8000/health`

---

## 2. Frontend Setup & Run

### Step 1: Open another terminal in `TextInsight/frontend`
```bash
cd frontend
```

### Step 2: Install npm dependencies
```bash
npm install
```

### Step 3: Start the Vite development server
```bash
npm run dev
```

### Step 4: Open in your browser
Navigate to:
```
http://localhost:5173
```

---

## 3. Testing the Endpoint via cURL or PowerShell

### cURL
```bash
curl -X POST http://127.0.0.1:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{"text": "Anthropic has released Claude 3.5 Sonnet, demonstrating incredible coding capabilities and reduced latency."}'
```

### PowerShell
```powershell
$body = @{ text = "Anthropic has released Claude 3.5 Sonnet with industry-leading reasoning performance." } | ConvertTo-Json
Invoke-RestMethod -Uri http://127.0.0.1:8000/analyze -Method POST -ContentType "application/json" -Body $body | ConvertTo-Json
```

### Sample Response Format
```json
{
  "summary": "Anthropic has introduced Claude 3.5 Sonnet, featuring industry-leading performance in coding and reasoning benchmarks. The model brings significant improvements to developer workflows and enterprise AI applications.",
  "sentiment": {
    "label": "positive",
    "confidence": 0.94
  },
  "keywords": [
    "Anthropic",
    "Claude 3.5 Sonnet",
    "coding",
    "benchmarks",
    "reasoning",
    "performance",
    "enterprise",
    "developer",
    "latency",
    "models"
  ],
  "classification": "Technology",
  "explanation": "The text discusses advanced artificial intelligence model releases and benchmark performance, which clearly falls under the Technology classification. The sentiment is positive (0.94 confidence) due to words emphasizing industry-leading performance and breakthrough capabilities."
}
```

---

## Key Technical Features

- **Single Structured Prompt**: Extracts all 5 features in one round-trip to minimize latency and token consumption.
- **Pydantic Validation & Retries**: Strict schema validation on the LLM output. If parsing fails, the backend automatically sends a feedback retry to the LLM before falling back to a clean HTTP 500 error.
- **Auto Fallback / Mock Mode**: Allows instant local testing out of the box even before entering an API key.
- **Modern Responsive UI**: Built with React, featuring quick sample prompts, confidence score visualization, keyword chips, and copy shortcuts.
=======
# TextInsight
A Full-stack text analysis application ("TextInsight") featuring summarization, sentiment analysis, keyword extraction, category classification, and AI-generated reasoning powered by the Anthropic Claude API.
>>>>>>> 01de6a8e0c25b250031892c3338007c1b0ac2a4b
