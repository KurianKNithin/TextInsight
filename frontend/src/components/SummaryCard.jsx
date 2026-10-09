import React, { useState } from 'react';
import { FileText, Copy, Check, Sparkles } from 'lucide-react';

export default function SummaryCard({ summary }) {
  const [copied, setCopied] = useState(false);

  const handleCopy = () => {
    if (!summary) return;
    navigator.clipboard.writeText(summary);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const sentenceCount = summary ? summary.split(/(?<=[.!?])\s+/).filter(Boolean).length : 0;

  return (
    <div className="card col-span-12">
      <div className="card-title">
        <span className="card-title-left">
          <FileText size={16} color="#6366f1" />
          Executive Summary
          <span style={{ 
            fontSize: '0.75rem', 
            fontWeight: 500, 
            color: '#a5b4fc', 
            background: 'rgba(99, 102, 241, 0.15)',
            padding: '0.15rem 0.5rem',
            borderRadius: '9999px',
            marginLeft: '0.35rem'
          }}>
            {sentenceCount} {sentenceCount === 1 ? 'sentence' : 'sentences'} &bull; high density
          </span>
        </span>
        <button className="copy-btn" onClick={handleCopy} title="Copy summary">
          {copied ? <Check size={14} color="#34d399" /> : <Copy size={14} />}
          <span>{copied ? 'Copied' : 'Copy'}</span>
        </button>
      </div>

      <div className="summary-box">
        {summary}
      </div>
    </div>
  );
}
