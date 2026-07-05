/**
 * src/components/ProjectForm.jsx
 *
 * The main project input form. Beautiful animated dark-mode form with:
 * - Project description textarea
 * - Budget input with $ prefix
 * - ZIP code input
 * - Skill level selector
 * - Multi-tag "tools on hand" input
 * - Full form validation
 */

import { useState, useRef, useCallback } from 'react';
import './ProjectForm.css';

// Skill level options with emoji icons
const SKILL_LEVELS = [
  { value: 'beginner',     label: 'Beginner',     icon: '🌱', desc: 'New to DIY' },
  { value: 'intermediate', label: 'Intermediate',  icon: '🔧', desc: 'Some experience' },
  { value: 'advanced',     label: 'Advanced',      icon: '⚡', desc: 'Seasoned builder' },
];

export default function ProjectForm({ onSubmit, isLoading }) {
  const [description, setDescription] = useState('');
  const [budget, setBudget]           = useState('');
  const [zipCode, setZipCode]         = useState('');
  const [skillLevel, setSkillLevel]   = useState('beginner');
  const [tools, setTools]             = useState([]);
  const [toolInput, setToolInput]     = useState('');
  const [errors, setErrors]           = useState({});

  const toolInputRef = useRef(null);

  // ── Validation ──────────────────────────────────────────────
  const validate = () => {
    const newErrors = {};

    if (!description.trim() || description.trim().length < 20) {
      newErrors.description = 'Please describe your project in at least 20 characters.';
    }
    if (!budget || isNaN(Number(budget)) || Number(budget) <= 0) {
      newErrors.budget = 'Please enter a valid budget amount.';
    }
    if (Number(budget) > 100000) {
      newErrors.budget = 'Budget seems too high — please enter a realistic amount.';
    }
    if (!zipCode.trim() || !/^\d{5}(-\d{4})?$/.test(zipCode.trim())) {
      newErrors.zipCode = 'Please enter a valid 5-digit ZIP code.';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  // ── Tool Tag Management ──────────────────────────────────────
  const addTool = useCallback(() => {
    const trimmed = toolInput.trim();
    if (trimmed && !tools.includes(trimmed)) {
      setTools(prev => [...prev, trimmed]);
    }
    setToolInput('');
    toolInputRef.current?.focus();
  }, [toolInput, tools]);

  const removeTool = useCallback((tool) => {
    setTools(prev => prev.filter(t => t !== tool));
  }, []);

  const handleToolKeyDown = (e) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      addTool();
    }
    if (e.key === 'Backspace' && toolInput === '' && tools.length > 0) {
      setTools(prev => prev.slice(0, -1));
    }
  };

  // ── Submit ───────────────────────────────────────────────────
  const handleSubmit = (e) => {
    e.preventDefault();
    if (!validate()) return;

    onSubmit({
      description: description.trim(),
      budget_usd: Number(budget),
      zip_code: zipCode.trim(),
      skill_level: skillLevel,
      tools_on_hand: tools,
    });
  };

  // Clear error on field change
  const clearError = (field) => setErrors(prev => ({ ...prev, [field]: undefined }));

  return (
    <div className="pf-form-wrapper animate-fadeInUp">
      {/* ── Header ── */}
      <div className="pf-form-header">
        <div className="pf-logo-badge">
          <span className="pf-logo-icon">🔩</span>
        </div>
        <h1 className="pf-form-title gradient-text">PartFinder</h1>
        <p className="pf-form-subtitle">
          Describe your project and get a complete sourced parts list — within budget.
        </p>
      </div>

      {/* ── Form ── */}
      <form className="pf-form glass-card" onSubmit={handleSubmit} noValidate>

        {/* Project Description */}
        <div className={`pf-field ${errors.description ? 'pf-field--error' : ''}`}>
          <label className="pf-label" htmlFor="description">
            <span className="pf-label-icon">📋</span>
            Project Description
          </label>
          <textarea
            id="description"
            className="pf-textarea"
            placeholder="Describe your DIY project in detail. For example: 'Build a 6x4 ft raised garden bed with cedar planks, lined with landscape fabric, and a simple drip irrigation system...'"
            value={description}
            onChange={e => { setDescription(e.target.value); clearError('description'); }}
            rows={5}
            disabled={isLoading}
            maxLength={2000}
          />
          <div className="pf-field-footer">
            {errors.description
              ? <span className="pf-error-msg">{errors.description}</span>
              : <span className="pf-hint">Be specific — include dimensions, materials, and goals</span>
            }
            <span className="pf-char-count">{description.length}/2000</span>
          </div>
        </div>

        {/* Budget + ZIP Row */}
        <div className="pf-row">
          {/* Budget */}
          <div className={`pf-field ${errors.budget ? 'pf-field--error' : ''}`}>
            <label className="pf-label" htmlFor="budget">
              <span className="pf-label-icon">💰</span>
              Total Budget
            </label>
            <div className="pf-input-with-prefix">
              <span className="pf-input-prefix">$</span>
              <input
                id="budget"
                type="number"
                className="pf-input pf-input--prefixed"
                placeholder="0.00"
                value={budget}
                onChange={e => { setBudget(e.target.value); clearError('budget'); }}
                min="1"
                max="100000"
                step="0.01"
                disabled={isLoading}
              />
            </div>
            {errors.budget && <span className="pf-error-msg">{errors.budget}</span>}
          </div>

          {/* ZIP Code */}
          <div className={`pf-field ${errors.zipCode ? 'pf-field--error' : ''}`}>
            <label className="pf-label" htmlFor="zipCode">
              <span className="pf-label-icon">📍</span>
              ZIP Code
            </label>
            <input
              id="zipCode"
              type="text"
              className="pf-input"
              placeholder="e.g. 90210"
              value={zipCode}
              onChange={e => { setZipCode(e.target.value); clearError('zipCode'); }}
              maxLength={10}
              disabled={isLoading}
            />
            {errors.zipCode && <span className="pf-error-msg">{errors.zipCode}</span>}
          </div>
        </div>

        {/* Skill Level */}
        <div className="pf-field">
          <label className="pf-label">
            <span className="pf-label-icon">🎯</span>
            Skill Level
          </label>
          <div className="pf-skill-grid">
            {SKILL_LEVELS.map(({ value, label, icon, desc }) => (
              <label
                key={value}
                className={`pf-skill-option ${skillLevel === value ? 'pf-skill-option--selected' : ''}`}
              >
                <input
                  type="radio"
                  name="skillLevel"
                  value={value}
                  checked={skillLevel === value}
                  onChange={() => setSkillLevel(value)}
                  disabled={isLoading}
                  className="pf-skill-radio"
                />
                <span className="pf-skill-icon">{icon}</span>
                <span className="pf-skill-label">{label}</span>
                <span className="pf-skill-desc">{desc}</span>
              </label>
            ))}
          </div>
        </div>

        {/* Tools on Hand */}
        <div className="pf-field">
          <label className="pf-label" htmlFor="toolInput">
            <span className="pf-label-icon">🛠️</span>
            Tools on Hand
            <span className="pf-label-optional">(optional)</span>
          </label>
          <div className={`pf-tag-input-wrapper ${isLoading ? 'pf-tag-input-wrapper--disabled' : ''}`}>
            {tools.map(tool => (
              <span key={tool} className="pf-tag animate-fadeIn">
                {tool}
                <button
                  type="button"
                  className="pf-tag-remove"
                  onClick={() => removeTool(tool)}
                  disabled={isLoading}
                  aria-label={`Remove ${tool}`}
                >
                  ×
                </button>
              </span>
            ))}
            <input
              ref={toolInputRef}
              id="toolInput"
              type="text"
              className="pf-tag-input"
              placeholder={tools.length === 0 ? 'Type a tool and press Enter...' : 'Add another...'}
              value={toolInput}
              onChange={e => setToolInput(e.target.value)}
              onKeyDown={handleToolKeyDown}
              disabled={isLoading}
            />
          </div>
          <span className="pf-hint">Press Enter to add each tool (e.g. drill, saw, level)</span>
        </div>

        {/* Submit Button */}
        <button
          type="submit"
          className="btn btn-primary pf-submit-btn"
          disabled={isLoading}
        >
          {isLoading ? (
            <>
              <span className="btn-spinner" />
              Finding Parts...
            </>
          ) : (
            <>
              <span className="pf-submit-icon">🔍</span>
              Find My Parts
            </>
          )}
        </button>

      </form>
    </div>
  );
}
