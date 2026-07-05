/**
 * src/components/ProgressTracker.jsx
 *
 * Live multi-stage progress display with animated vertical timeline.
 * This is the centerpiece during demo recording — designed to impress.
 *
 * Stage status:
 *   pending  → dim dot
 *   running  → spinning ring + pulsing glow
 *   done     → animated green checkmark
 */

import './ProgressTracker.css';

const STAGE_ORDER = ['feasibility', 'sourcing', 'verification', 'compiler'];

const STAGE_META = {
  feasibility:  { icon: '🧠', label: 'Feasibility Check',   description: 'Analyzing project requirements and constraints...' },
  sourcing:     { icon: '🏪', label: 'Parts Sourcing',       description: 'Searching Home Depot for exact part matches...' },
  verification: { icon: '🔬', label: 'Verification',         description: 'Verifying specifications and availability...' },
  compiler:     { icon: '📦', label: 'Compiling Results',    description: 'Assembling your complete parts list...' },
};

function StageIcon({ status, emoji }) {
  if (status === 'done') {
    return (
      <div className="pt-stage-icon pt-stage-icon--done">
        <svg className="pt-checkmark" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
          <polyline points="20 6 9 17 4 12" />
        </svg>
      </div>
    );
  }

  if (status === 'running') {
    return (
      <div className="pt-stage-icon pt-stage-icon--running">
        <span className="pt-stage-emoji">{emoji}</span>
        <div className="pt-spin-ring" />
      </div>
    );
  }

  // pending
  return (
    <div className="pt-stage-icon pt-stage-icon--pending">
      <span className="pt-stage-emoji pt-stage-emoji--dim">{emoji}</span>
    </div>
  );
}

function StageDot({ status }) {
  return (
    <span
      className={[
        'pt-status-dot',
        status === 'done'    && 'pt-status-dot--done',
        status === 'running' && 'pt-status-dot--running',
        status === 'pending' && 'pt-status-dot--pending',
      ].filter(Boolean).join(' ')}
    />
  );
}

function StatusLabel({ status }) {
  const labels = { pending: 'Waiting', running: 'In Progress', done: 'Complete' };
  return (
    <span className={`pt-status-label pt-status-label--${status}`}>
      {labels[status]}
    </span>
  );
}

export default function ProgressTracker({ stages }) {
  const activeStageIndex = STAGE_ORDER.findIndex(key => stages[key]?.status === 'running');
  const doneCount = STAGE_ORDER.filter(key => stages[key]?.status === 'done').length;
  const progressPct = Math.round((doneCount / STAGE_ORDER.length) * 100);

  return (
    <div className="pt-wrapper animate-fadeInUp">
      {/* ── Header ── */}
      <div className="pt-header">
        <div className="pt-header-left">
          <div className="pt-header-icon animate-pulse">⚙️</div>
          <div>
            <h2 className="pt-title">Finding Your Parts</h2>
            <p className="pt-subtitle">Our AI agents are working on your project</p>
          </div>
        </div>
        <div className="pt-progress-badge">
          <span className="pt-progress-pct">{progressPct}%</span>
        </div>
      </div>

      {/* ── Global progress bar ── */}
      <div className="pt-progress-bar-track">
        <div
          className="pt-progress-bar-fill"
          style={{ width: `${progressPct}%` }}
        />
      </div>

      {/* ── Timeline ── */}
      <div className="pt-timeline glass-card">
        {STAGE_ORDER.map((key, index) => {
          const meta   = STAGE_META[key];
          const status = stages[key]?.status || 'pending';
          const isLast = index === STAGE_ORDER.length - 1;
          const isActive = status === 'running';

          return (
            <div
              key={key}
              className={[
                'pt-stage',
                isActive && 'pt-stage--active',
                status === 'done' && 'pt-stage--done',
                status === 'pending' && 'pt-stage--pending',
              ].filter(Boolean).join(' ')}
              style={{ animationDelay: `${index * 80}ms` }}
            >
              {/* Left column: icon + connecting line */}
              <div className="pt-stage-left">
                <StageIcon status={status} emoji={meta.icon} />
                {!isLast && (
                  <div className={`pt-connector ${status === 'done' ? 'pt-connector--lit' : ''}`}>
                    <div className="pt-connector-line" />
                    {status === 'done' && <div className="pt-connector-fill" />}
                  </div>
                )}
              </div>

              {/* Right column: content */}
              <div className="pt-stage-content">
                <div className="pt-stage-top">
                  <span className="pt-stage-label">{meta.label}</span>
                  <div className="pt-stage-status">
                    <StageDot status={status} />
                    <StatusLabel status={status} />
                  </div>
                </div>
                <p className={`pt-stage-desc ${status === 'pending' ? 'pt-stage-desc--dim' : ''}`}>
                  {isActive ? (
                    <span className="pt-typing-text">{meta.description}</span>
                  ) : status === 'done' ? (
                    <span className="pt-done-text">✓ Completed successfully</span>
                  ) : (
                    meta.description
                  )}
                </p>

                {/* Active stage: animated progress dots */}
                {isActive && (
                  <div className="pt-loading-dots" aria-label="Loading">
                    <span /><span /><span />
                  </div>
                )}
              </div>
            </div>
          );
        })}
      </div>

      {/* ── Footer tip ── */}
      <p className="pt-footer-tip">
        💡 Results stream live — stay on this page
      </p>
    </div>
  );
}
