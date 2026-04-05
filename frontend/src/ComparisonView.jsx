import React, { useState } from 'react';
import { ArrowLeft, ExternalLink, X, Check, Link } from 'lucide-react';
import './ProductsPage.css';

const ComparisonView = ({ selectedProducts, onClose, removeFromCompare }) => {
    // Defines full-screen layout
    const [copied, setCopied] = useState(false);

    const handleShare = () => {
        const ids = selectedProducts.map(p => p.id).join(',');
        const url = `${window.location.origin}${window.location.pathname}?compare=${ids}`;
        
        if (navigator.clipboard) {
            navigator.clipboard.writeText(url).then(() => {
                setCopied(true);
                setTimeout(() => setCopied(false), 2000);
            }).catch(err => console.error("Failed to copy", err));
        } else {
             // Fallback
             const textArea = document.createElement("textarea");
             textArea.value = url;
             document.body.appendChild(textArea);
             textArea.select();
             document.execCommand("copy");
             document.body.removeChild(textArea);
             setCopied(true);
             setTimeout(() => setCopied(false), 2000);
        }
    };
    
    // Helper to extract numeric price for comparison
    const getPrice = (p) => {
        if (typeof p.price === 'number') return p.price;
        return parseFloat(p.price.toString().replace(/[^0-9.]/g, '')) || 0;
    };
    // Helper to extract numeric value from spec strings (e.g. "16 Go" -> 16)
    const extractNumber = (str) => {
        if (!str) return 0;
        const matches = str.toString().match(/(\d+)/);
        return matches ? parseInt(matches[0], 10) : 0;
    };

    // Helper to determine winners
    // type: 'min' (price) or 'max' (specs)
    const getWinnerId = (products, accessor, type = 'max') => {
        if (!products || products.length < 2) return null;
        
        let bestValue = type === 'min' ? Infinity : -Infinity;
        let winners = [];
        
        // First pass: find best value
        products.forEach(p => {
            const val = accessor(p);
            if (val <= 0) return; // Ignore invalid values 

            if (type === 'min') {
                if (val < bestValue) bestValue = val;
            } else {
                if (val > bestValue) bestValue = val;
            }
        });

        if (bestValue === Infinity || bestValue === -Infinity) return null;

        // Second pass: find all products with that value
        products.forEach(p => {
             const val = accessor(p);
             if (val === bestValue) winners.push(p.id);
        });

        // Only return winner if it's strictly better than others (not everyone is equal)
        // Actually, if 2 out of 3 match, highlight both. If all match, highlight none (tie).
        if (winners.length === products.length) return null; 

        return winners; // Return array of winning IDs
    };

    // Calculate Winners
    const priceWinners = getWinnerId(selectedProducts, getPrice, 'min');
    const ramWinners = getWinnerId(selectedProducts, p => extractNumber(p.specs?.ram));
    const storageWinners = getWinnerId(selectedProducts, p => extractNumber(p.specs?.storage));
    // CPU/GPU are harder to quantify without a benchmark database, so we skip for now.

    const isWinner = (id, winnersList) => winnersList && winnersList.includes(id);

    return (
        <div className="comparison-view-container">
            <header className="param-header">
                <div style={{display:'flex', gap:'15px'}}>
                    <button className="back-btn" onClick={onClose}>
                        <ArrowLeft size={24} />
                        <span>Back to Search</span>
                    </button>
                    
                    <button onClick={handleShare} className="share-btn">
                        <Link size={18} />
                        {copied ? "Link Copied!" : "Share Comparison"}
                    </button>
                </div>
                <h1>Comparing {selectedProducts.length} Products</h1>
            </header>

            <div className="compare-table-container full-screen">
                <table className="compare-table">
                    <thead>
                        <tr>
                            <th>Feature</th>
                            {selectedProducts.map(product => (
                                <th key={product.id}>
                                    <div className="th-product-header">
                                        <div style={{position: 'relative'}}>
                                             <img src={product.image} alt={product.title} />
                                             <button 
                                                className="remove-from-compare-x"
                                                onClick={() => removeFromCompare(product.id)}
                                                title="Remove from comparison"
                                             >
                                                <X size={14} />
                                             </button>
                                        </div>
                                        <span title={product.title}>{product.title.substring(0, 30)}...</span>
                                    </div>
                                </th>
                            ))}
                        </tr>
                    </thead>
                    <tbody>
                        {/* Price Row (Highlighted) */}
                        <tr className="price-row-table">
                            <td className="label">Price</td>
                            {selectedProducts.map(product => {
                                const price = getPrice(product);
                                const win = isWinner(product.id, priceWinners);
                                return (
                                    <td key={product.id} className={win ? "best-price" : ""}>
                                        {price.toFixed(3)} DT
                                        {win && <span className="best-deal-tag">Best Deal</span>}
                                    </td>
                                );
                            })}
                        </tr>
                        
                        {/* Specs Rows - auto-detect phone vs computer */}
                        {(() => {
                            const isPhone = selectedProducts.some(p =>
                                (p.specs?.category || p.category || '').toLowerCase() === 'smartphone'
                            );

                            return isPhone ? (
                                <>
                                {/* PHONE COMPARE: Store, CPU, RAM, Storage only */}
                                <tr>
                                    <td className="label">Store</td>
                                    {selectedProducts.map(product => (
                                        <td key={product.id}>
                                            <span className={`store-badge ${(product.source || '').toLowerCase()}`}>
                                                {product.source}
                                            </span>
                                        </td>
                                    ))}
                                </tr>
                                <tr>
                                    <td className="label">CPU</td>
                                    {selectedProducts.map(product => <td key={product.id}>{product.specs.cpu || '-'}</td>)}
                                </tr>
                                <tr>
                                    <td className="label">RAM</td>
                                    {selectedProducts.map(product => {
                                        const win = isWinner(product.id, ramWinners);
                                        return (
                                            <td key={product.id} className={win ? "winning-spec" : ""}>
                                                {product.specs.ram || '-'}
                                                {win && <Check size={14} className="win-icon" />}
                                            </td>
                                        );
                                    })}
                                </tr>
                                <tr>
                                    <td className="label">Storage</td>
                                    {selectedProducts.map(product => {
                                        const win = isWinner(product.id, storageWinners);
                                        return (
                                            <td key={product.id} className={win ? "winning-spec" : ""}>
                                                {product.specs.storage || '-'}
                                                {win && <Check size={14} className="win-icon" />}
                                            </td>
                                        );
                                    })}
                                </tr>
                                </>
                            ) : (
                                <>
                                {/* COMPUTER COMPARE: Full specs */}
                                <tr>
                                    <td className="label">Store</td>
                                    {selectedProducts.map(product => (
                                        <td key={product.id}>
                                            <span className={`store-badge ${(product.source || '').toLowerCase()}`}>
                                                {product.source}
                                            </span>
                                        </td>
                                    ))}
                                </tr>
                                <tr>
                                    <td className="label">Category</td>
                                    {selectedProducts.map(product => <td key={product.id}>{product.specs.category || '-'}</td>)}
                                </tr>
                                <tr>
                                    <td className="label">System (OS)</td>
                                    {selectedProducts.map(product => <td key={product.id}>{product.specs.os || '-'}</td>)}
                                </tr>
                                <tr>
                                    <td className="label">CPU</td>
                                    {selectedProducts.map(product => <td key={product.id}>{product.specs.cpu || '-'}</td>)}
                                </tr>
                                <tr>
                                    <td className="label">RAM</td>
                                    {selectedProducts.map(product => {
                                        const win = isWinner(product.id, ramWinners);
                                        return (
                                            <td key={product.id} className={win ? "winning-spec" : ""}>
                                                {product.specs.ram || '-'}
                                                {win && <Check size={14} className="win-icon" />}
                                            </td>
                                        );
                                    })}
                                </tr>
                                <tr>
                                    <td className="label">Storage</td>
                                    {selectedProducts.map(product => {
                                        const win = isWinner(product.id, storageWinners);
                                        return (
                                            <td key={product.id} className={win ? "winning-spec" : ""}>
                                                {product.specs.storage || '-'}
                                                {win && <Check size={14} className="win-icon" />}
                                            </td>
                                        );
                                    })}
                                </tr>
                                <tr>
                                    <td className="label">GPU</td>
                                    {selectedProducts.map(product => <td key={product.id}>{product.specs.gpu || '-'}</td>)}
                                </tr>
                                <tr>
                                    <td className="label">Screen</td>
                                    {selectedProducts.map(product => <td key={product.id}>{product.specs.screen || '-'}</td>)}
                                </tr>
                                <tr>
                                    <td className="label">Refresh Rate</td>
                                    {selectedProducts.map(product => {
                                        const val = product.specs.hz || "";
                                        const match = val.match(/(\d+)/);
                                        const hz = match ? parseInt(match[0]) : 0;
                                        const isBest = hz > 60;
                                        return (
                                            <td key={product.id} className={isBest ? "winning-spec" : ""}>
                                                {product.specs.hz || '-'}
                                                {isBest && <Check size={14} className="win-icon" />}
                                            </td>
                                        );
                                    })}
                                </tr>
                                </>
                            );
                        })()}
                        
                        {/* Action Row */}
                        <tr className="action-row">
                            <td></td>
                            {selectedProducts.map(product => (
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
    );
};

export default ComparisonView;
