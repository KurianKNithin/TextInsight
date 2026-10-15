import React from 'react';
import { Loader2 } from 'lucide-react';

export default function LoadingSpinner({ size = 18, text = "Analyzing..." }) {
  return (
    <span style={{ display: 'inline-flex', alignItems: 'center', gap: '0.5rem' }}>
      <Loader2 size={size} className="spinner" />
      {text && <span>{text}</span>}
    </span>
  );
}
