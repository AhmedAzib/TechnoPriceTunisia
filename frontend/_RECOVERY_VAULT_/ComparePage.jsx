import React from 'react';
import { useCompare } from './context/CompareContext';
import { X, Check, AlertTriangle } from 'lucide-react';
import { Link } from 'react-router-dom';
import './ComparePage.css';

const ComparePage = () => {
  const { compareList, removeFromCompare } = useCompare();

  if (compareList.length === 0) return (
    <div className="compare-container center">
      <div className="empty-compare">
        <h2>Your comparison list is empty.</h2>
        <Link to="/products" className="neon-btn">BROWSE LAPTOPS</Link>
      </div>
    </div>
  );

  // Define which specs to compare and how
  const specsKeys = [
    { label: 'Brand', key: 'brand', compare: false },
    { label: 'Processor', path: ['specs', 'cpu'], compare: 'rank', rankType: 'cpu' },
    { label: 'Graphics', path: ['specs', 'gpu'], compare: 'rank', rankType: 'gpu' },
    { label: 'RAM', path: ['specs', 'ram'], compare: 'number' },
    { label: 'Storage', path: ['specs', 'storage'], compare: 'storage' }, // Special handling for TB vs GB
    { label: 'Screen Size', path: ['specs', 'screen'], compare: 'number' },
    { label: 'Refresh Rate', path: ['specs', 'hz'], compare: 'number' },
    { label: 'Resolution', path: ['specs', 'res'], compare: 'rank', rankType: 'res' },
    { label: 'Panel Type', path: ['specs', 'panel'], compare: false },
    { label: 'OS', path: ['specs', 'os'], compare: false },
  ];

  const getValue = (product, spec) => {
    if (spec.path) return product.specs[spec.path[1]] || '-';
    return product[spec.key] || '-';
  };

  // --- RANKING SYSTEMS ---
  const rankings = {
    cpu: ['Celeron', 'Athlon', 'i3', 'Ryzen 3', 'i5', 'Ryzen 5', 'i7', 'Ryzen 7', 'M1', 'M2', 'M3', 'i9', 'Ryzen 9', 'Ultra 5', 'Ultra 7', 'Ultra 9'],
    gpu: ['Integrated', 'Intel Iris Xe', 'Radeon', 'NVIDIA MX', 'GTX 1650', 'RTX 2050', 'RTX 3050', 'RTX 3060', 'RTX 4050', 'RTX 4060', 'RTX 4070', 'RTX 4080', 'RTX 4090'],
    res: ['HD', 'FHD', 'QHD', 'UHD'],
  };

  const getRankScore = (type, value) => {
    if (!value || value === '-' || value === 'Unknown') return -1;
    let score = -1;
    rankings[type].forEach((keyword, index) => {
      if (value.toUpperCase().includes(keyword.toUpperCase().replace('CORE ', ''))) score = index;
    });
    return score;
  };

  const getNumberScore = (val) => {
    const match = (val || '').match(/(\d+(\.\d+)?)/);
    return match ? parseFloat(match[1]) : 0;
  };

  // Function to find the "best" value string in a row
  const getBestValueStr = (specConfig, allValues) => {
    if (specConfig.compare === false) return null;

    let bestScore = -1;
    let bestValStr = null;
    let hasVariance = false; // Only highlight if there's a difference
    let firstScore = null;
    
    allValues.forEach(val => {
        let currentScore = 0;
        if (specConfig.compare === 'number') currentScore = getNumberScore(val);
        else if (specConfig.compare === 'storage') {
             const num = getNumberScore(val);
             currentScore = val.toUpperCase().includes('TB') || val.toUpperCase().includes('TO') ? num * 1024 : num;
        }
        else if (specConfig.compare === 'rank') currentScore = getRankScore(specConfig.rankType, val);
        
        if (firstScore === null) firstScore = currentScore;
        if (currentScore !== firstScore && currentScore > 0 && firstScore > 0) hasVariance = true;
        
        if (currentScore > bestScore) {
            bestScore = currentScore;
            bestValStr = val;
        }
    });

    // Only return a "best" if there is actual difference and the values aren't all lowest rank/zero
    return (hasVariance && bestScore > 0) ? bestValStr : null;
  };

  return (
    <div className="compare-container">
      <h1>Compare Models</h1>
      <div className="table-wrapper">
        <table className="compare-table">
          <thead>
            <tr>
              <th className="label-col">Specs</th>
              {compareList.map(p => (
                <th key={p.id} className="product-col">
                  <button className="remove-btn" onClick={() => removeFromCompare(p.id)}><X size={14}/> Remove</button>
                  <img src={p.image} alt={p.title} />
                  <h3>{p.title}</h3>
                  <div className="price">{p.price.toFixed(3)} TND</div>
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {specsKeys.map((spec, i) => {
              // 1. Get all values for this row
              const rowValues = compareList.map(p => getValue(p, spec));
              
              // 2. Find the best value string
              const bestValueStr = getBestValueStr(spec, rowValues);
              
              return (
              <tr key={i}>
                <td className="label-cell">{spec.label}</td>
                {compareList.map((p, idx) => {
                  const val = rowValues[idx];
                  // 3. Highlight if it matches the best value string
                  const isWinner = bestValueStr && val === bestValueStr;
                  return (
                    <td key={p.id} className={isWinner ? 'winner-cell' : ''}>
                      {val}
                    </td>
                  )
                })}
              </tr>
            )})}
            <tr>
                <td className="label-cell">Action</td>
                {compareList.map(p => (
                    <td key={p.id}>
                        <Link to={`/product/${p.id}`} className="view-btn">VIEW DETAILS</Link>
                    </td>
                ))}
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default ComparePage;
