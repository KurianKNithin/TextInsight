import React, { useState, useEffect } from 'react';
import { 
  FileText, 
  Copy, 
  Check, 
  Volume2, 
  Square, 
  Pause, 
  Play, 
  VolumeX 
} from 'lucide-react';
import useSpeech from '../hooks/useSpeech';

export default function SummaryCard({ summary }) {
  const [copied, setCopied] = useState(false);
  const {
    speak,
    stop,
    pause,
    resume,
    isSpeaking,
    isPaused,
    rate,
    setRate,
    isSupported,
  } = useSpeech();

  // Cancel any ongoing speech when summary changes or component unmounts
  useEffect(() => {
    stop();
  }, [summary, stop]);

  const handleCopy = () => {
    if (!summary) return;
    navigator.clipboard.writeText(summary);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleToggleListen = () => {
    if (isSpeaking) {
      stop();
    } else {
      speak(summary, rate);
    }
  };

  const handleTogglePause = () => {
    if (isPaused) {
      resume();
    } else {
      pause();
    }
  };

  const handleSpeedChange = (e) => {
    const newRate = parseFloat(e.target.value);
    setRate(newRate);
    if (isSpeaking && !isPaused) {
      // Re-speak with the new rate if currently playing
      speak(summary, newRate);
    }
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

        <div className="summary-actions">
          {/* Audio Controls */}
          <div className="audio-controls">
            {!isSupported ? (
              <button
                type="button"
                className="audio-btn disabled"
                disabled
                title="Text-to-speech is not supported in this browser."
              >
                <VolumeX size={14} />
                <span>Not Supported</span>
              </button>
            ) : (
              <>
                <button
                  type="button"
                  className={`audio-btn ${isSpeaking ? 'speaking' : ''}`}
                  onClick={handleToggleListen}
                  title={isSpeaking ? "Stop speaking" : "Listen to summary aloud"}
                >
                  {isSpeaking ? (
                    <>
                      <Square size={12} fill="currentColor" />
                      <span>Stop</span>
                    </>
                  ) : (
                    <>
                      <Volume2 size={14} />
                      <span>Listen</span>
                    </>
                  )}
                </button>

                {isSpeaking && (
                  <button
                    type="button"
                    className="audio-btn secondary"
                    onClick={handleTogglePause}
                    title={isPaused ? "Resume speech" : "Pause speech"}
                  >
                    {isPaused ? <Play size={12} fill="currentColor" /> : <Pause size={12} fill="currentColor" />}
                    <span>{isPaused ? "Resume" : "Pause"}</span>
                  </button>
                )}

                <select
                  className="speed-select"
                  value={rate}
                  onChange={handleSpeedChange}
                  title="Speech playback rate"
                  aria-label="Speech playback rate"
                >
                  <option value={0.75}>0.75x</option>
                  <option value={1}>1x</option>
                  <option value={1.25}>1.25x</option>
                  <option value={1.5}>1.5x</option>
                </select>
              </>
            )}
          </div>

          {/* Copy Button */}
          <button className="copy-btn" onClick={handleCopy} title="Copy summary">
            {copied ? <Check size={14} color="#34d399" /> : <Copy size={14} />}
            <span>{copied ? 'Copied' : 'Copy'}</span>
          </button>
        </div>
      </div>

      <div className="summary-box">
        {summary}
      </div>
    </div>
  );
}
