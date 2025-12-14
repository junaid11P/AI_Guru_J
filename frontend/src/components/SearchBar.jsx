import React, { useEffect, useState, useRef } from "react";

export default function SearchBar({ onSubmit, loading, onStateChange }) {
  const [isListeningState, setIsListeningState] = useState(false); // For UI rendering
  const [isWakeWordActive, setIsWakeWordActive] = useState(true); // For UI rendering

  // Refs for stable access inside event listeners
  const isListeningRef = useRef(false);
  const loadingRef = useRef(loading);
  const onSubmitRef = useRef(onSubmit);
  const recognitionRef = useRef(null);
  const silenceTimer = useRef(null);

  // Sync props/state to refs
  useEffect(() => { loadingRef.current = loading; }, [loading]);
  useEffect(() => { onSubmitRef.current = onSubmit; }, [onSubmit]);
  useEffect(() => {
    if (onStateChange) onStateChange(isListeningState);
  }, [isListeningState, onStateChange]);

  // --- INITIALIZE SPEECH RECOGNITION (RUNS ONCE) ---
  useEffect(() => {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
      console.warn("Browser does not support Speech Recognition.");
      return;
    }

    const recognition = new SpeechRecognition();
    recognition.continuous = true;
    recognition.interimResults = true;
    recognition.lang = "en-US";

    recognition.onstart = () => {
      console.log("Recognition started");
      setIsWakeWordActive(true);
    };

    recognition.onresult = (event) => {
      if (loadingRef.current) return;

      const results = Array.from(event.results);
      const lastResult = results[results.length - 1];
      const transcript = lastResult[0].transcript.toLowerCase().trim();
      const isFinal = lastResult.isFinal;

      // --- 1. WAKE WORD DETECTION ---
      if (!isListeningRef.current) {
        if (transcript.includes("guru j") || transcript.includes("guru jay") || transcript.includes("guruji")) {
          console.log("Wake Word Detected!");
          isListeningRef.current = true;
          setIsListeningState(true);

          // Check if query followed immediately
          const parts = transcript.split(/guru j|guru jay|guruji/);
          if (parts.length > 1 && parts[1].trim().length > 5) {
            const query = parts[1].trim();
            console.log("Instant Query:", query);
            onSubmitRef.current(query);
            isListeningRef.current = false;
            setIsListeningState(false);
          }
        }
      }
      // --- 2. QUERY CAPTURE ---
      else {
        if (silenceTimer.current) clearTimeout(silenceTimer.current);

        // Auto-submit after silence
        silenceTimer.current = setTimeout(() => {
          if (transcript.length > 0) {
            console.log("Auto-submitting (Silence):", transcript);
            onSubmitRef.current(transcript);
            isListeningRef.current = false;
            setIsListeningState(false);
          }
        }, 2500);

        if (isFinal && transcript.length > 0) {
          if (silenceTimer.current) clearTimeout(silenceTimer.current);
          console.log("Auto-submitting (Final):", transcript);
          onSubmitRef.current(transcript);
          isListeningRef.current = false;
          setIsListeningState(false);
        }
      }
    };

    recognition.onend = () => {
      // Auto-restart for continuous listening
      if (recognitionRef.current) {
        try {
          recognition.start();
          console.log("...restarting listener...");
        } catch (e) {
          // ignore
        }
      }
    };

    recognition.onerror = (event) => {
      if (event.error === 'not-allowed') {
        setIsWakeWordActive(false);
      }
    };

    try {
      recognition.start();
    } catch (e) { }

    recognitionRef.current = recognition;

    return () => {
      // Cleanup on unmount
      recognitionRef.current = null;
      recognition.stop();
      if (silenceTimer.current) clearTimeout(silenceTimer.current);
    };
  }, []); // Run ONCE on mount

  const manualToggle = () => {
    // Toggle logic using refs
    const newState = !isListeningRef.current;
    isListeningRef.current = newState;
    setIsListeningState(newState);
  };

  return (
    <div className="search-bar" style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '10px' }}>

      {/* Helper Text */}
      {!isListeningState && !loading && isWakeWordActive && (
        <div style={{
          fontSize: '10px',
          color: 'rgba(255,255,255,0.7)',
          background: 'rgba(0,0,0,0.2)',
          padding: '4px 12px',
          borderRadius: '10px',
          marginBottom: '-10px',
          zIndex: 5
        }}>
          Say "Guru J"...
        </div>
      )}

      <button
        onClick={manualToggle}
        className={`mic-btn ${isListeningState ? "recording" : ""}`}
        disabled={loading}
        style={{ position: 'relative' }}
      >
        {loading ? "Thinking..." : isListeningState ? "Listening..." : "🎙️"}

        {isListeningState && !loading && (
          <div className="wake-pulse"></div>
        )}
      </button>
    </div>
  );
}