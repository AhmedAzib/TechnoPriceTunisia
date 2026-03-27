import React, { useState } from 'react';
import { ChevronDown, ChevronUp } from 'lucide-react';

const FilterSection = ({ title, options, selected, onSelect, isOpen = false, counts = {}, disableZero = false, children, onClear }) => {
  const [open, setOpen] = useState(isOpen);
  const [showAll, setShowAll] = useState(false);

  return (
    <div className="filter-section">
      <div className="fs-header" onClick={() => setOpen(!open)}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', flex: 1 }}>
            <span>{title}</span>
            {selected && selected.length > 0 && (
                <span style={{
                    background: '#5F8D8B',
                    color: 'white',
                    borderRadius: '50%',
                    width: '20px',
                    height: '20px',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    fontSize: '0.7rem',
                    fontWeight: 'bold',
                    marginLeft: '8px'
                }}>
                    {selected.length}
                </span>
            )}
            {selected && selected.length > 0 && onClear && (
                <span 
                    onClick={(e) => { e.stopPropagation(); onClear(); }}
                    style={{ fontSize: '0.7rem', color: '#5F8D8B', textDecoration: 'underline', cursor: 'pointer' }}
                >
                    Clear
                </span>
            )}
        </div>
        {open ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
      </div>
      <div 
        className="fs-body" 
        style={{ 
          maxHeight: open ? '2000px' : '0', 
          opacity: open ? 1 : 0, 
          overflow: 'hidden', 
          transition: 'all 0.5s ease',
          padding: open ? '0 12px 10px' : '0 12px 0' 
        }}
      >
        {children ? children : (
          <>
          {options.slice(0, open ? (showAll ? options.length : 5) : 0).map(opt => {
             const count = counts[opt] !== undefined ? counts[opt] : null;
             const isDisabled = disableZero && count === 0;
             return (
                <label key={opt} className="checkbox-row" style={{ opacity: isDisabled ? 0.5 : 1, cursor: isDisabled ? 'not-allowed' : 'pointer' }}>
                  <input 
                    type="checkbox" 
                    checked={selected.includes(opt)} 
                    onChange={() => !isDisabled && onSelect(opt)}
                    disabled={isDisabled}
                  />
                  {opt}
                  {count !== null && <span style={{ marginLeft: 'auto', fontSize: '0.7rem', color: '#64748b' }}>({count})</span>}
                </label>
             );
          })}
          {options.length > 5 && (
            <div 
              onClick={(e) => {
                  e.stopPropagation();
                  setShowAll(!showAll);
              }}
              style={{ fontSize: '0.75rem', color: '#5F8D8B', cursor: 'pointer', marginTop: '5px', fontWeight: '600' }}
            >
               {showAll ? "Show Less" : "Show More"}
            </div>
          )}
          </>
        )}
      </div>
    </div>
  );
};

export default FilterSection;
