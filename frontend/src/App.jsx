import React, { useState, useEffect } from "react";
import ThreeScene from "./components/ThreeScene";
import TeacherSelector from "./components/TeacherSelector";
import SearchBar from "./components/SearchBar";
import CodePanel from "./components/CodePanel";
import ExplanationPanel from "./components/ExplanationPanel";
import Contact from "./components/Contact"; 
import axios from "axios";
import "./index.css";

export default function App() {
  const [teacher, setTeacher] = useState("female");
  const [loading, setLoading] = useState(false);
  const [isRecording, setIsRecording] = useState(false);
  const [view, setView] = useState("home"); 

  const [inputText, setInputText] = useState(""); 
  const [userQuery, setUserQuery] = useState("");
  const [explanation, setExplanation] = useState("");
  const [codeData, setCodeData] = useState(`# AI Guru J Ready.\n# Ask a question (e.g., "swap numbers") to start!`);
  
  const [audioUrl, setAudioUrl] = useState(null);
  const [lipSyncData, setLipSyncData] = useState(null);

  // --- AUTO-UPDATE AUDIO WHEN TEACHER OR TEXT CHANGES ---
  useEffect(() => {
    // 1. Don't play audio if loading, empty, or just "Thinking..."
    if (!explanation || loading || explanation === "Thinking...") {
        setAudioUrl(null);
        return;
    }

    // 2. Construct the URL dynamically based on CURRENT teacher
    // We use encodeURIComponent to make the text safe for a URL
    const safeText = encodeURIComponent(explanation);
    // Adding timestamp (t=...) forces the browser to reload the audio even if the URL looks similar
    const newUrl = `http://127.0.0.1:8000/api/tutor/audio_stream/?text=${safeText}&gender=${teacher}&t=${Date.now()}`;
    
    setAudioUrl(newUrl);

  }, [teacher, explanation, loading]); 

  async function sendToBackend(formData) {
    setLoading(true);
    setExplanation("Thinking..."); 
    setUserQuery("");
    setCodeData("# Generating code..."); 

    try {
      const resp = await axios.post("http://127.0.0.1:8000/api/tutor/query/", formData, {
        headers: { "Content-Type": "multipart/form-data" }
      });

      const data = resp.data;

      setUserQuery(data.user_query || "User Query"); 
      
      // Setting explanation triggers the useEffect above to fetch audio
      setExplanation(data.explanation || "Here is the explanation.");
      
      const validCode = data.code && data.code.trim().length > 0 
        ? String(data.code) 
        : "# The AI provided an explanation but no specific code snippet.";
        
      setCodeData(validCode);
      setLipSyncData(data.lip_sync || null); 

    } catch (e) {
      console.error("API Error:", e);
      setExplanation("Error connecting to AI Guru J backend. Please check the terminal.");
      setCodeData("# Connection Error.");
      setAudioUrl(null);
    } finally {
      setLoading(false);
    }
  }

  async function handleSubmitAudio(audioBlob) {
    const formData = new FormData();
    formData.append("audio_file", audioBlob, "input.wav"); 
    formData.append("teacher_gender", teacher); 
    await sendToBackend(formData);
  }

  async function handleSubmitText() {
    if (!inputText.trim()) return;
    const formData = new FormData();
    formData.append("text_query", inputText);
    formData.append("teacher_gender", teacher);
    await sendToBackend(formData);
    setInputText(""); 
  }

  return (
    <div className="app-root">
      <nav className="top-nav">
        <div className="logo-container" onClick={() => setView("home")} style={{cursor: 'pointer'}}>
            <span className="logo-3d">🧊</span>
            <span className="logo-text">AI Guru J</span>
        </div>
        <div className="nav-links">
            <a 
              href="#" 
              className={`nav-item ${view === "home" ? "active" : ""}`}
              onClick={(e) => { e.preventDefault(); setView("home"); }}
            >
              Home
            </a>
            <a 
              href="#" 
              className={`nav-item ${view === "contact" ? "active" : ""}`}
              onClick={(e) => { e.preventDefault(); setView("contact"); }}
            >
              Contact
            </a>
        </div>
      </nav>

      {view === "contact" ? (
        <Contact />
      ) : (
        <>
          <div className="top-right-selector">
            <TeacherSelector teacher={teacher} setTeacher={setTeacher} />
          </div>

          <div className="main-content-area">
            <div className="whiteboard-container">
                <div className="wb-panel-left">
                    <CodePanel codeData={codeData} />
                </div>
                <div className="wb-panel-right">
                     <ExplanationPanel explanation={explanation} userQuery={userQuery} />
                </div>
            </div>
            <div className="avatar-container">
                <ThreeScene 
                    teacher={teacher} 
                    lipSyncData={lipSyncData} 
                    audioUrl={audioUrl}
                    isRecording={isRecording} 
                    loading={loading} /* <--- PASSING LOADING STATE HERE */
                />
            </div>
          </div>

          <div className="bottom-bar">
            <div className="search-bar-container">
                <SearchBar 
                    onSubmit={handleSubmitAudio} 
                    loading={loading} 
                    onStateChange={setIsRecording}
                />
            </div>

            <div className="text-input-container">
                <input 
                    type="text" 
                    className="text-input-field" 
                    placeholder="Type your question..." 
                    value={inputText}
                    onChange={(e) => setInputText(e.target.value)}
                    onKeyDown={(e) => e.key === 'Enter' && handleSubmitText()}
                    disabled={loading}
                />
                <button 
                    className="input-send-btn" 
                    onClick={handleSubmitText}
                    disabled={loading}
                >
                    {loading ? "..." : "➤"}
                </button>
            </div>
            <div className="bottom-icon sparkle">✨</div>
          </div>
        </>
      )}
    </div>
  );
}