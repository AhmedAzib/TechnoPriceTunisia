import React, { useState } from 'react';
import { Heart, Scale, TrendingUp, Laptop } from 'lucide-react';
import StarRating from './StarRating';

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
const ProductCardItem = ({ product, addToCompare, toggleWishlist, isFavorite, isInCompare, isBestDeal, onShowHistory, isGroupCard, onGroupSelect, groupCount, onViewVariants, theme = 'dark' }) => {
    const [imageLoaded, setImageLoaded] = useState(false);
    const [imageError, setImageError] = useState(false);

    const isLight = theme === 'light';

    return (
        <div 
            className="product-card-glass" 
            style={{ 
                position: 'relative', 
                cursor: isGroupCard ? 'pointer' : 'default',
                background: isLight ? 'white' : '#0F172A',
                border: isLight ? '1px solid rgba(26, 43, 72, 0.05)' : '1px solid rgba(255, 255, 255, 0.05)',
                color: isLight ? '#1A2B48' : 'white',
                boxShadow: isLight ? '0 4px 15px rgba(26, 43, 72, 0.03)' : '0 4px 6px -1px rgba(0, 0, 0, 0.1)'
            }}
            onClick={(e) => {
                if (isGroupCard && onGroupSelect) {
                    onGroupSelect();
                }
            }}
        >
            {/* Steps 9 & 30: Badges - Separated for clean positioning */}
            <div className="tag" style={{
                position: 'absolute',
                top: 10,
                left: 10, /* MOVED TO LEFT (Was Right) to make room for Heart */
                zIndex: 10,
                background: (() => {
                    const s = (product.source || '').toLowerCase().trim();
                    if (s.includes('spacenet')) return '#10b981'; // Green
                    if (s.includes('mytek')) return '#ef4444';    // Red
                    if (s.includes('wiki')) return '#8b5cf6';     // Purple
                    if (s.includes('tdiscount')) return '#ff6b00'; // Orange
                    if (s.includes('skymil')) return '#3b82f6';   // Blue
                    if (s.includes('megapc')) return '#eab308';   // Yellow/Gold
                    if (s.includes('techspace')) return '#ec4899'; // Pink
                    if (s.includes('tunisiatech')) return '#06b6d4'; // Teal
                    if (s.includes('samsung')) return '#1428a0'; // Samsung Blue
                    if (s.includes('sbs')) return '#6366f1'; // SBS Informatique (Indigo)
                    return '#5F8D8B'; // Default (Sage Teal)
                })(),
                width: 'fit-content',
                maxWidth: '90%', /* Safety Cap */
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
            
            {/* Heart Button: MOVED TO TOP-RIGHT (User Request) */ }
            {/* Heart Button: MOVED TO TOP-RIGHT (User Request) */ }
            <button className="heart-btn mobile-heart-btn heart-top-right" onClick={(e) => {
                e.stopPropagation(); 
                toggleWishlist(product);
            }} style={{
                position: 'absolute',
                top: '5px',
                right: '5px', /* Top Right Corner */
                left: 'auto', /* CRITICAL: Override CSS left:12px */
                zIndex: 20,
                background: 'rgba(255,255,255,0.9)', /* Light background for visibility */
                borderRadius: '50%',
                border: 'none',
                width: '32px',
                height: '32px',
                padding: '0',
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                boxShadow: '0 2px 5px rgba(0,0,0,0.1)'
            }}>
                <Heart 
                    size={18} 
                    fill={isFavorite ? "#ef4444" : "none"} 
                    color={isFavorite ? "#ef4444" : "#1e293b"} /* Dark icon for contrast on white */
                    className="heart-icon"
                />
            </button>
            
            {isBestDeal && (
                <div className="best-price-badge" style={{
                    position: 'absolute',
                    top: 45, /* Below Store Badge (Left) */
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
                {(!imageLoaded) && (
                    <div className="img-loading-overlay" style={{
                        position: 'absolute', top:0, left:0, width:'100%', height:'100%',
                        display:'flex', justifyContent:'center', alignItems:'center',
                        zIndex: 1
                    }}>
                        <div className="spinner-loader" style={{
                                 width: '24px', height: '24px', 
                                 border: '3px solid rgba(255,255,255,0.1)', 
                                 borderTop: '3px solid #5F8D8B', 
                                 borderRadius: '50%', 
                                 animation: 'spin 0.8s linear infinite'
                        }}></div>
                    </div>
                )}

                {imageError && (
                    <div className="img-placeholder">
                        <Laptop size={48} color="#ef4444" />
                        <span style={{fontSize: '0.7rem', color: '#ef4444', marginTop: '4px'}}>Image N/A</span>
                    </div>
                )}
                {!imageError && (
                    <img 
                        src={product.image} 
                        alt={product.title} 
                        className={`product-image ${imageLoaded ? 'loaded' : ''}`}
                        loading="eager" 
                        referrerPolicy="no-referrer" 
                        onLoad={() => setImageLoaded(true)}
                        onError={() => { setImageError(true); setImageLoaded(true); }}
                        style={{ 
                            opacity: imageLoaded ? 1 : 0, 
                            transition: 'opacity 0.3s ease-in-out',
                            position: 'relative' 
                        }}
                    />
                )}
                
                {isGroupCard && groupCount > 0 && (
                    <div className="config-badge" style={{ 
                        position: 'absolute', bottom: '0', left: '0', 
                        background: 'rgba(0,0,0,0.6)', color: 'white', 
                        padding: '2px 6px', borderTopRightRadius: '6px', 
                        fontSize: '0.7rem', fontWeight: 'bold',
                        zIndex: 5,
                        backdropFilter: 'blur(4px)'
                    }}>
                        +{groupCount} Configs
                    </div>
                )}
            </div>
            
            <div className="product-card-glass-body" style={{ background: isLight ? 'white' : '#0F172A', color: isLight ? '#1A2B48' : 'white' }}>
                <div style={{display:'flex', justifyContent:'space-between', alignItems:'flex-start'}}>
                     <h3 className="product-title" title={product?.title} style={{ color: isLight ? '#1A2B48' : '#F1F5F9' }}>{product?.title ? product.title.substring(0, 50) + (product.title.length > 50 ? '...' : '') : 'Unknown Product'}</h3>
                </div>

                <div className="specs-list">
                    <div className="specs-mini" style={{ color: isLight ? '#64748b' : '#94A3B8' }}>
                        {(() => {
                            const cat = (product.specs && product.specs.category) || (product.category) || '';
                            const catLower = cat.toLowerCase();
                            const titleLower = (product.title || '').toLowerCase();
                            // BULLETPROOF: Check title for "Carte Mère" or "CARTE MERE" as ultimate fallback
                            const isMobo = catLower === 'motherboard' || catLower.includes('motherboard') || 
                                           catLower === 'carte mère' || catLower.includes('carte') || catLower.includes('board') ||
                                           titleLower.includes('carte mère') || titleLower.includes('carte mere') || titleLower.includes('motherboard');
                            if (catLower === 'cpu') {
                                return (
                                    <>
                                        {(product.specs && product.specs.cpu) || 'Unknown'} • 
                                        {(product.specs && product.specs.cores && product.specs.cores !== 'Unknown') ? ` ${product.specs.cores}` : ''} • 
                                        {(product.specs && product.specs.clock_speed && product.specs.clock_speed !== 'Unknown') ? ` ${product.specs.clock_speed}` : ''}
                                    </>
                                );
                            } else if (catLower === 'gpu') {
                                return (
                                    <>
                                        {/* Spot 1: Type (Chipset) */}
                                        {(product.specs && product.specs.gpu) || 'Unknown'} • 
                                        {/* Spot 2: VRAM */}
                                        {(product.specs && product.specs.vram) || 'Unknown'} • 
                                        {/* Spot 3: Target Resolution */}
                                        {(product.specs && product.specs.target_res) || 'Unknown'}
                                    </>
                                );
                            } else if (catLower === 'ram') {
                                // RAM: Capacity • Type • Speed (User Request - 10000% Safe)
                                return (
                                    <>
                                        {/* Spot 1: Capacity */}
                                        {(product.specs && product.specs.ram_capacity) || 'Unknown'} • 
                                        {/* Spot 2: Memory Type */}
                                        {(product.specs && product.specs.memory_type) || 'Unknown'} • 
                                        {/* Spot 3: Memory Speed */}
                                        {(product.specs && product.specs.ram_speed) || 'Unknown'}
                                    </>
                                );
                            } else if (isMobo) {
                                // MOTHERBOARD: Socket • Capacity • Speed (User Request - 10000% Safe)
                                return (
                                    <>
                                        {/* Spot 1: Socket Type (AM4, LGA 1700, AM5, etc.) */}
                                        {(product.specs && product.specs.socket) || 'Unknown'} • 
                                        {/* Spot 2: Memory Capacity */}
                                        {(product.specs && product.specs.memory_capacity) || 'N/A'} • 
                                        {/* Spot 3: Memory Speed */}
                                        {(product.specs && product.specs.memory_speed) || 'N/A'}
                                    </>
                                );
                            } else {
                                return (
                                    <>
                                        {(product.specs && product.specs.cpu) || 'Unknown'} • 
                                        {(product.specs && product.specs.ram) || 'Unknown'} • 
                                        {(product.specs && product.specs.storage) || 'Unknown'}
                                    </>
                                );
                            }
                        })()}
                    </div>
                </div>

                <div style={{ marginTop: '8px', marginBottom: '8px' }}>
                     <StarRating rating={product.rating} count={product.reviewCount} size={14} />
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
                                <span className="price">{typeof product?.price === 'number' ? product.price.toFixed(3) : (product?.price || '0.000')} DT</span>
                                {/* Step 39: Price/RAM Metric */}
                                {(() => {
                                    // Priority 1: Price / Core (For Processors)
                                    const coresStr = product.specs && product.specs.cores ? String(product.specs.cores) : '';
                                    const coreMatch = coresStr.match(/(\d+)/);
                                    
                                    if (coreMatch && product.price > 0) {
                                        const cores = parseInt(coreMatch[0]);
                                        if (cores > 0) {
                                            const perCore = (product.price / cores).toFixed(1);
                                            return (
                                                <div style={{display:'flex', alignItems:'center', gap:'4px', marginTop:'-2px'}}>
                                                    <span style={{fontSize:'9px', color: isLight ? '#64748b' : '#94A3B8'}}>{perCore} DT / Core</span>
                                                    <TrendingUp 
                                                        size={16} 
                                                        color="#3b82f6" 
                                                        strokeWidth={2.5}
                                                        style={{cursor:'pointer', opacity:1, marginLeft:'2px'}} 
                                                        onClick={(e) => {
                                                            e.preventDefault();
                                                            e.stopPropagation();
                                                            onShowHistory && onShowHistory(product);
                                                        }}
                                                        title="View Price History"
                                                    />
                                                </div>
                                            );
                                        }
                                    }

                                    // Priority 2: Price / GB (VRAM for GPUs)
                                    const vramStr = product.specs && product.specs.vram ? String(product.specs.vram).toLowerCase() : '';
                                    const vramMatch = vramStr.match(/(\d+)/);
                                    if (vramMatch && product.price > 0) {
                                         const vram = parseInt(vramMatch[0]);
                                         if (vram > 0) {
                                             const perGb = (product.price / vram).toFixed(1);
                                             return (
                                                 <div style={{display:'flex', alignItems:'center', gap:'4px', marginTop:'-2px'}}>
                                                     <span style={{fontSize:'9px', color: isLight ? '#64748b' : '#94A3B8'}}>{perGb} DT / GB</span>
                                                     <TrendingUp 
                                                         size={16} 
                                                         color="#3b82f6" 
                                                         strokeWidth={2.5}
                                                         style={{cursor:'pointer', opacity:1, marginLeft:'2px'}} 
                                                         onClick={(e) => {
                                                             e.preventDefault();
                                                             e.stopPropagation();
                                                             onShowHistory && onShowHistory(product);
                                                         }}
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
                                e.stopPropagation(); // Prevent double-firing navigation (Card + Button)
                                onViewVariants && onViewVariants();
                            }}
                            className="view-btn"
                            style={{ 
                                background: '#5F8D8B', 
                                color: 'white',
                                border: 'none',
                                cursor: 'pointer',
                                fontWeight: 'bold'
                            }}
                        >
                            View
                        </button>
                    ) : (
                        product.link ? (
                            <button 
                                onClick={(e) => {
                                    e.preventDefault();
                                    e.stopPropagation();
                                    window.open(product.link, '_blank');
                                }}
                                className="view-btn"
                                style={{ 
                                    background: '#F1F5F9', 
                                    color: '#0F172A', 
                                    border: 'none', 
                                    cursor: 'pointer', 
                                    fontWeight: 'bold',
                                    zIndex: 1000,
                                    position: 'relative'
                                }}
                            >
                                View
                            </button>
                        ) : (
                            <span 
                                className="view-btn" 
                                style={{ opacity: 0.5, cursor: 'not-allowed', background: '#e2e8f0' }}
                            >
                                N/A
                            </span>
                        )
                    )}
                </div>

                <div style={{ margin: '10px 0' }}>
                    <button 
                        className={`compare-add-btn ${isInCompare ? 'active' : ''}`} 
                        onClick={(e) => {
                            e.stopPropagation();
                            e.preventDefault();
                            addToCompare && addToCompare(product);
                        }}
                        style={{
                           background: isInCompare ? 'rgba(95, 141, 139, 0.2)' : (isLight ? '#F1F5F9' : 'rgba(255,255,255,0.05)'),
                           color: isInCompare ? '#2DD4BF' : (isLight ? '#1A2B48' : 'white'),
                           borderColor: isInCompare ? '#2DD4BF' : (isLight ? '#e2e8f0' : 'rgba(255,255,255,0.1)'),
                           position: 'relative',
                           zIndex: 20
                        }}
                    >
                       <Scale size={16} /> {isInCompare ? "Remove" : "+ Compare"}
                    </button>
                </div>
            </div>
        </div>
    );
};

export default ProductCardItem;
