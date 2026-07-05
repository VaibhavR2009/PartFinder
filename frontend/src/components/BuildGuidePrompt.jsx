import React, { useState } from 'react';
import './BuildGuidePrompt.css';

export default function BuildGuidePrompt({ inputData, resultData }) {
  const [copied, setCopied] = useState(false);

  if (!inputData || !resultData || !resultData.parts) return null;

  // Build the prompt text
  const partsListText = resultData.parts.map(p => 
    `- ${p.qty}x ${p.product_title || p.product_name || p.item_name} (from ${p.source})`
  ).join('\n');
  
  const toolsText = inputData.tools_on_hand?.length 
    ? inputData.tools_on_hand.join(', ') 
    : 'None specified';

  const caveatsText = resultData.caveats?.length 
    ? '\nCaveats:\n' + resultData.caveats.map(c => `- ${c}`).join('\n')
    : '';

  const promptText = `I want to build a DIY project based on the following details. Please act as an expert DIY builder and guide me step-by-step through the construction process.

Project Description:
${inputData.description}

My Skill Level: ${inputData.skill_level}
Tools I have on hand: ${toolsText}

I have already sourced the following parts:
${partsListText}${caveatsText}

Please provide:
1. A logical step-by-step build guide.
2. Any safety tips or precautions I should take.
3. Recommendations for any additional tools or materials I might have missed.`;

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
