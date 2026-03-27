import React from 'react';
import { useCompare } from '../CompareContext';
import { Link } from 'react-router-dom';

function CompareBar() {
  const { compareList, removeFromCompare, clearCompare } = useCompare();

  if (compareList.length === 0) return null;

  return (
    <div style={{
      position: 'fixed', bottom: '20px', left: '50%', transform: 'translateX(-50%)',
      backgroundColor: 'white', padding: '15px 25px', borderRadius: '50px',
      boxShadow: '0 10px 30px rgba(0,0,0,0.2)', zIndex: 1000,
      display: 'flex', alignItems: 'center', gap: '20px', border: '1px solid #e2e8f0'
    }}>
      <div style={{ display: 'flex', gap: '10px' }}>
        {compareList.map(p => (
          <div key={p.id} style={{ position: 'relative' }}>
            <img src={p.image_url} alt={p.name} 
              style={{ width: '40px', height: '40px', borderRadius: '50%', objectFit: 'contain', border: '1px solid #ddd', padding: '2px' }} 
            />
            <button onClick={() => removeFromCompare(p.id)}
              style={{
                position: 'absolute', top: '-5px', right: '-5px',
                background: '#ff4444', color: 'white', border: 'none',
                borderRadius: '50%', width: '18px', height: '18px', fontSize: '10px',
                cursor: 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'center'
              }}>×</button>
          </div>
        ))}
      </div>

      <div style={{ width: '1px', height: '30px', backgroundColor: '#ddd' }}></div>

      <span style={{ fontWeight: '600', color: '#333' }}>{compareList.length} Selected</span>

      {compareList.length > 1 && (
        <Link to="/compare" style={{
          backgroundColor: '#2563eb', color: 'white', padding: '8px 20px',
          borderRadius: '20px', textDecoration: 'none', fontWeight: 'bold'
        }}>
          Compare VS
        </Link>
      )}

      <button onClick={clearCompare} style={{ background: 'none', border: 'none', color: '#666', cursor: 'pointer', textDecoration: 'underline' }}>
        Clear
      </button>
    </div>
  );
}

export default CompareBar;
