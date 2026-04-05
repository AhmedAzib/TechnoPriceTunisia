import React, { useMemo } from 'react';
import { useParams, useNavigate, useSearchParams } from 'react-router-dom';
import { ArrowLeft, X, Scale, ChevronRight, Grid, List } from 'lucide-react';
import { MASTER_DATA } from './data/masterData';
import { normalizeProductData, generateVariantKey } from './utils/productUtils';
import ProductCard from './ProductCardItem';
import ComparisonView from './ComparisonView';
import { useWishlist } from './context/WishlistContext';
import { useCompare } from './context/CompareContext';
import './ProductsPage.css'; // Reuse existing styles

// --- REFACTORED: USE SHARED NORMALIZATION LOGIC ---
// This ensures consistency with productUtils.js fixes (Lesia, Storage checks, etc.)
const normalizedData = normalizeProductData(MASTER_DATA);
const normalizedMobileData = normalizedData.filter(p => {
    // Legacy filter to match MobilesPage somewhat, but strictly checking our new isMobileInput results via category/brand would be better.
    // However, productUtils returns the object. We can check the normalized 'category'.
    return p.specs.category === 'Smartphone' || p.specs.category === 'Mobile' || (p.title && p.title.toLowerCase().includes('smartphone'));
});


const MobileGroupDetailsPage = () => {
    const { groupKey } = useParams();
    const navigate = useNavigate();
    const [searchParams] = useSearchParams();
    const { wishlist, toggleWishlist, isInWishlist } = useWishlist();
    const { compareList, toggleCompare, addToCompare, isInCompare, removeFromCompare } = useCompare(); 
    
    // Decode key
    const decodedKey = decodeURIComponent(groupKey);

    // 1. Find all variants in normalizedMobileData
    // We must re-generate keys to match
    const allVariants = useMemo(() => {
        const rawGroup = normalizedMobileData.filter(p => generateVariantKey(p) === decodedKey);

        // --- CPU PROPAGATION LOGIC ---
        // Find the "Best" CPU in this group to fill gaps (User Request)
        let bestCpu = null;
        let maxRank = 0;

        const getCpuRank = (cpu) => {
            if (!cpu || cpu === "Unknown" || cpu === "Others" || cpu === "N/A") return 0; // Rank 0 (Worst)
            if (cpu === "Quad Core" || cpu === "Octa Core") return 1;    // Rank 1 (Generic)
            return 2; // Rank 2 (Specific Brand: Snapdragon, MediaTek, Unisoc, etc.)
        };

        rawGroup.forEach(p => {
             const rank = getCpuRank(p.specs.cpu);
             if (rank > maxRank) {
                 maxRank = rank;
                 bestCpu = p.specs.cpu;
             } else if (rank === maxRank && rank > 0 && !bestCpu) {
                 bestCpu = p.specs.cpu; // First valid/better one if tie
             }
        });

        // Apply best CPU to inferiors (Unknown/Others/Generic if better exists)
        return rawGroup.map(p => {
            const currentRank = getCpuRank(p.specs.cpu);
            if (bestCpu && currentRank < maxRank) {
                // Return new object with improved CPU
                return { 
                    ...p, 
                    specs: { 
                        ...p.specs, 
                        cpu: bestCpu 
                    } 
                };
            }
            return p;
        });
    }, [decodedKey]);

    const [isComparing, setIsComparing] = React.useState(false);
    const [mobileViewMode, setMobileViewMode] = React.useState('grid4'); // 'list' | 'grid2' | 'grid4'

    // --- DYNAMIC FILTERS STATE ---
    const [filters, setFilters] = React.useState({
        store: [],
        ram: [],
        storage: [],
        color: [] // Added Color
    });
    // Show results immediately on page load
    const [showResults, setShowResults] = React.useState(true);

    // --- DERIVED DATA ---
    const { displayedVariants, availableOptions } = useMemo(() => {
        // 1. Filter Logic
        const filtered = allVariants.filter(p => {
            if (filters.store.length > 0 && !filters.store.includes(p.source)) return false;
            if (filters.ram.length > 0 && !filters.ram.includes(p.specs.ram)) return false;
            if (filters.storage.length > 0 && !filters.storage.includes(p.specs.storage)) return false;
            if (filters.color.length > 0 && !filters.color.includes(p.specs.color)) return false;
            return true;
        });

        // 2. Extract Options
        const options = {
            store: [...new Set(allVariants.map(p => p.source))].filter(Boolean),
            ram: [...new Set(allVariants.map(p => p.specs.ram))].filter(Boolean),
            storage: [...new Set(allVariants.map(p => p.specs.storage))].filter(Boolean),
            color: [...new Set(allVariants.map(p => p.specs.color))].filter(Boolean)
        };

        return { displayedVariants: filtered, availableOptions: options };
    }, [allVariants, filters]);

    if (allVariants.length === 0) {
        return (
            <div style={{ padding: '50px', color: '#1A2B48', textAlign: 'center', background: '#E8F1F5', minHeight: '100vh' }}>
                <h2>Group Not Found</h2>
                <button onClick={() => navigate('/mobiles')} className="cta-button primary" style={{ marginTop: '20px' }}>Back to Mobiles</button>
            </div>
        );
    }

    const heroProduct = allVariants[0];

    const toggleFilter = (category, value) => {
        setShowResults(false);
        setFilters(prev => {
            const current = prev[category];
            const newValues = current.includes(value)
                ? current.filter(v => v !== value)
                : [...current, value];
            return { ...prev, [category]: newValues };
        });
    };

    return (
        <div style={{ minHeight: '100vh', backgroundColor: '#E8F1F5', padding: '40px 20px', color: '#1A2B48' }}>
            <div style={{ maxWidth: '1400px', margin: '0 auto' }}>
                
                {/* BACK BUTTON */}
                <button 
                    onClick={() => navigate('/mobiles')} 
                    style={{ 
                        background: 'transparent',
                        border: '1px solid #e2e8f0',
                        color: '#1A2B48',
                        padding: '10px 20px', 
                        borderRadius: '8px', 
                        cursor: 'pointer', 
                        display: 'flex', 
                        alignItems: 'center', 
                        gap: '8px', 
                        marginBottom: '20px',
                        fontSize: '1rem',
                        fontWeight: '600'
                    }}
                >
                    <ArrowLeft size={20} /> Back to Mobiles
                </button>

                {/* Header */}
                <div style={{ 
                    marginBottom: '40px', 
                    display: 'flex', 
                    gap: '30px', 
                    background: 'white',
                    padding: '30px',
                    borderRadius: '20px',
                    border: '1px solid #e2e8f0',
                    alignItems: 'center',
                    flexWrap: 'wrap'
                }}>
                    <div style={{
                        width: '200px',
                        height: '150px',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        background: '#f1f5f9',
                        borderRadius: '10px',
                        padding: '10px'
                    }}>
                        <img src={heroProduct.image} alt={decodedKey} style={{ maxWidth: '100%', maxHeight: '100%', objectFit: 'contain' }} />
                    </div>

                    <div style={{ flex: 1 }}>
                        <h1 style={{ fontSize: '2rem', fontWeight: 'bold', margin: '0 0 10px 0' }}>{decodedKey}</h1>
                        <p style={{ color: '#94a3b8', fontSize: '1.1rem' }}>
                            <span style={{color: '#1A2B48', fontWeight: 'bold'}}>{allVariants.length}</span> Variants Available 
                            <span style={{margin: '0 10px'}}>•</span>
                            Starting from <span style={{color: '#10b981', fontWeight: 'bold', fontSize: '1.3rem'}}>{heroProduct.price} TND</span>
                        </p>
                    </div>

                     <div style={{ display: 'flex', gap: '20px', color: '#cbd5e1' }}>
                        <div style={{ textAlign: 'center' }}>
                            <div style={{ fontSize: '0.8rem', color: '#64748b' }}>STORES</div>
                            <div style={{ fontWeight: 'bold' }}>{availableOptions.store.length}</div>
                        </div>
                        <div style={{ textAlign: 'center' }}>
                            <div style={{ fontSize: '0.8rem', color: '#64748b' }}>COLOR OPTIONS</div>
                            <div style={{ fontWeight: 'bold' }}>{availableOptions.color.length}</div>
                        </div>
                    </div>
                </div>

                {/* FILTERS (Horizontal Scroll) */}
                <div style={{ marginBottom: '20px' }}>
                    <div style={{ 
                        display: 'flex', 
                        overflowX: 'auto', 
                        gap: '10px', 
                        paddingBottom: '10px',
                        scrollbarWidth: 'none', 
                        msOverflowStyle: 'none'
                    }}>
                         <style>{`
                            ::-webkit-scrollbar { display: none; }
                        `}</style>
                        
                        {/* Reset Filter Pill */}
                        {(filters.store.length > 0 || filters.ram.length > 0 || filters.storage.length > 0 || filters.color.length > 0) && (
                            <button 
                                onClick={() => setFilters({ store: [], ram: [], storage: [], color: [] })}
                                style={{
                                    flex: '0 0 auto',
                                    padding: '8px 16px',
                                    borderRadius: '50px',
                                    border: '1px solid #ef4444',
                                    background: 'rgba(239, 68, 68, 0.1)',
                                    color: '#ef4444',
                                    fontWeight: 'bold',
                                    fontSize: '0.85rem',
                                    whiteSpace: 'nowrap',
                                    cursor: 'pointer'
                                }}
                            >
                                <X size={14} style={{ marginRight: '5px', verticalAlign: 'middle' }} />
                                Reset
                            </button>
                        )}

                        {[
                            { id: 'store', label: 'Store', options: availableOptions.store },
                            { id: 'ram', label: 'RAM', options: availableOptions.ram },
                            { id: 'storage', label: 'Storage', options: availableOptions.storage },
                            { id: 'color', label: 'Color', options: availableOptions.color }
                        ].map(group => (
                            group.options.map(opt => {
                                const isActive = filters[group.id].includes(opt);
                                return (
                                    <button 
                                        key={`${group.id}-${opt}`}
                                        onClick={() => toggleFilter(group.id, opt)}
                                        style={{
                                            flex: '0 0 auto',
                                            display: 'flex',
                                            alignItems: 'center',
                                            gap: '6px',
                                            background: isActive ? '#5F8D8B' : 'white',
                                            color: isActive ? 'white' : '#1A2B48',
                                            border: isActive ? 'none' : '1px solid #e2e8f0',
                                            borderRadius: '50px',
                                            padding: '8px 16px',
                                            fontSize: '0.85rem',
                                            fontWeight: isActive ? '600' : '400',
                                            cursor: 'pointer',
                                            whiteSpace: 'nowrap',
                                            transition: 'all 0.2s'
                                        }}
                                    >
                                        {/* Optional Icon based on category could go here */}
                                        {opt}
                                        {isActive && <X size={12} />}
                                    </button>
                                );
                            })
                        ))}
                    </div>
                </div>

                {/* CONFIRM BUTTON (Floating / Sticky if needed, or just inline) */}
                {!showResults && (
                    <div style={{ textAlign: 'center', padding: '40px', background: 'white', borderRadius: '20px', border: '1px dashed #e2e8f0' }}>
                        <button 
                            onClick={() => setShowResults(true)}
                            style={{ 
                                padding: '16px 40px', fontSize: '1.2rem', background: '#5F8D8B', color: 'white',
                                fontWeight: 'bold', border: 'none', borderRadius: '14px', cursor: 'pointer',
                                boxShadow: '0 0 30px rgba(95, 141, 139, 0.2)', transition: 'transform 0.2s',
                                display: 'inline-flex', alignItems: 'center', gap: '10px'
                            }}
                        >
                             Show Matches <span style={{ background: 'rgba(0,0,0,0.1)', padding: '2px 8px', borderRadius: '8px', fontSize: '0.9rem' }}>({displayedVariants.length})</span>
                        </button>
                    </div>
                )}

                {/* RESULTS GRID */}
                {showResults && (
                    <>
                        <div className="mobile-group-grid" style={{ 
                            display: 'grid', 
                            gridTemplateColumns: mobileViewMode === 'list' ? '1fr' : mobileViewMode === 'grid2' ? 'repeat(2, minmax(0, 1fr))' : 'repeat(4, minmax(0, 1fr))',
                            gap: '15px' 
                        }}>
                            {displayedVariants.sort((a,b) => a.price - b.price).map((product) => (
                                <ProductCard 
                                    key={product.id || product.link} 
                                    product={product} 
                                    addToCompare={toggleCompare}
                                    isInCompare={isInCompare(product.id)}
                                    toggleWishlist={toggleWishlist}
                                    isFavorite={isInWishlist(product.id)}
                                    // Pass formatting props if ProductCard supports them (it might likely handle its own responsive style)
                                    compact={mobileViewMode !== 'list'}
                                />
                            ))}
                        </div>
                        
                        {/* BOTTOM PADDING for Sticky Bar */}
                        <div style={{ height: '80px' }}></div>
                    </>
                )}

            </div>

            {/* --- MOBILE VIEW TOGGLE STRIP (Sticky Bottom) --- */}
            {showResults && (
                <div style={{
                    position: 'fixed',
                    bottom: '20px',
                    left: '50%',
                    transform: 'translateX(-50%)',
                    background: 'rgba(255, 255, 255, 0.95)',
                    backdropFilter: 'blur(10px)',
                    border: '1px solid #e2e8f0',
                    borderRadius: '50px',
                    padding: '10px 25px',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '20px',
                    zIndex: 1000,
                    boxShadow: '0 10px 30px rgba(0,0,0,0.1)'
                }}>
                    {['list', 'grid2', 'grid4'].map(mode => (
                        <button
                            key={mode}
                            onClick={() => setMobileViewMode(mode)}
                            style={{
                                background: mobileViewMode === mode ? '#5F8D8B' : 'transparent',
                                border: mobileViewMode === mode ? '1px solid #5F8D8B' : '1px solid #e2e8f0',
                                color: mobileViewMode === mode ? 'white' : '#1A2B48',
                                display: 'flex',
                                alignItems: 'center',
                                gap: '6px',
                                fontSize: '0.8rem',
                                fontWeight: '600',
                                cursor: 'pointer',
                                padding: '6px 12px',
                                borderRadius: '8px',
                                transition: '0.2s'
                            }}
                        >
                            {mode === 'list' ? <List size={16} /> : <Grid size={16} />}
                            <span>{mode === 'list' ? 'List' : mode === 'grid2' ? '2×2' : '4×4'}</span>
                        </button>
                    ))}
                    
                    <div style={{ width: '1px', height: '20px', background: '#e2e8f0' }}></div>

                    <div style={{ color: '#94a3b8', fontSize: '0.85rem' }}>
                        {displayedVariants.length} Items
                    </div>
                </div>
            )}

            {/* Comparison Overlay */}
            {/* Comparison Dock */}
            {compareList.length > 0 && !isComparing && (
                <div className="compare-dock">
                    <div className="dock-info">
                        <Scale size={20} color="#5F8D8B" />
                        <span>{compareList.length} Items</span>
                    </div>
                    
                    <div className="dock-thumbs">
                        {compareList.map(p => (
                            <div key={p.id} className="dock-thumb" onClick={() => removeFromCompare(p.id)}>
                                <img src={p.image} alt={p.title} />
                                <div className="dock-x">
                                    <X size={14}/>
                                </div>
                            </div>
                        ))}
                    </div>

                    <button 
                        className="compare-action-btn" 
                        onClick={() => navigate('/compare')}
                    >
                        Compare Now <ChevronRight size={16} />
                    </button>
                </div>
            )}

            {/* --- COMPARISON OVERLAY --- */}
            {isComparing && (
                <div style={{ position: 'fixed', inset: 0, zIndex: 9999, background: '#E8F1F5', overflowY: 'auto' }}>
                    <ComparisonView
                        selectedProducts={compareList} 
                        onClose={() => setIsComparing(false)}
                        removeFromCompare={removeFromCompare}
                    />
                </div>
            )}
        </div>
    );
};

export default MobileGroupDetailsPage;
