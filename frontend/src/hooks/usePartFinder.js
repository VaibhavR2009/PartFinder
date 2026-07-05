/**
 * src/hooks/usePartFinder.js
 *
 * Custom React hook that manages the entire PartFinder pipeline state.
 * Connects to the SSE API client and provides structured state to the UI.
 *
 * Pipeline States:
 *   idle        — form is visible, nothing running
 *   loading     — SSE stream is active, stages progressing
 *   infeasible  — agent determined project cannot be done
 *   done        — pipeline complete, results are available
 *   error       — something went wrong
 *
 * Stage Statuses:
 *   pending  — not started yet
 *   running  — currently active (show spinner)
 *   done     — complete (show checkmark)
 */

import { useState, useCallback, useRef } from 'react';
import { runPartFinder } from '../api/client.js';

// Initial stage definitions
const INITIAL_STAGES = {
  feasibility: { status: 'pending', label: 'Feasibility Check',   description: 'Checking project feasibility...' },
  sourcing:    { status: 'pending', label: 'Parts Sourcing',       description: 'Searching Home Depot for parts...' },
  verification:{ status: 'pending', label: 'Verification',         description: 'Verifying product specifications...' },
  compiler:    { status: 'pending', label: 'Compiling Results',    description: 'Compiling your parts list...' },
};

export function usePartFinder() {
  // Overall pipeline state
  const [state, setState] = useState('idle');

  // Per-stage status map
  const [stages, setStages] = useState(INITIAL_STAGES);

  // Data from feasibility check
  const [feasibilityData, setFeasibilityData] = useState(null);

  // Final compiled result (parts list, budget, caveats, etc.)
  const [resultData, setResultData] = useState(null);

  // Error message string
  const [error, setError] = useState(null);

  // Original user input (available when done/infeasible)
  const [inputData, setInputData] = useState(null);

  // Abort controller ref for cancellation
  const abortRef = useRef(null);

  /**
   * Update a single stage's status.
   */
  const updateStage = useCallback((stageName, status) => {
    setStages(prev => ({
      ...prev,
      [stageName]: {
        ...prev[stageName],
        status,
      },
    }));
  }, []);

  /**
   * Handle incoming SSE events from the backend.
   *
   * The backend emits named events matching stage names:
   *   event: feasibility  → { stage, status, message, data: feasibilityData }
   *   event: sourcing     → { stage, status, message, data: sourcingData }
   *   event: verification → { stage, status, message, data: verificationData }
   *   event: compiler     → { stage, status, message, data: compilerData }
   *   event: complete     → { stage, status, message, data: { result, feasibility, input } }
   *   event: error        → { stage: "error", status: "error", message, data: null }
   */
  const handleEvent = useCallback((eventType, payload) => {
    console.debug('[PartFinder event]', eventType, payload);

    // All events from the backend carry { stage, status, message, data }
    const { stage, status, data } = payload || {};

    // Update the matching stage's status (running → done)
    const KNOWN_STAGES = ['feasibility', 'sourcing', 'verification', 'compiler'];
    if (KNOWN_STAGES.includes(stage)) {
      if (status === 'running' || status === 'done') {
        updateStage(stage, status);
      }
    }

    switch (stage) {
      case 'feasibility': {
        if (data) {
          setFeasibilityData(data);
          // Stop pipeline display if infeasible
          if (data.feasible === false && status === 'done') {
            setState('infeasible');
          }
        }
        break;
      }

      case 'compiler': {
        // The compiler's done event carries the final parts list
        if (status === 'done' && data) {
          setResultData(data);
        }
        break;
      }

      case 'complete': {
        // Final event — carries the full result
        if (status === 'infeasible') {
          if (data?.feasibility) setFeasibilityData(data.feasibility);
          if (data?.input) setInputData(data.input);
          setState('infeasible');
        } else if (status === 'done') {
          if (data?.result) setResultData(data.result);
          if (data?.input) setInputData(data.input);
          setState('done');
        }
        break;
      }

      case 'error': {
        const msg = payload?.message || 'Unknown error';
        setError(msg);
        setState('error');
        break;
      }

      default:
        // Sourcing / verification stages — just track status (handled above)
        break;
    }
  }, [updateStage]);


  /**
   * Handle stream completion (reader.done === true).
   */
  const handleDone = useCallback(() => {
    setState(prev => {
      if (prev === 'loading') return 'done';
      return prev;
    });
  }, []);

  /**
   * Handle stream-level errors.
   */
  const handleError = useCallback((err) => {
    setError(err?.message || String(err) || 'Connection failed');
    setState('error');
  }, []);

  /**
   * Submit the project form and start the pipeline.
   *
   * @param {Object} projectData - Form values to send to the backend
   */
  const submit = useCallback((projectData) => {
    // Cancel any in-flight request
    if (abortRef.current) abortRef.current();

    // Reset state
    setState('loading');
    setStages(INITIAL_STAGES);
    setFeasibilityData(null);
    setResultData(null);
    setError(null);

    // Start SSE stream
    abortRef.current = runPartFinder(
      projectData,
      handleEvent,
      handleDone,
      handleError,
    );
  }, [handleEvent, handleDone, handleError]);

  /**
   * Reset everything back to the idle/form state.
   */
  const reset = useCallback(() => {
    // Cancel any in-flight request
    if (abortRef.current) {
      abortRef.current();
      abortRef.current = null;
    }

    setState('idle');
    setStages(INITIAL_STAGES);
    setFeasibilityData(null);
    setResultData(null);
    setError(null);
  }, []);

  return {
    state,
    stages,
    feasibilityData,
    resultData,
    inputData,
    error,
    submit,
    reset,
  };
}
