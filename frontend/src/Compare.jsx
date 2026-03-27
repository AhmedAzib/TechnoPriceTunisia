import React, { useEffect, useState } from 'react';
import { useCompare } from './CompareContext';
import { Link } from 'react-router-dom';
import axios from 'axios';

function Compare() {
  const { compareList, removeFromCompare } = useCompare();
  const [detailedProducts, setDetailedProducts] = useState([]);
  const [loading, setLoading] = useState(true);

  // --- FETCH DATA ---
  useEffect(() => {
    if (compareList.length === 0) {
      setDetailedProducts([]);
      setLoading(false);
      return;
    }

    const ids = compareList.map(p => p.id).join(',');
    axios.get(`http://127.0.0.1:8000/api/products/compare/?ids=${ids}`)
      .then(res => {
        setDetailedProducts(res.data);
        setLoading(false);
      })
      .catch(err => {
        console.error("Comparison Error:", err);
        setLoading(false);
      });
  }, [compareList]);

  if (compareList.length === 0) {
    return (
      <div style={{ textAlign: 'center', marginTop: '100px', fontFamily: '"Inter", sans-serif' }}>
        <h2>No products to compare 🤷‍♂️</h2>
        <Link to="/" style={{ color: '#2563eb', fontWeight: 'bold' }}>Go back to shop</Link>
      </div>
    );
  }

  if (loading) return <div style={{ textAlign: 'center', marginTop: '50px' }}>Loading comparison...</div>;

  // --- WINNER LOGIC HELPERS ---
  const parseNum = (str) => {
    if (!str) return 0;
    const match = str.match(/(\d+)/);
    return match ? parseInt(match[1]) : 0;
  };

  const parsePrice = (prices) => {
    if (!prices || prices.length === 0) return 999999;
    return Math.min(...prices.map(p => parseFloat(p.price)));
  };

  const getWinner = (field) => {
    if (detailedProducts.length < 2) return null; // No winner if only 1 item

    let values = detailedProducts.map(p => {
        if (field === 'price') return parsePrice(p.prices);
        if (field === 'ram') return parseNum(p.ram);
        if (field === 'storage') return parseNum(p.storage);
        if (field === 'screen') return parseFloat(p.screen_size) || 0;
        return 0;
    });

    // Strategy: Price = Lower is better. Others = Higher is better.
    let bestVal;
    if (field === 'price') {
        bestVal = Math.min(...values);
    } else {
        bestVal = Math.max(...values);
    }

    // Return array of indices that are winners
    return values.map((v, i) => (v === bestVal && v !== 0 && v !== 999999) ? i : -1).filter(i => i !== -1);
  };

  const winners = {
    price: getWinner('price'),
    ram: getWinner('ram'),
    storage: getWinner('storage'),
    screen: getWinner('screen')
  };

  // Check if index is a winner for a field
  const isWinner = (idx, field) => winners[field] && winners[field].includes(idx);

  return (
    <div style={{ padding: '40px', maxWidth: '1400px', margin: '0 auto', fontFamily: '"Inter", sans-serif' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '30px' }}>
        <h1 style={{ margin: 0 }}>Compare Laptops ⚔️</h1>
        <Link to="/" style={{ textDecoration: 'none', background: '#f1f5f9', padding: '10px 20px', borderRadius: '8px', color: '#333' }}>
          ← Back to Shop
        </Link>
      </div>

      <div style={{ overflowX: 'auto' }}>
        <table style={{ width: '100%', borderCollapse: 'collapse', borderRadius: '12px', overflow: 'hidden', boxShadow: '0 4px 6px -1px rgba(0,0,0,0.1)' }}>
          <thead>
            <tr>
              <th style={{ padding: '20px', background: '#f8fafc', textAlign: 'left', minWidth: '150px' }}>Specs</th>
              {detailedProducts.map((p, i) => (
                <th key={p.id} style={{ padding: '20px', background: 'white', minWidth: '250px', borderBottom: '1px solid #e2e8f0', position: 'relative' }}>
                  <button onClick={() => removeFromCompare(p.id)} 
                    style={{ position: 'absolute', top: '10px', right: '10px', border: 'none', background: 'none', color: '#ef4444', cursor: 'pointer', fontSize: '1.2rem' }}>
                    ×
                  </button>
                  <img src={p.image_url} alt={p.name} style={{ height: '120px', objectFit: 'contain', marginBottom: '15px' }} />
                  <div style={{ fontSize: '1.1rem', color: '#0f172a' }}>{p.name}</div>
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {/* PRICE ROW */}
            <tr>
              <td style={{ padding: '20px', fontWeight: 'bold' }}>Best Price</td>
              {detailedProducts.map((p, i) => {
                const price = parsePrice(p.prices);
                return (
                  <td key={p.id} style={{ 
                    padding: '20px', borderBottom: '1px solid #e2e8f0', background: isWinner(i, 'price') ? '#dcfce7' : 'white',
                    color: isWinner(i, 'price') ? '#166534' : '#333', fontWeight: isWinner(i, 'price') ? '700' : '400'
                  }}>
                    {price} TND
                  </td>
                );
              })}
            </tr>

             {/* GRAPHICS ROW (No numeric winner logic usually, just text) */}
             <tr>
              <td style={{ padding: '20px', fontWeight: 'bold' }}>Graphics Card</td>
              {detailedProducts.map(p => (
                <td key={p.id} style={{ padding: '20px', borderBottom: '1px solid #e2e8f0', background: 'white' }}>
                  <span style={{ fontWeight: '600', color: '#d946ef' }}>{p.gpu}</span>
                </td>
              ))}
            </tr>

            {/* RAM ROW */}
            <tr>
              <td style={{ padding: '20px', fontWeight: 'bold' }}>RAM</td>
              {detailedProducts.map((p, i) => (
                <td key={p.id} style={{ 
                  padding: '20px', borderBottom: '1px solid #e2e8f0', background: isWinner(i, 'ram') ? '#dcfce7' : 'white'
                }}>
                  {p.ram}
                </td>
              ))}
            </tr>

            {/* STORAGE ROW */}
             <tr>
              <td style={{ padding: '20px', fontWeight: 'bold' }}>Storage</td>
              {detailedProducts.map((p, i) => (
                <td key={p.id} style={{ 
                  padding: '20px', borderBottom: '1px solid #e2e8f0', background: isWinner(i, 'storage') ? '#dcfce7' : 'white'
                }}>
                  {p.storage}
                </td>
              ))}
            </tr>

            {/* SCREEN ROW */}
            <tr>
              <td style={{ padding: '20px', fontWeight: 'bold' }}>Screen</td>
              {detailedProducts.map((p, i) => (
                <td key={p.id} style={{ 
                    padding: '20px', borderBottom: '1px solid #e2e8f0', background: isWinner(i, 'screen') ? '#dcfce7' : 'white'
                  }}>
                  {p.screen_size}
                </td>
              ))}
            </tr>

            {/* CPU ROW */}
            <tr>
              <td style={{ padding: '20px', fontWeight: 'bold' }}>Processor</td>
              {detailedProducts.map(p => (
                <td key={p.id} style={{ padding: '20px', borderBottom: '1px solid #e2e8f0', background: 'white' }}>
                  {p.cpu}
                </td>
              ))}
            </tr>

             {/* BRAND ROW */}
             <tr>
              <td style={{ padding: '20px', fontWeight: 'bold' }}>Brand</td>
              {detailedProducts.map(p => (
                <td key={p.id} style={{ padding: '20px', borderBottom: '1px solid #e2e8f0', background: 'white' }}>
                  {p.brand.name}
                </td>
              ))}
            </tr>

          </tbody>
        </table>
      </div>
    </div>
  );
}

export default Compare;
