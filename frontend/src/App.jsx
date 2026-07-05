import React from 'react';
import { usePartFinder } from './hooks/usePartFinder';
import ProjectForm from './components/ProjectForm';
import ProgressTracker from './components/ProgressTracker';
import InfeasibleResult from './components/InfeasibleResult';
import PartsTable from './components/PartsTable';
import BudgetSummary from './components/BudgetSummary';
import CaveatsList from './components/CaveatsList';
import ErrorState from './components/ErrorState';
import BuildGuidePrompt from './components/BuildGuidePrompt';
import './App.css';

/**
 * App — root component.
 *
 * State routing:
 *   idle       → show ProjectForm
 *   loading    → show ProgressTracker (with form header still visible)
 *   infeasible → show InfeasibleResult
 *   done       → show PartsTable + BudgetSummary + CaveatsList
 *   error      → show ErrorState
 *
 * The ProgressTracker is especially important for the demo video:
 * it shows all four agents activating in real time.
 */
export default function App() {
  const {
    state,
    stages,
    feasibilityData,
    resultData,
    inputData,
    error,
    submit,
    reset,
  } = usePartFinder();

  const isLoading = state === 'loading';
  const isDone = state === 'done';
  const isInfeasible = state === 'infeasible';
  const isError = state === 'error';
  const isIdle = state === 'idle';

  return (
    <div className="app-shell">
      {/* ── Persistent header bar ── */}
      <header className="app-header">
        <div className="header-inner">
          <div className="brand">
            <span className="brand-icon">🔩</span>
            <span className="brand-name">PartFinder</span>
          </div>
          <div className="header-badges">
            <span className="tech-badge">Google ADK</span>
            <span className="tech-badge">MCP</span>
            <span className="tech-badge tech-badge-ai">Gemini 2.5 Flash</span>
          </div>
        </div>
      </header>

      {/* ── Main content area ── */}
      <main className="app-main">

        {/* IDLE: Show the input form */}
        {isIdle && (
          <div className="content-center animate-fadeIn">
            <ProjectForm onSubmit={submit} isLoading={isLoading} />
          </div>
        )}

        {/* LOADING: Show ProgressTracker alongside a compact form header */}
        {isLoading && (
          <div className="content-loading animate-fadeIn">
            <div className="loading-header">
              <span className="loading-logo">🔩</span>
              <div>
                <h1 className="loading-title">Finding Your Parts</h1>
                <p className="loading-subtitle">Running 4 specialized AI agents...</p>
              </div>
            </div>
            <ProgressTracker stages={stages} />
          </div>
        )}

        {/* INFEASIBLE: Show the feasibility agent's explanation */}
        {isInfeasible && (
          <div className="content-center animate-fadeIn">
            <InfeasibleResult
              feasibilityData={feasibilityData}
              onReset={reset}
            />
          </div>
        )}

        {/* DONE: Show the full results */}
        {isDone && resultData && (
          <div className="content-results animate-fadeIn">
            {/* Results header */}
            <div className="results-header">
              <h1 className="results-title">Your Parts List</h1>
              <button className="btn-ghost" onClick={reset}>
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" width="14" height="14">
                  <path strokeLinecap="round" strokeLinejoin="round"
                    d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                </svg>
                New Search
              </button>
            </div>

            {/* Parts table (full width) */}
            <PartsTable parts={resultData.parts || resultData.parts_list || []} />

            {/* Budget + Caveats (side by side on wide screens) */}
            <div className="results-bottom">
              <BudgetSummary result={resultData} />
              <CaveatsList
                caveats={resultData.caveats || []}
                unresolvedItems={resultData.unresolved_items || []}
              />
            </div>
            
            {/* AI Build Guide Prompt */}
            <BuildGuidePrompt inputData={inputData} resultData={resultData} />
          </div>
        )}

        {/* ERROR: Graceful error display */}
        {isError && (
          <div className="content-center animate-fadeIn">
            <ErrorState message={error} onReset={reset} />
          </div>
        )}
      </main>

      {/* ── Footer ── */}
      <footer className="app-footer">
        <span>Built with</span>
        <span className="footer-badge">Google ADK</span>
        <span>+</span>
        <span className="footer-badge">FastMCP</span>
        <span>+</span>
        <span className="footer-badge">SerpApi</span>
        <span>·</span>
        <span>Kaggle AI Agents Capstone 2026</span>
      </footer>
    </div>
  );
}
