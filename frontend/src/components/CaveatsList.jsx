import React from 'react';
import './CaveatsList.css';

/**
 * CaveatsList — surfaces important notes, warnings, and unresolved items.
 *
 * Safety/permit reminders are surfaced prominently because ignoring them
 * can have real consequences for the user (failed inspection, injury risk).
 * Unresolved items are shown in red to make it clear the user needs to
 * find those parts themselves.
 */

const SAFETY_KEYWORDS = ['permit', 'code', 'safety', 'inspector', 'licensed', 'electrical', 'gas', 'load'];

function isSafetyNote(text) {
  const lower = text.toLowerCase();
  return SAFETY_KEYWORDS.some(k => lower.includes(k));
}

export default function CaveatsList({ caveats = [], unresolvedItems = [] }) {
  const hasCaveats = caveats.length > 0;
  const hasUnresolved = unresolvedItems.length > 0;

  if (!hasCaveats && !hasUnresolved) return null;

  const safetyCaveats = caveats.filter(isSafetyNote);
  const regularCaveats = caveats.filter(c => !isSafetyNote(c));

  return (
    <div className="caveats-section animate-slideUp">
      <h3 className="caveats-title">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" width="20" height="20">
          <path strokeLinecap="round" strokeLinejoin="round"
            d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        Important Notes
      </h3>

      {/* Safety / permit reminders — highlighted separately */}
      {safetyCaveats.length > 0 && (
        <div className="safety-block">
          <div className="safety-header">
            <span>🚨</span>
            <span>Safety &amp; Permit Reminders</span>
          </div>
          {safetyCaveats.map((c, i) => (
            <div key={i} className="caveat-card caveat-safety">{c}</div>
          ))}
        </div>
      )}

      {/* Regular caveats */}
      {regularCaveats.map((c, i) => (
        <div key={i} className="caveat-card">
          <span className="caveat-icon">⚠️</span>
          <span>{c}</span>
        </div>
      ))}

      {/* Unresolved items */}
      {hasUnresolved && (
        <div className="unresolved-block">
          <div className="unresolved-header">
            <span>❌</span>
            <span>Items Not Found</span>
          </div>
          <p className="unresolved-desc">
            The following items could not be matched to a product on Home Depot or Amazon.
            You may need to source these locally or adjust the project specifications.
          </p>
          <ul className="unresolved-list">
            {unresolvedItems.map((item, i) => (
              <li key={i}>{item}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
