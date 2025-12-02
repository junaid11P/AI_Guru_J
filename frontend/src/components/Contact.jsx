import React from "react";

export default function Contact() {
  return (
    <div className="contact-overlay">
      <div className="glass-panel contact-card">
        <div className="panel-header">
          <span>📞   Contact Us</span>
        </div>
        
        <div className="contact-content">
          <h2>We'd love to hear from you!</h2>
          <p className="contact-intro">
            Have questions about Python, suggestions for AI Guru J, or <br/>just want to say hi? 
            Reach out to us through any of the channels below.
          </p>

          <div className="contact-details">
            <div className="detail-item">
              <span className="icon">📍</span>
              <div>
                <strong>Address</strong>
                <p>AI Guru J<br/>Bangalore, Karnataka, India</p>
              </div>
            </div>

            <div className="detail-item">
              <span className="icon">📧</span>
              <div>
                <strong>Email</strong>
                <p>support@aiguruj.com</p>
              </div>
            </div>

            <div className="detail-item">
              <span className="icon">📱</span>
              <div>
                <strong>Phone</strong>
                <p>+91 8105238129</p>
              </div>
            </div>
          </div>

          <div className="social-links">
            <a 
              href="https://github.com/junaid11P" 
              target="_blank" 
              rel="noopener noreferrer"
              className="social-btn github"
            >
              GitHub
            </a>

            <a 
              href="https://www.linkedin.com/in/juned11/" 
              target="_blank" 
              rel="noopener noreferrer"
              className="social-btn linkedin"
            >
              LinkedIn
            </a>

            <a 
              href="https://www.youtube.com/@JunnuBlr" 
              target="_blank" 
              rel="noopener noreferrer"
              className="social-btn"
              style={{ background: "#FF0000" }}
            >
              YouTube
            </a>

            <a 
              href="https://www.instagram.com/junaid11_" 
              target="_blank" 
              rel="noopener noreferrer"
              className="social-btn"
              style={{ background: "#C13584" }}
            >
              Instagram
            </a>
          </div>

        </div>
      </div>
    </div>
  );
}