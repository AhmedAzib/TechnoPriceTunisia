import React, { useState } from 'react';
import { Heart, Scale, TrendingUp, Laptop } from 'lucide-react';

// --- HELPER: STORE LOGO MAPPING (Step 37) ---
const getStoreLogo = (source) => {
    // Using SVG Data URIs to prevent console errors and ensure fast loading
    switch(source.toLowerCase()) {
        case 'tunisianet': 
            // Blue Text Logo
            return 'data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAyMDAgNjAiPjx0ZXh0IHg9IjEwIiB5PSI0MCIgZm9udC1mYW1pbHk9IkFyaWFsLCBzYW5zLXNlcmlmIiBmb250LXdlaWdodD0iYm9sZCIgZm9udC1zaXplPSIzMCIgZmlsbD0iIzAwNzBmZiI+VHVuaXNpYW5ldDwvdGV4dD48L3N2Zz4=';
        case 'spacenet': 
            // Green Text Logo
            return 'data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAyMDAgNjAiPjx0ZXh0IHg9IjEwIiB5PSI0MCIgZm9udC1mYW1pbHk9IkFyaWFsLCBzYW5zLXNlcmlmIiBmb250LXdlaWdodD0iYm9sZCIgZm9udC1zaXplPSIzMCIgZmlsbD0iIzEwYjk4MSI+U3BhY2VuZXQ8L3RleHQ+PC9zdmc+';
        case 'mytek': 
            // Red Text Logo
            return 'data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAyMDAgNjAiPjx0ZXh0IHg9IjEwIiB5PSI0MCIgZm9udC1mYW1pbHk9IkFyaWFsLCBzYW5zLXNlcmlmIiBmb250LXdlaWdodD0iYm9sZCIgZm9udC1zaXplPSIzNSIgZmlsbD0iI2VmNDQ0NCI+TXlUZWs8L3RleHQ+PC9zdmc+';
        case 'wiki': 
            // Purple Text Logo
            return 'data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAyMDAgNjAiPjx0ZXh0IHg9IjEwIiB5PSI0MCIgZm9udC1mYW1pbHk9IkFyaWFsLCBzYW5zLXNlcmlmIiBmb250LXdlaWdodD0iYm9sZCIgZm9udC1zaXplPSIzNSIgZmlsbD0iIzhINUNGNiI+V2lraTwvdGV4dD48L3N2Zz4=';
        default: return null;
    }
};

