/**
 * src/components/PartsTable.jsx
 *
 * Results table displaying the sourced parts list.
 * Columns: Item | Product | Qty | Unit Price | Total | Source | Availability | Link
 */

import './PartsTable.css';

const SOURCE_CONFIG = {
  'home depot': { label: 'Home Depot', cls: 'badge-green',  },
  'amazon':     { label: 'Amazon',     cls: 'badge-orange', },
  'unresolved': { label: 'Unresolved', cls: 'badge-gray',   },
};

function getSourceConfig(source) {
  if (!source) return SOURCE_CONFIG['unresolved'];
  const key = source.toLowerCase();
  if (key.includes('home depot') || key.includes('homedepot')) return SOURCE_CONFIG['home depot'];
  if (key.includes('amazon')) return SOURCE_CONFIG['amazon'];
  return { label: source, cls: 'badge-gray' };
}

const AVAIL_CONFIG = {
  'in stock':     { cls: 'avail-dot--green',  label: 'In Stock' },
  'ships':        { cls: 'avail-dot--yellow', label: 'Ships' },
  'limited':      { cls: 'avail-dot--yellow', label: 'Limited' },
  'out of stock': { cls: 'avail-dot--red',    label: 'Out of Stock' },
  'unavailable':  { cls: 'avail-dot--red',    label: 'Unavailable' },
  'unresolved':   { cls: 'avail-dot--red',    label: 'Unresolved' },
};

function getAvailConfig(availability) {
  if (!availability) return AVAIL_CONFIG['unresolved'];
  const key = availability.toLowerCase();
  if (key.includes('in stock'))  return AVAIL_CONFIG['in stock'];
  if (key.includes('ship'))      return AVAIL_CONFIG['ships'];
  if (key.includes('limited'))   return AVAIL_CONFIG['limited'];
  if (key.includes('out'))       return AVAIL_CONFIG['out of stock'];
  if (key.includes('unavail'))   return AVAIL_CONFIG['unavailable'];
  return { cls: 'avail-dot--yellow', label: availability };
}

function ExternalLinkIcon() {
  return (
    <svg
      className="pt-ext-icon"
      viewBox="0 0 16 16"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.5"
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
    >
      <path d="M7 2H2v12h12V9M9 2h5v5M14 2L7 9" />
    </svg>
  );
}

function fmt(n) {
  if (n == null || isNaN(Number(n))) return '—';
  return `$${Number(n).toFixed(2)}`;
}

function PartRow({ part, index }) {
  const productName = part.product_name || part.product_title;
  const url = part.url || part.link;
  const unitPrice = part.unit_price || part.price_per_unit;
  const qty = part.qty || part.quantity;
  const unit = part.unit || '';
  const qtyStr = qty != null ? `${qty} ${unit}`.trim() : '—';
  const totalPrice = part.total_price != null ? part.total_price : Number(unitPrice || 0) * Number(qty || 1);

  const isUnresolved =
    part.resolved === false || part.status === 'unresolved' || part.source === 'unresolved' ||
    (!productName && !url);
  const isClosestMatch = part.status === 'closest_match';

  const sourceConf = getSourceConfig(part.source);
  const availConf  = getAvailConfig(part.availability);

  return (
    <tr
      className={[
        'pt-row',
        index % 2 === 0 ? 'pt-row--even' : 'pt-row--odd',
        isUnresolved    ? 'pt-row--unresolved' : '',
        isClosestMatch  ? 'pt-row--closest-match' : '',
      ].filter(Boolean).join(' ')}
    >
      <td className="pt-cell pt-cell-item">
        <div className="pt-item-name">
          {isUnresolved && <span className="pt-warn-icon" title="Could not source">⚠️</span>}
          <span className={isUnresolved ? 'pt-text-strikethrough' : ''}>
            {part.item_name || part.name || '—'}
          </span>
          {isClosestMatch && (
             <span className="badge badge-orange" style={{ marginLeft: '8px', fontSize: '0.7em', padding: '0.15rem 0.4rem', fontWeight: 'bold' }} title="Closest available match">🔶 Closest Match</span>
          )}
          {part.caveat && (
            <span className="item-caveat" title={part.caveat}>⚠</span>
          )}
        </div>
      </td>
      <td className="pt-cell pt-cell-product">
        <span className={isUnresolved ? 'pt-text-muted' : 'pt-product-name'}>
          {productName || (isUnresolved ? 'Not found' : '—')}
        </span>
      </td>
      <td className="pt-cell pt-cell-num">
        <span className="pt-qty">{qtyStr}</span>
      </td>
      <td className="pt-cell pt-cell-num">
        <span className="pt-price">{fmt(unitPrice)}</span>
      </td>
      <td className="pt-cell pt-cell-num">
        <span className={isUnresolved ? 'pt-text-muted' : 'pt-total'}>
          {isUnresolved ? '—' : fmt(totalPrice)}
        </span>
      </td>
      <td className="pt-cell pt-cell-source">
        <span className={`badge ${sourceConf.cls}`}>{sourceConf.label}</span>
      </td>
      <td className="pt-cell pt-cell-avail">
        <div className="pt-avail-wrap">
          <span className={`avail-dot ${availConf.cls}`} />
          <span className="pt-avail-label">{availConf.label}</span>
        </div>
      </td>
      <td className="pt-cell pt-cell-link">
        {url ? (
          <a href={url} target="_blank" rel="noopener noreferrer" className="pt-link">
            <ExternalLinkIcon />
            <span className="sr-only">View product</span>
          </a>
        ) : (
          <span className="pt-no-link">—</span>
        )}
      </td>
    </tr>
  );
}

export default function PartsTable({ parts = [] }) {
  if (!parts.length) {
    return (
      <div className="parts-empty glass-card">
        <span className="parts-empty-icon">📭</span>
        <p>No parts data yet.</p>
      </div>
    );
  }

  return (
    <div className="parts-section animate-fadeInUp">
      <div className="parts-header">
        <h2 className="parts-title">
          <span className="parts-title-icon">📦</span>
          Parts List
        </h2>
        <span className="parts-count badge badge-green">{parts.length} items</span>
      </div>
      <div className="parts-table-wrap glass-card">
        <div className="parts-table-scroll">
          <table className="parts-table">
            <thead className="pt-thead">
              <tr>
                <th className="pt-th">Item</th>
                <th className="pt-th">Product</th>
                <th className="pt-th pt-th-num">Qty</th>
                <th className="pt-th pt-th-num">Unit Price</th>
                <th className="pt-th pt-th-num">Total</th>
                <th className="pt-th">Source</th>
                <th className="pt-th">Availability</th>
                <th className="pt-th pt-th-center">Link</th>
              </tr>
            </thead>
            <tbody>
              {parts.map((part, i) => (
                <PartRow key={part.id ?? part.item_name ?? i} part={part} index={i} />
              ))}
            </tbody>
          </table>
        </div>
      </div>
      <p className="parts-disclaimer">
        * Prices are estimates and may vary. Availability reflects data at time of search.
      </p>
    </div>
  );
}
