import React, { useEffect, useState, useRef } from "react";

export default function SearchBar({ onSubmit, loading, onStateChange, onInputUpdate }) {
  const [isListeningState, setIsListeningState] = useState(false); // For UI rendering
  const [isWakeWordActive, setIsWakeWordActive] = useState(true); // For UI rendering
  const [errorMsg, setErrorMsg] = useState(null);

  // Refs for stable access inside event listeners
  const isListeningRef = useRef(false);
  const loadingRef = useRef(loading);
  const recognitionRef = useRef(null);
  const silenceTimer = useRef(null);
  const onInputUpdateRef = useRef(onInputUpdate);

  // Sync props/state to refs
  useEffect(() => { loadingRef.current = loading; }, [loading]);
  useEffect(() => { onInputUpdateRef.current = onInputUpdate; }, [onInputUpdate]);
  useEffect(() => {
    if (onStateChange) onStateChange(isListeningState);
  }, [isListeningState, onStateChange]);

  // --- INITIALIZE SPEECH RECOGNITION (RUNS ONCE) ---
  useEffect(() => {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
      setErrorMsg("Browser unsupported");
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
      setErrorMsg(null);
    };

    recognition.onresult = (event) => {
      if (loadingRef.current) return;

      const results = Array.from(event.results);
      const lastResult = results[results.length - 1];
      let transcript = lastResult[0].transcript.toLowerCase().trim();
      const isFinal = lastResult.isFinal;

      // --- 1. WAKE WORD DETECTION ---
      if (!isListeningRef.current) {
        // Check for wake word variations
        const wakeWordMatch = transcript.match(/guru\s*j[a-z]*|guru\s*ji/i);

        if (wakeWordMatch) {
          console.log("Wake Word Detected!");
          isListeningRef.current = true;
          setIsListeningState(true);

          // Reset silence timer on wake word
          if (silenceTimer.current) clearTimeout(silenceTimer.current);

          // Strip wake word and capture any immediate query
          const parts = transcript.split(wakeWordMatch[0]);
          if (parts.length > 1 && parts[1].trim().length > 0) {
            const cleanQuery = parts[1].trim();
            if (onInputUpdateRef.current) onInputUpdateRef.current(cleanQuery);
          } else {
            // Clear input if only wake word was said
            if (onInputUpdateRef.current) onInputUpdateRef.current("");
          }
        }
      }
      // --- 2. QUERY CAPTURE ---
      else {
        // Handle "Guru Ji" being repeated or just normal speech
        // We might want to strip "Guru Ji" if it appears again, but usually we just take the text

        // Update input field in real-time
        if (onInputUpdateRef.current) onInputUpdateRef.current(transcript);

        if (silenceTimer.current) clearTimeout(silenceTimer.current);

        // Stop listening (but DONT submit) after silence
        silenceTimer.current = setTimeout(() => {
          if (transcript.length > 0) {
            console.log("Silence detected: Stopping listening");
            isListeningRef.current = false;
            setIsListeningState(false);
            // We assume the user enters the text to review
          }
        }, 5000);

        if (isFinal) {
          console.log("Final result: Stopping listening");
          isListeningRef.current = false;
          setIsListeningState(false);
          if (silenceTimer.current) clearTimeout(silenceTimer.current);
        }
      }
    };

    recognition.onend = () => {
      // Auto-restart for continuous listening
      // Unless we explicitly stopped ? For now, always try to keep wake word active
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
      console.error("Speech Recognition Error:", event.error);
      if (event.error === 'not-allowed') {
        setIsWakeWordActive(false);
        setErrorMsg("Mic Permission Denied");
      } else if (event.error === 'no-speech') {
        // ignore
      } else {
        setErrorMsg("Voice Error");
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
    if (newState && onInputUpdateRef.current) {
      // Clear input when manually starting? Optional. 
      // onInputUpdateRef.current(""); 
    }
  };

  return (
    <div className="search-bar" style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '10px' }}>

      {/* Helper Text / Error Msg */}
      {(!isListeningState && !loading) && (
        <div style={{
          fontSize: '10px',
          color: errorMsg ? '#ff6b6b' : 'rgba(255,255,255,0.7)',
          background: 'rgba(0,0,0,0.2)',
          padding: '4px 12px',
          borderRadius: '10px',
          marginBottom: '-10px',
          zIndex: 5
        }}>
          {errorMsg ? errorMsg : (isWakeWordActive ? 'Say "Guru Ji"...' : 'Mic Inactive')}
        </div>
      )}

      <button
        onClick={manualToggle}
        className={`mic-btn ${isListeningState ? "recording" : ""}`}
        disabled={loading || !!errorMsg}
        title={errorMsg || "Activate Voice"}
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