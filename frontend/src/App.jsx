import React, { useState } from 'react';
import { 
  Sparkles, 
  Send, 
  Trash2, 
  AlertTriangle, 
  CheckCircle2, 
  Layers,
  FileText
} from 'lucide-react';
import SummaryCard from './components/SummaryCard';
import SentimentCard from './components/SentimentCard';
import ClassificationCard from './components/ClassificationCard';
import KeywordsCard from './components/KeywordsCard';
import ExplanationCard from './components/ExplanationCard';
import LoadingSpinner from './components/LoadingSpinner';

const SAMPLES = [
  {
    title: "Tech Article",
    text: "Anthropic has introduced Claude 3.5 Sonnet, setting new industry benchmarks in reasoning, coding, and comprehension. The model demonstrates unprecedented speed and efficiency, enabling enterprises to build reliable agentic workflows at a fraction of the cost."
  },
  {
    title: "Customer Review",
    text: "I purchased this monitor two weeks ago and the display quality is simply breathtaking. The colors are vivid, the refresh rate makes gaming buttery smooth, and the customer support team resolved my setup inquiry within minutes. Absolutely worth every penny!"
  },
  {
    title: "Quarterly Earnings",
    text: "Global logistics corporation posted a 14% drop in quarterly net earnings amid rising fuel expenses and declining freight shipping volumes across trans-Pacific routes. Executives revised the fiscal outlook downward, cautioning that supply chain volatility could persist into next year."
  },
  {
    title: "Championship Match",
    text: "In a thrilling championship final that went down to the closing seconds, the underdog squad rallied from a twelve-point deficit in the fourth quarter to claim victory. The point guard delivered a stellar 38-point performance to capture the MVP title."
  }
];

export default function App() {
  const [inputText, setInputText] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [result, setResult] = useState(null);

  const characterCount = inputText.length;
  const wordCount = inputText.trim() ? inputText.trim().split(/\s+/).length : 0;

  const handleSampleClick = (text) => {
    setInputText(text);
    setError(null);
  };

  const handleClear = () => {
    setInputText('');
    setError(null);
    setResult(null);
  };

  const handleAnalyze = async (e) => {
    e.preventDefault();
    const trimmed = inputText.trim();

    if (!trimmed) {
      setError("Please enter or paste text to analyze.");
      return;
    }

    setLoading(true);
    setError(null);

    try {
      // First try relative path via Vite proxy (/api/analyze), fallback to direct port 8000
      let response;
      try {
        response = await fetch('/api/analyze', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ text: trimmed })
        });
      } catch (proxyErr) {
        // Direct call fallback
        response = await fetch('http://127.0.0.1:8000/analyze', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ text: trimmed })
        });
      }

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        const errorMessage = errorData.detail || `Server error (${response.status}): ${response.statusText}`;
        throw new Error(errorMessage);
      }

      const data = await response.json();
      setResult(data);
    } catch (err) {
      console.error("Analysis error:", err);
      setError(
        err.message || "Failed to analyze text. Please make sure the backend server is running on port 8000."
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container">
      {/* Header */}
      <header className="header">
        <div className="brand-badge">
          <Sparkles size={14} />
          <span>Powered by Claude & FastAPI</span>
        </div>
        <h1 className="brand-title">TextInsight</h1>
        <p className="brand-subtitle">
          Extract 5 core intelligence layers in seconds: Summarization, Sentiment, Keywords, Category Classification, and AI Reasoning.
        </p>
      </header>

      {/* Input Form */}
      <section className="input-card">
        <form onSubmit={handleAnalyze}>
          <div className="input-header">
            <label htmlFor="text-input" className="input-label">
              <FileText size={18} color="#818cf8" />
              Source Text
            </label>
            <div className="sample-prompts">
              <span className="sample-title">Try sample:</span>
              {SAMPLES.map((sample, idx) => (
                <button
                  type="button"
                  key={idx}
                  className="sample-btn"
                  onClick={() => handleSampleClick(sample.text)}
                >
                  {sample.title}
                </button>
              ))}
            </div>
          </div>

          <div className="textarea-wrapper">
            <textarea
              id="text-input"
              className="textarea-field"
              rows={6}
              placeholder="Paste any article, review, customer message, news report, or document here to extract full insights..."
              value={inputText}
              onChange={(e) => {
                setInputText(e.target.value);
                if (error) setError(null);
              }}
              disabled={loading}
            />
          </div>

          <div className="input-footer">
            <div className="meta-stats">
              {characterCount} chars &bull; {wordCount} words
            </div>

            <div style={{ display: 'flex', gap: '0.75rem' }}>
              {inputText && (
                <button
                  type="button"
                  className="sample-btn"
                  style={{ display: 'inline-flex', alignItems: 'center', gap: '0.3rem', padding: '0.6rem 0.9rem' }}
                  onClick={handleClear}
                  disabled={loading}
                >
                  <Trash2 size={14} />
                  Clear
                </button>
              )}

              <button
                type="submit"
                className="submit-btn"
                disabled={loading || !inputText.trim()}
              >
                {loading ? (
                  <LoadingSpinner text="Analyzing text..." />
                ) : (
                  <>
                    <Send size={16} />
                    <span>Analyze Text</span>
                  </>
                )}
              </button>
            </div>
          </div>
        </form>
      </section>

      {/* Error Alert */}
      {error && (
        <div className="error-banner">
          <AlertTriangle size={20} style={{ flexShrink: 0, marginTop: '2px' }} />
          <div>
            <strong>Analysis Failed: </strong>
            <span>{error}</span>
          </div>
        </div>
      )}

      {/* Results Section */}
      {result && (
        <section className="results-container">
          <div className="results-header">
            <h2 className="results-title">
              <CheckCircle2 size={22} color="#10b981" />
              Analysis Results
            </h2>
            <span style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>
              All 5 features generated via single structured prompt
            </span>
          </div>

          <div className="results-grid">
            {/* 1. Summary */}
            <SummaryCard summary={result.summary} />

            {/* 2. Sentiment */}
            <SentimentCard sentiment={result.sentiment} />

            {/* 3. Classification */}
            <ClassificationCard classification={result.classification} />

            {/* 4. Keywords */}
            <KeywordsCard keywords={result.keywords} />

            {/* 5. Explanation */}
            <ExplanationCard explanation={result.explanation} />
          </div>
        </section>
      )}
    </div>
  );
}
