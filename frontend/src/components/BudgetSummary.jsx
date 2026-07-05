import React from 'react';
import './BudgetSummary.css';

/**
 * BudgetSummary — shows the cost breakdown and a clear over/under indicator.
 *
 * The 10% tax/shipping heuristic is prominently labeled as an estimate
 * so users aren't misled into thinking it's an exact figure.
 */
function fmt(val) {
  return `$${Number(val || 0).toFixed(2)}`;
}

export default function BudgetSummary({ result }) {
  const {
    subtotal = 0,
    estimated_tax_shipping = 0,
    total_estimated = 0,
    budget_usd = 0,
    budget_delta = 0,
    over_budget = false,
  } = result || {};

  const absDelta = Math.abs(budget_delta);

  return (
    <div className="budget-card animate-slideUp">
      <h3 className="budget-title">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" width="20" height="20">
          <path strokeLinecap="round" strokeLinejoin="round"
            d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        Budget Summary
      </h3>

      <div className="budget-rows">
        <div className="budget-row">
          <span className="budget-label">Parts Subtotal</span>
          <span className="budget-value">{fmt(subtotal)}</span>
        </div>
        <div className="budget-row">
          <span className="budget-label">
            Est. Tax &amp; Shipping
            <span className="estimate-note">(~10% heuristic)</span>
          </span>
          <span className="budget-value muted">{fmt(estimated_tax_shipping)}</span>
        </div>
        <div className="budget-row budget-row-total">
          <span className="budget-label">Total Estimated</span>
          <span className="budget-value">{fmt(total_estimated)}</span>
        </div>
        <div className="budget-row budget-row-yours">
          <span className="budget-label">Your Budget</span>
          <span className="budget-value budget-user">{fmt(budget_usd)}</span>
        </div>
      </div>

      {/* Over/Under indicator — the most important element on this card */}
      <div className={`budget-indicator ${over_budget ? 'over' : 'under'}`}>
        <span className="indicator-icon">{over_budget ? '⚠️' : '✅'}</span>
        <div>
          <span className="indicator-verdict">
            {over_budget ? 'OVER BUDGET' : 'UNDER BUDGET'}
          </span>
          <span className="indicator-delta"> by {fmt(absDelta)}</span>
        </div>
      </div>

      <p className="budget-disclaimer">
        Tax and shipping estimate is approximate (10% flat rate). Actual costs vary
        by location, store, and carrier. Prices shown are from Home Depot / Amazon
        at time of search and may have changed.
      </p>
    </div>
  );
}
