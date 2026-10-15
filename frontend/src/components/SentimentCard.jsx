import React from 'react';
import { Smile, Frown, Meh, Activity } from 'lucide-react';

export default function SentimentCard({ sentiment }) {
  const { label, confidence } = sentiment || { label: 'neutral', confidence: 0 };
  const percentage = Math.round(confidence * 100);

  const getSentimentIcon = () => {
    switch (label) {
      case 'positive':
        return <Smile size={18} />;
      case 'negative':
        return <Frown size={18} />;
      case 'neutral':
      default:
        return <Meh size={18} />;
    }
  };

  const getFillClass = () => {
    switch (label) {
      case 'positive':
        return 'fill-positive';
      case 'negative':
        return 'fill-negative';
      case 'neutral':
      default:
        return 'fill-neutral';
    }
  };

  const getConfidenceLevel = (score) => {
    if (score >= 0.85) return { label: "High Certainty", color: "#34d399" };
    if (score >= 0.70) return { label: "Moderate Certainty", color: "#fbbf24" };
    return { label: "Nuanced / Mixed", color: "#94a3b8" };
  };

  const confMeta = getConfidenceLevel(confidence);

  return (
    <div className="card col-span-6">
      <div className="card-title">
        <span className="card-title-left">
          <Activity size={16} color="#818cf8" />
          Sentiment Analysis
        </span>
        <span style={{ fontSize: '0.75rem', fontWeight: 600, color: confMeta.color }}>
          {confMeta.label}
        </span>
      </div>

      <div className="sentiment-display">
        <div className={`sentiment-badge ${label}`}>
          {getSentimentIcon()}
          <span>{label}</span>
        </div>

        <div className="confidence-bar-wrapper">
          <div className="confidence-labels">
            <span>Confidence Score</span>
            <span style={{ fontWeight: 600, color: 'var(--text-primary)' }}>{percentage}%</span>
          </div>
          <div className="confidence-bar-bg">
            <div
              className={`confidence-bar-fill ${getFillClass()}`}
              style={{ width: `${percentage}%` }}
            />
          </div>
        </div>
      </div>
    </div>
  );
}
