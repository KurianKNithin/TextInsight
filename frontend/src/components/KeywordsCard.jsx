import React, { useState } from 'react';
import { Tag, Check, Copy } from 'lucide-react';

export default function KeywordsCard({ keywords = [] }) {
  const [copied, setCopied] = useState(false);

  const handleCopy = () => {
    if (!keywords.length) return;
    navigator.clipboard.writeText(keywords.join(', '));
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="card col-span-12">
      <div className="card-title">
        <span className="card-title-left">
          <Tag size={16} color="#a855f7" />
          Extracted Keywords & Key Phrases ({keywords.length})
        </span>
        <button className="copy-btn" onClick={handleCopy} title="Copy keywords">
          {copied ? <Check size={14} color="#34d399" /> : <Copy size={14} />}
          <span>{copied ? 'Copied' : 'Copy'}</span>
        </button>
      </div>

      <div className="keyword-chips">
        {keywords.map((kw, idx) => (
          <span key={idx} className="keyword-chip">
            <span style={{ opacity: 0.6, fontSize: '0.75rem' }}>#{idx + 1}</span>
            {kw}
          </span>
        ))}
      </div>
    </div>
  );
}
