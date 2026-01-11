import React from "react";

// Added 'icon' prop, defaulted to the star if not provided
export default function GlassCard({ title, children, className = "", icon = "★" }) {
  return (
    <div className={`glass-panel ${className}`}>
      <div className="panel-header">
        <span>{title}</span>
        {/* Render the passed icon component or string */}
        <span>{icon}</span>
      </div>
      <div className="panel-content">
        {children}
      </div>
    </div>
  );
}