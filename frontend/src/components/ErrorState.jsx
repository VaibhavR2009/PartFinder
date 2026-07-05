import React from 'react';
import './ErrorState.css';

/**
 * ErrorState — graceful error display.
 * Never shows a blank screen. Always gives the user a way to recover.
 */
export default function ErrorState({ message, onReset }) {
  return (
    <div className="error-container animate-slideUp">
      <div className="error-icon">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
          <circle cx="12" cy="12" r="10" />
          <line x1="15" y1="9" x2="9" y2="15" />
          <line x1="9" y1="9" x2="15" y2="15" />
        </svg>
      </div>

      <h2 className="error-title">Something Went Wrong</h2>

      <p className="error-message">
        {message || 'An unexpected error occurred while processing your request.'}
      </p>

      <div className="error-hints">
        <p>Try the following:</p>
        <ul>
          <li>Check that your API keys are correctly set in <code>.env</code></li>
          <li>Ensure the MCP server is running on port 8001</li>
          <li>Verify your internet connection</li>
          <li>Try enabling <code>DEMO_MODE=true</code> to test without live APIs</li>
        </ul>
      </div>

      <button className="btn-primary" onClick={onReset}>
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" width="16" height="16">
          <path strokeLinecap="round" strokeLinejoin="round"
            d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
        </svg>
        Try Again
      </button>
    </div>
  );
}
