import React, { useState } from "react";
import GlassCard from "./GlassCard";

export default function CodePanel({ codeData }) {
  const [copied, setCopied] = useState(false);
  
  // Default text if empty
  const displayCode = codeData || "# Waiting for generated code...";

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(displayCode);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000); // Reset after 2s
    } catch (err) {
      console.error("Failed to copy:", err);
    }
  };

  return (
    <div className="glass-panel code-interpreter" style={{ 
        padding: "0", 
        overflow: "hidden", 
        display: "flex", 
        flexDirection: "column",
        background: "rgba(30, 30, 30, 0.85)", // VS Code-like dark bg
        backdropFilter: "blur(12px)",
        border: "1px solid rgba(255, 255, 255, 0.1)",
        borderRadius: "16px",
        height: "100%",
        boxShadow: "0 8px 32px 0 rgba(0, 0, 0, 0.3)"
    }}>
      {/* --- INTERPRETER HEADER --- */}
      <div className="interpreter-header" style={{
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          padding: "10px 15px",
          background: "rgba(255, 255, 255, 0.05)",
          borderBottom: "1px solid rgba(255, 255, 255, 0.1)"
      }}>
        {/* Window Controls */}
        <div style={{ display: "flex", gap: "8px" }}>
            <div style={{ width: "12px", height: "12px", borderRadius: "50%", background: "#FF5F56" }}></div>
            <div style={{ width: "12px", height: "12px", borderRadius: "50%", background: "#FFBD2E" }}></div>
            <div style={{ width: "12px", height: "12px", borderRadius: "50%", background: "#27C93F" }}></div>
        </div>

        {/* File Name */}
        <div style={{ 
            color: "#aaa", 
            fontSize: "0.9rem", 
            fontFamily: "monospace",
            fontWeight: "bold"
        }}>
            📄 solution.py
        </div>

        {/* Copy Button */}
        <button 
            onClick={handleCopy}
            style={{
                background: copied ? "#27C93F" : "rgba(255, 255, 255, 0.1)",
                border: "none",
                borderRadius: "6px",
                padding: "5px 12px",
                color: "white",
                cursor: "pointer",
                fontSize: "0.8rem",
                transition: "all 0.2s ease",
                display: "flex",
                alignItems: "center",
                gap: "5px"
            }}
            title="Copy Code"
        >
            {copied ? (
                <><span>✓</span> Copied</>
            ) : (
                <><span>📋</span> Copy</>
            )}
        </button>
      </div>

      {/* --- CODE CONTENT --- */}
      <div className="code-content" style={{ 
          padding: "15px",
          fontFamily: "'Fira Code', 'Consolas', monospace",
          fontSize: "14px",
          lineHeight: "1.5",
          color: "#d4d4d4",
          whiteSpace: "pre-wrap",
          wordBreak: "break-word",
          overflowY: "auto",
          flex: 1
      }}>
        {displayCode.split("\n").map((line, i) => (
          <div key={i} style={{ display: "flex" }}>
            {/* Line Numbers */}
            <span className="line-num" style={{ 
                minWidth: "35px", 
                marginRight: "15px", 
                color: "#6e7681", 
                textAlign: "right",
                userSelect: "none",
                fontSize: "12px",
                paddingTop: "2px"
            }}>
                {i + 1}
            </span>
            {/* Syntax Coloring (Simple Heuristic) */}
            <span style={{ color: getLineColor(line) }}>{line}</span>
          </div>
        ))}
      </div>
    </div>
  );
}

// Simple helper to add fake syntax highlighting colors
function getLineColor(line) {
    const l = line.trim();
    if (l.startsWith("#")) return "#6A9955"; // Comments (Green)
    if (l.startsWith("def ") || l.startsWith("class ")) return "#569CD6"; // Keywords (Blue)
    if (l.startsWith("import ") || l.startsWith("from ")) return "#C586C0"; // Imports (Purple)
    if (l.startsWith("print") || l.startsWith("return")) return "#DCDCAA"; // Functions (Yellow-ish)
    if (l.includes('"') || l.includes("'")) return "#CE9178"; // Strings (Orange)
    return "#d4d4d4"; // Default
}