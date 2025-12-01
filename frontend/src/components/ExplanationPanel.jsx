import React from "react";
import GlassCard from "./GlassCard";

export default function ExplanationPanel({ explanation, userQuery }) {
  // REMOVED: const headerIcon = <span className="panel-icon">🔊</span>;

  return (
    <GlassCard title="AI Explanation" className="explanation-panel">
      <div className="explanation-content" style={{ height: "100%", display: "flex", flexDirection: "column", gap: "15px" }}>
        
        {/* User Question Section */}
        {userQuery && (
          <div style={{
            background: "rgba(255, 255, 255, 0.05)",
            padding: "12px",
            borderRadius: "8px",
            borderLeft: "4px solid #a855f7", // Purple accent
            marginBottom: "10px"
          }}>
            <div style={{ fontSize: "0.8rem", color: "#a855f7", fontWeight: "bold", marginBottom: "4px" }}>
              YOUR QUESTION:
            </div>
            <div style={{ fontStyle: "italic", color: "#f50505ff" }}>
              "{userQuery}"
            </div>
          </div>
        )}

        {/* AI Answer Section */}
        <div style={{ 
            flex: 1, 
            overflowY: "auto", 
            lineHeight: "1.6", 
            color: "#0e0101ff",
            whiteSpace: "pre-wrap",
            paddingRight: "5px"
        }}>
          {explanation || "I am ready to help! Ask me anything about Python."}
        </div>

      </div>
    </GlassCard>
  );
}