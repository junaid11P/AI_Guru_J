import ReactMarkdown from 'react-markdown';

export default function ExplanationPanel({ explanation, userQuery }) {

  return (
    <GlassCard title="AI Explanation" className="explanation-panel">
      <div className="explanation-content" style={{ height: "100%", display: "flex", flexDirection: "column" }}>
        
        {/* User Question Section - UPDATED TO USE CSS CLASSES */}
        {userQuery && (
          <div className="user-query-box">
            <div className="query-label">YOUR QUESTION</div>
            <div className="query-text">"{userQuery}"</div>
          </div>
        )}

        {/* AI Answer Section */}
        <div className="markdown-body" style={{ 
            flex: 1, 
            overflowY: "auto", 
            paddingRight: "5px",
            color: "white",
            fontSize: "0.95rem",
            lineHeight: "1.6"
        }}>
          {explanation ? (
              <ReactMarkdown>{explanation}</ReactMarkdown>
          ) : (
              "I am ready to help! Ask me anything about Python."
          )}
        </div>

      </div>
    </GlassCard>
  );
}