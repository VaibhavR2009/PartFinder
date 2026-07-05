import React, { useState } from 'react';
import './BuildGuidePrompt.css';

export default function BuildGuidePrompt({ inputData, resultData }) {
  const [copied, setCopied] = useState(false);

  const partsList = resultData.parts || resultData.parts_list;
  if (!inputData || !resultData || !partsList) return null;

  // Use the pre-generated prompt from the Compiler Agent, or a fallback if not present
  const promptText = resultData.build_guide_prompt || `I want to build a DIY project based on the following details. Please act as an expert DIY builder and guide me step-by-step through the construction process.

Project Description:
${inputData.description}

Please provide a logical step-by-step build guide, safety tips, and recommendations.`;

  const copyToClipboard = () => {
    navigator.clipboard.writeText(promptText);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="prompt-card glass-card">
      <div className="prompt-header">
        <h3 className="prompt-title">
          <span className="prompt-icon">🤖</span>
          AI Build Guide Prompt
        </h3>
        <button className="btn-ghost prompt-copy-btn" onClick={copyToClipboard}>
          {copied ? 'Copied!' : 'Copy Prompt'}
        </button>
      </div>
      <p className="prompt-description">
        Copy this prompt and paste it into ChatGPT, Claude, or Gemini to get a step-by-step build guide customized to your tools and sourced parts.
      </p>
      <div className="prompt-textarea-wrapper">
        <textarea
          className="prompt-textarea"
          readOnly
          value={promptText}
        />
      </div>
    </div>
  );
}
