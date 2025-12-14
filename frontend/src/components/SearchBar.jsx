import React, { useEffect, useState, useRef } from "react";

export default function SearchBar({ onSubmit, loading, onStateChange }) {
  const [isListening, setIsListening] = useState(false); // Active recording state
  const [isWakeWordActive, setIsWakeWordActive] = useState(true); // "Waiting for Guru J" state
  const recognitionRef = useRef(null);
  const silenceTimer = useRef(null);

  // --- REPORT STATE CHANGE ---
  useEffect(() => {
    if (onStateChange) onStateChange(isListening);
  }, [isListening, onStateChange]);

  // --- INITIALIZE SPEECH RECOGNITION ---
  useEffect(() => {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
      console.warn("Browser does not support Speech Recognition.");
      return;
    }

    const recognition = new SpeechRecognition();
    recognition.continuous = true; // Keep listening to detect wake word
    recognition.interimResults = true;
    recognition.lang = "en-US";

    recognition.onresult = (event) => {
      // If loading (processing previous request), ignore input to avoid confusion
      if (loading) return;

      const results = Array.from(event.results);
      const lastResult = results[results.length - 1];
      const transcript = lastResult[0].transcript.toLowerCase().trim();
      const isFinal = lastResult.isFinal;

      // DEBUG: console.log("Heard:", transcript, "Final:", isFinal);

      // --- 1. WAKE WORD DETECTION ---
      if (!isListening) {
        // Flexible matching for "Guru J"
        if (transcript.includes("guru j") || transcript.includes("guru jay") || transcript.includes("guruji")) {
          setIsListening(true);
          // Optional: Play a "ding" sound here
          console.log("Wake Word Detected!");

          // If it was one continuous phrase "Guru J what is python", capture the rest
          const parts = transcript.split(/guru j|guru jay|guruji/);
          if (parts.length > 1 && parts[1].trim().length > 5) {
            // They said the query in the same breath
            onSubmit(parts[1].trim());
            setIsListening(false);
            // Note: recognition continues, but we reset UI
          }
        }
      }
      // --- 2. QUERY CAPTURE ---
      else {
        // We are already listening. Wait for silence/finality.

        // Reset silence timer on every speech event
        if (silenceTimer.current) clearTimeout(silenceTimer.current);

        // Auto-submit if user pauses for 2 seconds (Siri style)
        silenceTimer.current = setTimeout(() => {
          if (transcript.length > 0) {
            console.log("Auto-submitting due to silence:", transcript);
            onSubmit(transcript);
            setIsListening(false);
          }
        }, 2500);

        // Also submit immediately if "Final" (browser thinks sentence ended)
        if (isFinal) {
          if (silenceTimer.current) clearTimeout(silenceTimer.current); // Cancel timer
          if (transcript.length > 0) {
            onSubmit(transcript);
            setIsListening(false);
          }
        }
      }
    };

    recognition.onend = () => {
      // ALWAYS RESTART! (Unless component unmounts)
      // This is the key to "Always Listening"
      if (recognitionRef.current) {
        try {
          recognition.start();
          console.log("...restarting listener...");
        } catch (e) {
          console.log("Restart validation:", e);
        }
      }
    };

    recognition.onerror = (event) => {
      console.error("Speech Error", event.error);
      if (event.error === 'not-allowed') {
        setIsWakeWordActive(false); // User denied permission
      }
      // Use onend to restart
    };

    try {
      recognition.start();
    } catch (e) { console.error(e); }

    recognitionRef.current = recognition;

    return () => {
      recognitionRef.current = null; // Prevent restart loop
      recognition.stop();
      if (silenceTimer.current) clearTimeout(silenceTimer.current);
    };
  }, [onSubmit, loading, isListening]); // Re-bind if these change

  const manualToggle = () => {
    if (isListening) {
      setIsListening(false);
      // recognition continues running for wake word
    } else {
      setIsListening(true);
    }
  };

  return (
    <div className="search-bar" style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '10px' }}>

      {/* Helper Text */}
      {!isListening && !loading && isWakeWordActive && (
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
        className={`mic-btn ${isListening ? "recording" : ""}`}
        disabled={loading}
        style={{ position: 'relative' }}
      >
        {loading ? "Thinking..." : isListening ? "Listening..." : "🎙️"}

        {/* Visual Pulse ring when listening */}
        {isListening && !loading && (
          <div className="wake-pulse"></div>
        )}
      </button>
    </div>
  );
}