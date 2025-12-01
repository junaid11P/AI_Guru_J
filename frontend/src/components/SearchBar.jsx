import React, { useEffect } from "react";
import { useReactMediaRecorder } from "react-media-recorder-2";

export default function SearchBar({ onSubmit, loading, onStateChange }) {
  const { status, startRecording, stopRecording } = useReactMediaRecorder({
    audio: true,
    onStop: (blobUrl, blob) => {
        // Pass the raw audio blob to App.jsx for processing
        if (blob) {
            onSubmit(blob); 
        }
    }
  });

  const isRecording = status === "recording";

  // CRITICAL: Notify App.jsx (and subsequently ThreeScene) 
  // whenever the recording state changes. 
  // This triggers the "Thinking" animation in the 3D scene.
  useEffect(() => {
    if (onStateChange) {
      onStateChange(isRecording);
    }
  }, [isRecording, onStateChange]);

  return (
    <div className="search-bar">
      <button
        onMouseDown={startRecording}
        onMouseUp={stopRecording}
        // Touch support for mobile devices
        onTouchStart={startRecording}
        onTouchEnd={stopRecording}
        className={`mic-btn ${isRecording ? "recording" : ""}`}
        disabled={loading}
      >
        {loading ? "Thinking..." : isRecording ? "Listening..." : "Hold to Ask"}
      </button>
    </div>
  );
}