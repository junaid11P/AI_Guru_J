import React, { useEffect, useState, useRef } from "react";
import { useReactMediaRecorder } from "react-media-recorder-2";

export default function SearchBar({ onSubmit, loading, onStateChange }) {
  const [wakeWordActive, setWakeWordActive] = useState(true);
  const recognitionRef = useRef(null);

  // --- 1. SETUP MEDIA RECORDER (Your existing logic) ---
  const { status, startRecording, stopRecording } = useReactMediaRecorder({
    audio: true,
    onStop: (blobUrl, blob) => {
      // Pass the raw audio blob to App.jsx
      if (blob) {
        onSubmit(blob);
      }
      // After processing, restart wake word listener (after a small delay)
      setTimeout(() => setWakeWordActive(true), 2000);
    }
  });

  const isRecording = status === "recording";

  // --- 2. NOTIFY APP OF STATE CHANGE ---
  useEffect(() => {
    if (onStateChange) {
      onStateChange(isRecording);
    }
  }, [isRecording, onStateChange]);

  // --- 3. WAKE WORD DETECTION LOGIC ---
  useEffect(() => {
    // Check browser support
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    
    if (!SpeechRecognition) {
      console.warn("Browser does not support Speech Recognition.");
      return;
    }

    // Initialize Recognition
    const recognition = new SpeechRecognition();
    recognition.continuous = true;
    recognition.interimResults = true; 
    recognition.lang = "en-US";

    recognition.onresult = (event) => {
      // If we are already recording or loading, ignore speech
      if (isRecording || loading) return;

      const transcript = Array.from(event.results)
        .map((result) => result[0])
        .map((result) => result.transcript)
        .join("")
        .toLowerCase();

      // --- THE TRIGGER PHRASE ---
      // We check for variations like "guru j", "guru jay", "guruji"
      if (transcript.includes("guru j") || transcript.includes("guru")) {
        handleWakeWordTriggered();
      }
    };

    recognitionRef.current = recognition;

    if (wakeWordActive && !isRecording && !loading) {
      try {
        recognition.start();
      } catch (e) {
        // Recognition already started
      }
    } else {
      recognition.stop();
    }

    return () => {
      recognition.stop();
    };
  }, [wakeWordActive, isRecording, loading]); // Re-run if states change

  // --- 4. HANDLER: WHEN WAKE WORD IS HEARD ---
  const handleWakeWordTriggered = () => {
    // 1. Stop the wake listener so it doesn't conflict with the recorder
    setWakeWordActive(false);
    if(recognitionRef.current) recognitionRef.current.stop();

    // 2. Start the actual audio recording
    startRecording();

    // 3. AUTO-STOP LOGIC (Siri Style)
    // Automatically stop recording after 5 seconds to process the query
    setTimeout(() => {
      stopRecording();
    }, 10000); 
  };

  return (
    <div className="search-bar" style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '10px' }}>
      
      {/* Visual Indicator for Wake Word */}
      {wakeWordActive && !loading && !isRecording && (
        <div style={{ 
            fontSize: '10px', 
            color: 'rgba(255,255,255,0.7)', 
            background: 'rgba(0,0,0,0.2)', 
            padding: '4px 12px', 
            borderRadius: '10px',
            marginBottom: '-10px',
            zIndex: 5
        }}>
           Tap or say "Guru J"...
        </div>
      )}

      <button
        onMouseDown={startRecording}
        onMouseUp={stopRecording}
        onTouchStart={startRecording}
        onTouchEnd={stopRecording}
        className={`mic-btn ${isRecording ? "recording" : ""}`}
        disabled={loading}
        style={{ position: 'relative' }}
      >
        {loading? "Thinking...": isRecording? "Listening...":
        (
        <>
          Hold <br /> to Ask <br />
        </>
        )
        }
            
        {/* Visual Pulse ring when Wake Word is active but not recording */}
        {wakeWordActive && !isRecording && !loading && (
             <div className="wake-pulse"></div>
        )}
      </button>
    </div>
  );
}