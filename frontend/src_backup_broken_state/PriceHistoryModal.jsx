import React from 'react';
import { X, TrendingUp, Activity } from 'lucide-react';
import './ProductsPage.css'; // Re-use existing styles or modal styles if they exist

const PriceHistoryModal = ({ product, onClose }) => {
    if (!product) return null;

    return (
        <div className="modal-overlay" onClick={onClose} style={{
            position: 'fixed',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            backgroundColor: 'rgba(0, 0, 0, 0.7)',
            display: 'flex',
            justifyContent: 'center',
            alignItems: 'center',
            zIndex: 1000,
            backdropFilter: 'blur(5px)'
        }}>
            <div className="modal-content" onClick={e => e.stopPropagation()} style={{
                backgroundColor: '#1e293b',
                padding: '25px',
                borderRadius: '16px',
                width: '90%',
                maxWidth: '500px',
                border: '1px solid rgba(255, 255, 255, 0.1)',
                boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.5)',
                color: 'white',
                position: 'relative'
            }}>
                <button 
                    onClick={onClose}
                    style={{
                        position: 'absolute',
                        top: '15px',
                        right: '15px',
                        background: 'transparent',
                        border: 'none',
                        color: '#94a3b8',
                        cursor: 'pointer'
                    }}
                >
                    <X size={24} />
                </button>

                <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '20px' }}>
                    <div style={{
                        padding: '10px',
                        borderRadius: '12px',
                        background: 'rgba(0, 242, 255, 0.1)',
                        color: '#00f2ff'
                    }}>
                        <TrendingUp size={24} />
                    </div>
                    <div>
                        <h2 style={{ margin: 0, fontSize: '1.2rem' }}>Price History</h2>
                        <span style={{ fontSize: '0.9rem', color: '#94a3b8' }}>Tracking trends across 20+ stores</span>
                    </div>
                </div>

                <div style={{ marginBottom: '20px', paddingBottom: '15px', borderBottom: '1px solid rgba(255,255,255,0.1)' }}>
                    <h3 style={{ fontSize: '1rem', marginBottom: '5px' }}>{product.title}</h3>
                    <div style={{ display: 'flex', gap: '15px', fontSize: '0.9rem', color: '#cbd5e1' }}>
                        <span>Current: <strong style={{ color: '#10b981' }}>{typeof product.price === 'number' ? product.price.toFixed(3) : product.price} DT</strong></span>
                        {product.oldPrice && <span>Old: <span style={{ textDecoration: 'line-through' }}>{product.oldPrice.toFixed(3)} DT</span></span>}
                    </div>
                </div>

                <div style={{ 
                    height: '200px', 
                    background: 'rgba(15, 23, 42, 0.5)', 
                    borderRadius: '12px', 
                    display: 'flex', 
                    flexDirection: 'column',
                    justifyContent: 'center', 
                    alignItems: 'center',
                    border: '1px dashed rgba(255,255,255,0.1)',
                    gap: '15px'
                }}>
                    <Activity size={48} color="#64748b" style={{ opacity: 0.5 }} />
                    <p style={{ color: '#64748b', fontSize: '0.9rem', textAlign: 'center', maxWidth: '80%' }}>
                        Chart visualization coming soon.<br/>
                        We are currently aggregating historical data for this item.
                    </p>
                </div>

                <button 
                    onClick={onClose}
                    style={{
                        width: '100%',
                        padding: '12px',
                        marginTop: '20px',
                        background: '#3b82f6',
                        color: 'white',
                        border: 'none',
                        borderRadius: '8px',
                        fontWeight: '600',
                        cursor: 'pointer'
                    }}
                >
                    Got it
                </button>
            </div>
        </div>
    );
};

export default PriceHistoryModal;
