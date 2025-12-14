import React, { useEffect, useState, useRef } from "react";

export default function SearchBar({ onSubmit, loading, onStateChange }) {
  const [isListening, setIsListening] = useState(false);
  const recognitionRef = useRef(null);

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
    recognition.continuous = false; // We want one sentence/query at a time
    recognition.interimResults = true;
    recognition.lang = "en-US";

    recognition.onstart = () => setIsListening(true);

    recognition.onend = () => {
      setIsListening(false);
    };

    recognition.onresult = (event) => {
      const transcript = Array.from(event.results)
        .map((result) => result[0])
        .map((result) => result.transcript)
        .join("");

      // Ensure we get the final result
      if (event.results[0].isFinal) {
        // If the user says something valid, submit it
        if (transcript.trim().length > 0) {
          onSubmit(transcript);
        }
      }
    };

    recognition.onerror = (event) => {
      console.error("Speech Recognition Error", event.error);
      setIsListening(false);
    };

    recognitionRef.current = recognition;
  }, [onSubmit]);

  const toggleListening = () => {
    if (loading) return;

    if (isListening) {
      recognitionRef.current.stop();
    } else {
      try {
        recognitionRef.current.start();
      } catch (e) {
        console.error("Could not start recognition:", e);
      }
    }
  };

  return (
    <div className="search-bar" style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '10px' }}>

      {/* Helper Text */}
      {!isListening && !loading && (
        <div style={{
          fontSize: '10px',
          color: 'rgba(255,255,255,0.7)',
          background: 'rgba(0,0,0,0.2)',
          padding: '4px 12px',
          borderRadius: '10px',
          marginBottom: '-10px',
          zIndex: 5
        }}>
          Tap to Speak...
        </div>
      )}

      <button
        onClick={toggleListening}
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