import React, { useMemo } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeft } from 'lucide-react';
import { MASTER_DATA } from './data/masterData';
import { normalizeProductData, generateVariantKey } from './utils/productUtils';
import ProductCard from './ProductCard';
import { useWishlist } from './context/WishlistContext';
import { useCompare } from './context/CompareContext';
import './ProductsPage.css'; // Reuse existing styles

const GroupDetailsPage = () => {
    const { groupKey } = useParams();
    const navigate = useNavigate();
    const { wishlist, toggleWishlist } = useWishlist();
    const { compareList, toggleCompare, isInCompare } = useCompare();

    // Decode key
    const decodedKey = decodeURIComponent(groupKey);

    // Normalize Data (Consistently with ProductsPage)
    const products = useMemo(() => normalizeProductData(MASTER_DATA), []);

    // Filter Group Variants (All available items in this group)
    const allVariants = useMemo(() => {
        return products.filter(p => generateVariantKey(p) === decodedKey)
            .sort((a, b) => a.price - b.price); // Cheapest first
    }, [products, decodedKey]);

    // --- DYNAMIC FILTERS STATE ---
    const [filters, setFilters] = React.useState({
        store: [],
        ram: [],
        storage: [],
        cpu: []
    });

    // --- DERIVED DATA: AVAILABLE OPTIONS & FILTERED LIST ---
    const { displayedVariants, availableOptions } = useMemo(() => {
        // 1. Filter Logic
        const filtered = allVariants.filter(p => {
            if (filters.store.length > 0 && !filters.store.includes(p.source)) return false;
            if (filters.ram.length > 0 && !filters.ram.includes(p.specs.ram)) return false;
            if (filters.storage.length > 0 && !filters.storage.includes(p.specs.storage)) return false;
            if (filters.cpu.length > 0 && !filters.cpu.includes(p.specs.cpu)) return false;
            return true;
        });

        // 2. Extract Options from ALL variants (to build the filter menu)
        const options = {
            store: [...new Set(allVariants.map(p => p.source))].filter(Boolean),
            ram: [...new Set(allVariants.map(p => p.specs.ram))].filter(Boolean),
            storage: [...new Set(allVariants.map(p => p.specs.storage))].filter(Boolean),
            cpu: [...new Set(allVariants.map(p => p.specs.cpu))].filter(Boolean)
        };

        return { displayedVariants: filtered, availableOptions: options };
    }, [allVariants, filters]);

    // Handle "Not Found" case
    if (allVariants.length === 0) {
        return (
            <div style={{ padding: '50px', color: '#1A2B48', textAlign: 'center' }}>
                <h2>Group Not Found</h2>
                <button onClick={() => navigate('/products')} className="cta-button primary">Back to Products</button>
            </div>
        );
    }

    // Symbolic Product (The "Hero" - usually the cheapest)
    const heroProduct = allVariants[0];

    const toggleFilter = (category, value) => {
        setFilters(prev => {
            const current = prev[category];
            const newValues = current.includes(value)
                ? current.filter(v => v !== value)
                : [...current, value];
            return { ...prev, [category]: newValues };
        });
    };

    return (
        <div style={{ minHeight: '100vh', backgroundColor: '#E8F1F5', padding: '120px 20px 40px', color: '#1A2B48' }}>
            <div style={{ maxWidth: '1400px', margin: '0 auto' }}>
                
                {/* Header / Symbolic Computer */}
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
                    {/* Image */}
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

                    {/* Info */}
                    <div style={{ flex: 1 }}>
                        <button 
                            onClick={() => navigate(-1)} 
                            style={{ background: 'none', border: 'none', color: '#94a3b8', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '5px', marginBottom: '10px' }}
                        >
                            <ArrowLeft size={16} /> Back to Search
                        </button>
                        <h1 style={{ fontSize: '2rem', fontWeight: 'bold', margin: '0 0 10px 0' }}>{decodedKey}</h1>
                        <p style={{ color: '#94a3b8', fontSize: '1.1rem' }}>
                            <span style={{color: '#1A2B48', fontWeight: 'bold'}}>{allVariants.length}</span> Variants Available 
                            <span style={{margin: '0 10px'}}>•</span>
                            Starting from <span style={{color: '#10b981', fontWeight: 'bold', fontSize: '1.3rem'}}>{heroProduct.price} TND</span>
                        </p>
                    </div>

                    {/* Quick Stats (Optional) */}
                    <div style={{ display: 'flex', gap: '20px', color: '#cbd5e1' }}>
                        <div style={{ textAlign: 'center' }}>
                            <div style={{ fontSize: '0.8rem', color: '#64748b' }}>STORES</div>
                            <div style={{ fontWeight: 'bold' }}>{availableOptions.store.length}</div>
                        </div>
                        <div style={{ textAlign: 'center' }}>
                            <div style={{ fontSize: '0.8rem', color: '#64748b' }}>CPU OPTIONS</div>
                            <div style={{ fontWeight: 'bold' }}>{availableOptions.cpu.length}</div>
                        </div>
                    </div>
                </div>

                {/* --- DYNAMIC FILTER BAR --- */}
                {/* Only show filters if there are actually options to filter by! */}
                <div style={{ marginBottom: '30px', display: 'flex', gap: '15px', flexWrap: 'wrap' }}>
                    
                    {/* Helper to render a filter group */}
                    {[
                        { id: 'store', label: 'Store', options: availableOptions.store },
                        { id: 'ram', label: 'RAM', options: availableOptions.ram },
                        { id: 'storage', label: 'Storage', options: availableOptions.storage },
                        { id: 'cpu', label: 'CPU', options: availableOptions.cpu }
                    ].map(group => (
                        group.options.length > 1 && (
                            <div key={group.id} style={{ display: 'flex', alignItems: 'center', gap: '10px', background: 'white', padding: '5px 15px', borderRadius: '50px' }}>
                                <span style={{ fontSize: '0.8rem', color: '#64748b', textTransform: 'uppercase', fontWeight: 'bold' }}>{group.label}</span>
                                <div style={{ display: 'flex', gap: '5px' }}>
                                    {group.options.map(opt => {
                                        const isActive = filters[group.id].includes(opt);
                                        return (
                                            <button 
                                                key={opt}
                                                onClick={() => toggleFilter(group.id, opt)}
                                                style={{
                                                    background: isActive ? '#5F8D8B' : '#f1f5f9',
                                                    color: isActive ? 'white' : '#1A2B48',
                                                    border: 'none',
                                                    borderRadius: '20px',
                                                    padding: '4px 12px',
                                                    fontSize: '0.8rem',
                                                    cursor: 'pointer',
                                                    transition: '0.2s'
                                                }}
                                            >
                                                {opt}
                                            </button>
                                        );
                                    })}
                                </div>
                            </div>
                        )
                    ))}
                    
                    {/* Clear Filters */}
                    {(filters.store.length > 0 || filters.ram.length > 0 || filters.storage.length > 0 || filters.cpu.length > 0) && (
                        <button 
                            onClick={() => setFilters({ store: [], ram: [], storage: [], cpu: [] })}
                            style={{ background: 'none', border: 'none', color: '#ef4444', cursor: 'pointer', fontSize: '0.85rem', textDecoration: 'underline' }}
                        >
                            Reset Filters
                        </button>
                    )}
                </div>

                {/* Grid */}
                <div style={{
                    display: 'grid',
                    gridTemplateColumns: 'repeat(4, 1fr)', // Consistent 4-col layout
                    gap: '20px'
                }}>
                    {displayedVariants.map(product => (
                        <ProductCard 
                            key={product.id || product.link} 
                            product={product} 
                            isFavorite={wishlist.some(w => w.id === product.id)}
                            toggleWishlist={toggleWishlist}
                            addToCompare={toggleCompare}
                            isInCompare={isInCompare(product.id)}
                            isBestDeal={false}
                            onShowHistory={() => {}}
                        />
                    ))}
                </div>
                
                {displayedVariants.length === 0 && (
                    <div style={{ padding: '50px', textAlign: 'center', color: '#64748b' }}>
                        No variants match your filters.
                    </div>
                )}

            </div>
        </div>
    );
};

export default GroupDetailsPage;
