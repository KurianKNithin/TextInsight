import React from 'react';
import { 
  FolderCheck, 
  Cpu, 
  Briefcase, 
  Newspaper, 
  Tv, 
  Trophy, 
  User, 
  Compass,
  Gauge
} from 'lucide-react';

export default function ClassificationCard({ classification }) {
  // Support both object { category, confidence } and string "Technology"
  const category = typeof classification === 'object' && classification !== null 
    ? (classification.category || 'Other') 
    : (classification || 'Other');
    
  const confidence = typeof classification === 'object' && classification !== null && classification.confidence !== undefined
    ? classification.confidence
    : null;

  const percentage = confidence !== null ? Math.round(confidence * 100) : null;

  const getCategoryIcon = (cat) => {
    switch (cat) {
      case 'Technology':
        return <Cpu size={20} color="#38bdf8" />;
      case 'Business':
        return <Briefcase size={20} color="#38bdf8" />;
      case 'News':
        return <Newspaper size={20} color="#38bdf8" />;
      case 'Entertainment':
        return <Tv size={20} color="#38bdf8" />;
      case 'Sports':
        return <Trophy size={20} color="#38bdf8" />;
      case 'Personal':
        return <User size={20} color="#38bdf8" />;
      case 'Other':
      default:
        return <Compass size={20} color="#38bdf8" />;
    }
  };

  const getConfidenceLevel = (score) => {
    if (score >= 0.85) return { label: "High Confidence", color: "#38bdf8" };
    if (score >= 0.70) return { label: "Moderate Fit", color: "#818cf8" };
    return { label: "Hybrid / Nuanced", color: "#94a3b8" };
  };

  const confMeta = confidence !== null ? getConfidenceLevel(confidence) : null;

  return (
    <div className="card col-span-6">
      <div className="card-title">
        <span className="card-title-left">
          <FolderCheck size={16} color="#38bdf8" />
          Text Classification
        </span>
        {confMeta && (
          <span style={{ fontSize: '0.75rem', fontWeight: 600, color: confMeta.color }}>
            {confMeta.label}
          </span>
        )}
      </div>

      <div className="classification-box">
        <div className="category-badge">
          {getCategoryIcon(category)}
          <span>{category}</span>
        </div>

        {percentage !== null && (
          <div className="confidence-bar-wrapper">
            <div className="confidence-labels">
              <span>Domain Alignment Score</span>
              <span style={{ fontWeight: 600, color: 'var(--text-primary)' }}>{percentage}%</span>
            </div>
            <div className="confidence-bar-bg">
              <div
                className="confidence-bar-fill"
                style={{ 
                  width: `${percentage}%`,
                  background: 'linear-gradient(90deg, #0284c7, #38bdf8)' 
                }}
              />
            </div>
          </div>
        )}

        <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
          Assigned from 7 standard taxonomy domains based on terminology density and context.
        </p>
      </div>
    </div>
  );
}
