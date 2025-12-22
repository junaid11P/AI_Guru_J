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
  const wakeWordIndexRef = useRef(null);
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
        // Check for wake word variations in the *latest* result
        // We only care about the latest result for wake word trigger
        const wakeWordMatch = transcript.match(/guru\s*j[a-z]*|guru\s*ji/i);

        if (wakeWordMatch) {
          console.log("Wake Word Detected!");
          isListeningRef.current = true;
          setIsListeningState(true);

          // Store which result index triggered the wake word so we can accumulate from here
          wakeWordIndexRef.current = results.length - 1;

          // Reset silence timer on wake word
          if (silenceTimer.current) clearTimeout(silenceTimer.current);

          // Strip wake word and capture any immediate query in this same chunk
          const parts = transcript.split(wakeWordMatch[0]);
          if (parts.length > 1 && parts[1].trim().length > 0) {
            // We will handle accumulation in the "else" block by default, 
            // but strictly speaking since we just switched state, we can force an update here or let the next event handle it.
            // For simplicity, let's just let the next pass (or fallthrough if we restructure) handle it, 
            // BUT since we are in the "if (!isListening)" block, we must handle the immediate text here if we want instant feedback.
            // However, accumulation logic is better centralized. 
            // Let's do a quick initial functional update:
            const initialQuery = parts[1].trim();
            if (onInputUpdateRef.current) onInputUpdateRef.current(initialQuery);
          } else {
            if (onInputUpdateRef.current) onInputUpdateRef.current("");
          }
        }
      }
      // --- 2. QUERY CAPTURE (accumulate results) ---
      else {
        // We want to combine all results from wakeWordIndexRef to now
        let fullTranscript = "";

        // Safety check: ensure start index is valid
        const startIndex = wakeWordIndexRef.current !== null ? wakeWordIndexRef.current : 0;

        for (let i = startIndex; i < results.length; i++) {
          let chunk = results[i][0].transcript;
          // If this is the start chunk, we need to strip the wake word if it exists
          if (i === startIndex) {
            const match = chunk.match(/guru\s*j[a-z]*|guru\s*ji/i);
            if (match) {
              chunk = chunk.substring(match.index + match[0].length);
            }
          }
          fullTranscript += chunk + " ";
        }

        fullTranscript = fullTranscript.trim();

        // Update input field in real-time with ACCUMULATED text
        if (onInputUpdateRef.current) onInputUpdateRef.current(fullTranscript);

        // Stop listening AND SUBMIT after silence (Siri-like)
        if (silenceTimer.current) clearTimeout(silenceTimer.current);
        silenceTimer.current = setTimeout(() => {
          if (fullTranscript.length > 0) {
            console.log("Silence detected: Auto-submitting");
            stopAndSubmit(fullTranscript);
          }
        }, 2000);

        if (isFinal) {
          console.log("Chunk final. Continuing to listen...");
        }
      }
    };

    const stopAndSubmit = (text) => {
      isListeningRef.current = false;
      setIsListeningState(false);
      if (silenceTimer.current) clearTimeout(silenceTimer.current);

      if (onSubmit && text) {
        onSubmit(text);
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
    if (loading || !!errorMsg) return;

    // Toggle logic
    const newState = !isListeningRef.current;
    isListeningRef.current = newState;
    setIsListeningState(newState);

    if (newState && onInputUpdateRef.current) {
      onInputUpdateRef.current("");
      wakeWordIndexRef.current = null; // Important: reset index for manual start
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
        title={errorMsg || "Wake Word / Manual"}
        style={{ position: 'relative' }}
      >
        {loading ? "..." : isListeningState ? "🛑" : "🎙️"}
        <span style={{ fontSize: '10px', marginTop: '4px' }}>Guru Ji</span>
        {isListeningState && !loading && (
          <div className="wake-pulse"></div>
        )}
      </button>
    </div>
  );
}