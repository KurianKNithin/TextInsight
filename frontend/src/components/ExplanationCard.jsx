import React from 'react';
import { Sparkles } from 'lucide-react';

export default function ExplanationCard({ explanation }) {
  return (
    <div className="card col-span-12">
      <div className="card-title">
        <span className="card-title-left">
          <Sparkles size={16} color="#ec4899" />
          AI Analysis Reasoning & Explanation
        </span>
      </div>

      <p className="explanation-text">
        {explanation}
      </p>
    </div>
  );
}
