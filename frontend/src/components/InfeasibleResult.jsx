/**
 * src/components/InfeasibleResult.jsx
 *
 * Shown when the feasibility agent determines the project cannot be done
 * within the given budget or constraints.
 */

import './InfeasibleResult.css';

export default function InfeasibleResult({ feasibilityData, onReset }) {
  const { reason, alternative } = feasibilityData || {};

  return (
    <div className="ir-wrapper animate-slideUp">

      {/* ── Warning Icon ── */}
      <div className="ir-icon-wrap">
        <div className="ir-icon-ring">
          <span className="ir-icon" role="img" aria-label="Warning">⚠️</span>
        </div>
      </div>

      {/* ── Headline ── */}
      <h2 className="ir-headline">Project Not Feasible</h2>
      <p className="ir-lead">
        Our agents carefully analyzed your project and determined it cannot be
        completed as described within your current budget and constraints.
      </p>

      {/* ── Reason Card ── */}
      {reason && (
        <div className="ir-reason-card glass-card">
          <div className="ir-reason-header">
            <span className="ir-reason-icon">📋</span>
            <span className="ir-reason-title">Agent Analysis</span>
          </div>
          <p className="ir-reason-text">{reason}</p>
        </div>
      )}

      {/* ── Alternative Suggestion ── */}
      {alternative && (
        <div className="ir-suggestion-card glass-card animate-fadeInUp">
          <div className="ir-suggestion-header">
            <span className="ir-suggestion-icon">💡</span>
            <div>
              <span className="ir-suggestion-badge">Suggested Alternative</span>
              <h3 className="ir-suggestion-title">Try This Instead</h3>
            </div>
          </div>
          <p className="ir-suggestion-text">{alternative}</p>
        </div>
      )}

      {/* ── Tips ── */}
      <div className="ir-tips">
        <p className="ir-tips-title">Ways to make it work:</p>
        <ul className="ir-tips-list">
          <li>🔼 Increase your budget</li>
          <li>✂️ Simplify the project scope</li>
          <li>📐 Reduce dimensions or materials</li>
          <li>♻️ Use reclaimed or second-hand materials</li>
        </ul>
      </div>

      {/* ── Actions ── */}
      <div className="ir-actions">
        <button
          className="btn btn-primary ir-btn-retry"
          onClick={onReset}
        >
          <span>↩</span>
          Try Again with New Parameters
        </button>
      </div>

    </div>
  );
}