// --- PRODUCT CARD COMPONENT (Step 17) ---
const ProductCard = ({ product, addToCompare, toggleWishlist, isFavorite, isInCompare, isBestDeal, onShowHistory, isGroupCard, onGroupSelect, groupCount }) => {
    const [imageLoaded, setImageLoaded] = useState(false);
    const [imageError, setImageError] = useState(false);

    return (
        <div className="product-card-glass" style={{ position: 'relative' }}>
            {/* Steps 9 & 30: Badges - Separated for clean positioning */}
            <div className="tag" style={{
                position: 'absolute',
                top: 10,
                right: 10,
                zIndex: 10,
                background: (() => {
                    const s = (product.source || '').toLowerCase().trim();
                    if (s.includes('spacenet')) return '#10b981';
                    if (s.includes('mytek')) return '#ef4444'; 
                    if (s.includes('wiki')) return '#8b5cf6';
                    return '#00f2ff'; // Tunisianet
                })(),
                width: 'fit-content',
                padding: '3px 8px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                color: 'white', /* Ensure text is white */
                borderRadius: '4px',
                boxShadow: '0 2px 5px rgba(0,0,0,0.1)'
            }}>
                <span>
                    {product.source || 'Tunisianet'}
                </span>
            </div>
            
            {isBestDeal && (
                <div className="best-price-badge" style={{
                    position: 'absolute',
                    top: 40, /* Offset to avoid Heart overlap as requested */
                    left: 10,
                    zIndex: 10,
                    background: '#ff0055',
                    color: 'white',
                    fontSize: '10px',
                    fontWeight: 'bold',
                    padding: '4px 8px',
                    borderRadius: '12px',
                    boxShadow: '0 2px 4px rgba(0,0,0,0.2)',
                    width: 'fit-content',
                    animation: 'pulse 2s infinite'
                }}>
                    BEST PRICE
                </div>
            )}
            
            <div className="img-box">
                {(!imageLoaded || imageError) && (
                    <div className="img-placeholder">
                        <Laptop size={48} />
                        <span style={{fontSize: '0.7rem'}}>Loading...</span>
                    </div>
                )}
                {!imageError && (
                    <img 
                        src={product.image} 
                        alt={product.title} 
                        className={`product-image ${imageLoaded ? 'loaded' : ''}`}
                        loading="lazy"
                        onLoad={() => setImageLoaded(true)}
                        onError={() => { setImageError(true); setImageLoaded(true); }}
                        style={{ position: imageLoaded ? 'relative' : 'absolute' }}
                    />
                )}
                
                {/* Variant Count Badge for Groups */}
                {isGroupCard && groupCount > 0 && (
                    <div style={{ 
                        position: 'absolute', bottom: '10px', right: '10px', 
                        background: 'rgba(0,0,0,0.8)', color: 'white', 
                        padding: '4px 8px', borderRadius: '6px', 
                        fontSize: '0.75rem', fontWeight: 'bold',
                        border: '1px solid rgba(255,255,255,0.2)',
                        zIndex: 5
                    }}>
                        {groupCount} Configs
                    </div>
                )}
            </div>
            
            <div className="product-card-glass-body">
                {/* Brand Name Removed as per user request */}

                <div style={{display:'flex', justifyContent:'space-between', alignItems:'flex-start'}}>
                     <h3 className="product-title" title={product.title}>{product.title.substring(0, 50)}...</h3>
                     <button className="heart-btn" onClick={() => toggleWishlist(product)}>
                        <Heart 
                            size={18} 
                            fill={isFavorite ? "red" : "none"} 
                            color={isFavorite ? "red" : "black"} 
                        />
                    </button>
                </div>
                
                <div className="specs-list">
                    <div className="specs-mini">
                        {(product.specs && product.specs.cpu) || 'Unknown'} • 
                        {(product.specs && product.specs.ram) || 'Unknown'} • 
                        {(product.specs && product.specs.storage) || 'Unknown'}
                    </div>
                </div>

                <div className="price-row">
                    <div style={{display:'flex', flexDirection:'column'}}>
                         {/* Step 32: Stock Indicator */}
                         {(() => {
                             const isPreOrder = product.availability === 'on-order' || product.availability === 'pre-order';
                             const color = isPreOrder ? '#f59e0b' : '#10b981';
                             const text = isPreOrder ? 'Sur Commande' : 'En Stock';
                             
                             return (
                                 <div style={{fontSize:'0.7rem', color: color, display:'flex', alignItems:'center', gap:'4px', marginBottom:'2px'}}>
                                    <div style={{width:6, height:6, borderRadius:'50%', background:color}}></div> 
                                    {text}
                                 </div>
                             );
                         })()}
                         <div style={{display:'flex', alignItems:'center', gap:'6px'}}>
                             <div style={{display:'flex', flexDirection:'column'}}>
                                <span className="price">{typeof product.price === 'number' ? product.price.toFixed(3) : product.price} DT</span>
                                {/* Step 39: Price/RAM Metric */}
                                {(() => {
                                    const ramStr = product.specs && product.specs.ram ? String(product.specs.ram).toLowerCase() : '';
                                    const ramMatch = ramStr.match(/(\d+)/);
                                    if (ramMatch && product.price > 0) {
                                        const ram = parseInt(ramMatch[0]);
                                        if (ram > 0) {
                                            const perGb = (product.price / ram).toFixed(1);
                                            return (
                                                <div style={{display:'flex', alignItems:'center', gap:'4px', marginTop:'-2px'}}>
                                                    <span style={{fontSize:'9px', color:'#64748b'}}>{perGb} DT / GB</span>
                                                    <TrendingUp 
                                                        size={12} 
                                                        color="#3b82f6" 
                                                        style={{cursor:'pointer', opacity:0.8}} 
                                                        onClick={(e) => {
                                                            e.preventDefault();
                                                            e.stopPropagation();
                                                            onShowHistory && onShowHistory(product);
                                                        }}
                                                        onMouseOver={e => e.currentTarget.style.opacity = 1}
                                                        onMouseOut={e => e.currentTarget.style.opacity = 0.8}
                                                        title="View Price History"
                                                    />
                                                </div>
                                            );
                                        }
                                    }
                                    return null;
                                })()}
                             </div>
                             
                             {product.oldPrice && product.oldPrice > product.price && (
                                <span style={{
                                    background: 'rgba(255, 0, 85, 0.1)', 
                                    color: '#ff0055', 
                                    borderRadius:'4px', 
                                    padding:'0px 4px', 
                                    fontSize:'0.75rem', 
                                    fontWeight:'bold',
                                    border: '1px solid rgba(255, 0, 85, 0.2)',
                                    alignSelf: 'flex-start',
                                    marginTop: '4px'
                                }}>
                                    -{Math.round(((product.oldPrice - product.price) / product.oldPrice) * 100)}%
                                </span>
                             )}
                         </div>
                    </div>
                    {isGroupCard ? (
                        <button 
                            onClick={(e) => {
                                e.preventDefault();
                                onGroupSelect && onGroupSelect();
                            }}
                            className="view-btn"
                            style={{ 
                                background: '#00f2ff', 
                                color: 'black',
                                border: 'none',
                                cursor: 'pointer',
                                fontWeight: 'bold'
                            }}
                        >
                            Select
                        </button>
                    ) : (
                        <a href={product.link} target="_blank" rel="noopener noreferrer" className="view-btn">View</a>
                    )}
                </div>

                <div style={{ margin: '10px 0' }}>
                    <button 
                        className={`compare-add-btn ${isInCompare ? 'active' : ''}`} 
                        onClick={() => addToCompare && addToCompare(product)}
                        style={{
                           background: isInCompare ? 'rgba(0, 242, 255, 0.2)' : 'rgba(255,255,255,0.05)',
                           color: isInCompare ? '#00f2ff' : 'white',
                           borderColor: isInCompare ? '#00f2ff' : 'rgba(255,255,255,0.1)'
                        }}
                    >
                       <Scale size={16} /> {isInCompare ? "Remove" : "+ Compare"}
                    </button>
                </div>
            </div>
        </div>
    );
};

export default ProductCard;
