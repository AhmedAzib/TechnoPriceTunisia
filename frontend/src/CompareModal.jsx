import React, { useMemo } from 'react';
import { X, Check, ShoppingCart, ExternalLink } from 'lucide-react';
import { MASTER_DATA } from './data/masterData';
import { normalizeProductData } from './utils/productUtils';
import './ProductsPage.css';

const CompareModal = ({ isOpen, onClose, selectedProducts }) => {
    if (!isOpen || !selectedProducts || selectedProducts.length === 0) return null;

    // HYDRATE DATA: Ensure we are using the LATEST specs
    const hydratedProducts = useMemo(() => {
        const freshRaw = selectedProducts.map(staleItem => {
            const fresh = MASTER_DATA.find(m => m.id === staleItem.id || m.link === staleItem.link);
            return fresh || staleItem;
        });
        return normalizeProductData(freshRaw);
    }, [selectedProducts]);

    // Helper to extract numeric price
    const getPrice = (p) => {
        if (typeof p.price === 'number') return p.price;
        return parseFloat(p.price.toString().replace(/[^0-9.]/g, '')) || 0;
    };

    // Helper to extract numeric Hz
    const getHz = (p) => {
        const val = p.specs.hz || "";
        const match = val.match(/(\d+)/);
        return match ? parseInt(match[1]) : 0;
    };

    const minPrice = Math.min(...hydratedProducts.map(p => getPrice(p)));
    const maxHz = Math.max(...hydratedProducts.map(p => getHz(p)));

    return (
        <div className="compare-modal-overlay" onClick={onClose}>
            <div className="compare-modal-content" onClick={e => e.stopPropagation()}>
                <button className="modal-close-btn" onClick={onClose}>
                    <X size={24} />
                </button>
                
                <h2>Compare Specs</h2>
                
                <div className="compare-table-container">
                    <table className="compare-table">
                        <thead>
                            <tr>
                                <th>Feature</th>
                                {hydratedProducts.map(product => (
                                    <th key={product.id}>
                                        <div className="th-product-header">
                                            <img src={product.image} alt={product.title} />
                                            <span title={product.title}>{product.title.substring(0, 30)}...</span>
                                        </div>
                                    </th>
                                ))}
                            </tr>
                        </thead>
                        <tbody>
                            {/* Price Row */}
                            <tr className="price-row-table">
                                <td className="label">Price</td>
                                {hydratedProducts.map(product => {
                                    const price = getPrice(product);
                                    const isCheapest = price === minPrice;
                                    return (
                                        <td key={product.id} className={isCheapest ? "best-price" : ""}>
                                            {price.toFixed(3)} DT
                                            {isCheapest && <span className="best-deal-tag">Best Deal</span>}
                                        </td>
                                    );
                                })}
                            </tr>
                            
                            {/* Specs Rows */}
                            <tr>
                                <td className="label">Store</td>
                                {hydratedProducts.map(product => (
                                    <td key={product.id}>
                                        <span className={`store-badge ${product.source.toLowerCase()}`}>
                                            {product.source}
                                        </span>
                                    </td>
                                ))}
                            </tr>
                            {(() => {
                                // Detect if comparing phones or computers
                                const isPhone = hydratedProducts.some(p =>
                                    (p.specs?.category || p.category || '').toLowerCase() === 'smartphone'
                                );

                                if (isPhone) {
                                    // PHONE COMPARE: Price, Store, CPU, RAM, Storage only
                                    return (
                                        <>
                                        <tr>
                                            <td className="label">CPU</td>
                                            {hydratedProducts.map(product => <td key={product.id}>{product.specs.cpu || '-'}</td>)}
                                        </tr>
                                        <tr>
                                            <td className="label">RAM</td>
                                            {hydratedProducts.map(product => <td key={product.id}>{product.specs.ram || '-'}</td>)}
                                        </tr>
                                        <tr>
                                            <td className="label">Storage</td>
                                            {hydratedProducts.map(product => <td key={product.id}>{product.specs.storage || '-'}</td>)}
                                        </tr>
                                        </>
                                    );
                                } else {
                                    // COMPUTER COMPARE: Full specs
                                    return (
                                        <>
                                        <tr>
                                            <td className="label">Brand</td>
                                            {hydratedProducts.map(product => <td key={product.id}>{product.brand || '-'}</td>)}
                                        </tr>
                                        <tr>
                                            <td className="label">System (OS)</td>
                                            {hydratedProducts.map(product => <td key={product.id}>{product.specs.os || '-'}</td>)}
                                        </tr>
                                        <tr>
                                            <td className="label">CPU</td>
                                            {hydratedProducts.map(product => <td key={product.id}>{product.specs.cpu || '-'}</td>)}
                                        </tr>
                                        <tr>
                                            <td className="label">RAM</td>
                                            {hydratedProducts.map(product => <td key={product.id}>{product.specs.ram || '-'}</td>)}
                                        </tr>
                                        <tr>
                                            <td className="label">Storage</td>
                                            {hydratedProducts.map(product => <td key={product.id}>{product.specs.storage || '-'}</td>)}
                                        </tr>
                                        <tr>
                                            <td className="label">GPU</td>
                                            {hydratedProducts.map(product => <td key={product.id}>{product.specs.gpu || '-'}</td>)}
                                        </tr>
                                        <tr>
                                            <td className="label">Screen</td>
                                            {hydratedProducts.map(product => <td key={product.id}>{product.specs.screen || '-'}</td>)}
                                        </tr>
                                        <tr>
                                            <td className="label">Refresh Rate</td>
                                            {hydratedProducts.map(product => {
                                                const hz = getHz(product);
                                                const isBest = hz === maxHz && hz > 60;
                                                return (
                                                    <td key={product.id} className={isBest ? "best-price" : ""}>
                                                        {product.specs.hz || '-'}
                                                        {isBest && <span style={{color: '#10b981', marginLeft: '5px'}}>✓</span>}
                                                    </td>
                                                )
                                            })}
                                        </tr>
                                        </>
                                    );
                                }
                            })()}
                            
                            {/* Action Row */}
                            <tr className="action-row">
                                <td></td>
                                {hydratedProducts.map(product => (
                                    <td key={product.id}>
                                        <a href={product.link} target="_blank" rel="noopener noreferrer" className="view-store-btn">
                                            View on Store <ExternalLink size={14}/>
                                        </a>
                                    </td>
                                ))}
                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    );
};

export default CompareModal;
