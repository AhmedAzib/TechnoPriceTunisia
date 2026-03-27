import React, { useState, useEffect } from 'react';
import { Smartphone, ArrowLeft, RefreshCw, Search, ArrowUpDown, Filter, Heart, Scale, Laptop } from 'lucide-react';
import { useNavigate, Link } from 'react-router-dom';
import './ProductsPage.css';
import pixelImage from './assets/pixel_9_pro.png';
import ProductCard from './ProductCard';
import FilterSection from './components/FilterSection';
import { useCompare } from './context/CompareContext';
import { useWishlist } from './context/WishlistContext';

// --- DATA SOURCE ---
import { MASTER_DATA } from './data/masterData';

import { generateVariantKey } from './utils/productUtils';

// Normalized Mobile Data
const normalizedMobileData = MASTER_DATA.filter(product => {
     // Robust filtering for mobiles
     const t = product.title.toLowerCase();
     const cat = product.category ? product.category.toLowerCase() : "";
     return cat === 'smartphone' || 
            cat === 'tablet' ||
            cat === 'feature phone' ||
            cat === 'mobile' ||
            t.includes('smartphone') || 
            t.includes('tablette') ||
            t.includes('iphone') || 
            t.includes('galaxy s') ||
            product.id.toString().includes('mob'); // Legacy ID check
}).map(p => {
    // Normalize Brand (Title Case)
    let brand = p.brand ? p.brand.trim() : "Unknown";
    // Fix common casing issues
    if (brand.toUpperCase() === 'INFINIX') brand = 'Infinix';
    if (brand.toUpperCase() === 'HONOR') brand = 'Honor';
    if (brand.toUpperCase() === 'Oppo') brand = 'Oppo';
    if (brand.toUpperCase() === 'XIAOMI') brand = 'Xiaomi';
    if (brand.toLowerCase() === 'xiomi') brand = 'Xiaomi'; // Fix typo if exists
    
    // Generic Title Case for others
    if (brand.length > 2 && brand === brand.toUpperCase()) {
         brand = brand.charAt(0).toUpperCase() + brand.slice(1).toLowerCase();
    }

    // Ensure specs exist locally for manipulation
    let specs = p.specs || {
        screen: "Unknown",
        storage: "Unknown",
        ram: "Unknown",
        camera: "Unknown",
        battery: "Unknown",
        os: "Android"
    };

    // Dictionary-based Screen Inference
    if (specs.screen === "Unknown") {
        const t = p.title.toLowerCase();
        
        // Manual Map for popular models
        if (t.includes('iphone 16 pro max') || t.includes('iphone 15 pro max') || t.includes('iphone 14 pro max')) specs.screen = '6.7"';
        else if (t.includes('iphone 16 plus') || t.includes('iphone 15 plus') || t.includes('iphone 14 plus')) specs.screen = '6.7"';
        else if (t.includes('iphone 16') || t.includes('iphone 15') || t.includes('iphone 14') || t.includes('iphone 13')) specs.screen = '6.1"';
        else if (t.includes('galaxy s24 ultra') || t.includes('galaxy s23 ultra')) specs.screen = '6.8"';
        else if (t.includes('galaxy s24+') || t.includes('galaxy s23+')) specs.screen = '6.7"';
        else if (t.includes('galaxy s24') || t.includes('galaxy s23')) specs.screen = '6.1"';
        else if (t.includes('galaxy a06') || t.includes('galaxy a05') || t.includes('galaxy a16') || t.includes('galaxy a15') || t.includes('galaxy a25')) specs.screen = '6.7"';
        else if (t.includes('galaxy a55') || t.includes('galaxy a35') || t.includes('galaxy a54') || t.includes('galaxy a34')) specs.screen = '6.6"';
        else if (t.includes('galaxy a')) specs.screen = '6.5"'; // Generic A series
        else if (t.includes('redmi note 13') || t.includes('redmi note 12')) specs.screen = '6.67"';
        else if (t.includes('redmi a3') || t.includes('redmi a2')) specs.screen = '6.7"';
        else if (t.includes('redmi 13') || t.includes('redmi 12')) specs.screen = '6.79"';
        else if (t.includes('infinix note') || t.includes('infinix hot')) specs.screen = '6.78"';
        else if (t.includes('infinix smart')) specs.screen = '6.6"';
        else if (t.includes('tecno spark') || t.includes('tecno pop')) specs.screen = '6.6"';
        else if (t.includes('itel')) specs.screen = '6.5"'; // Most itels are big now
        else if (t.includes('lesia')) specs.screen = '6.5"'; // Budget phones usually 6.5
        else if (t.includes('oppo reno')) specs.screen = '6.7"';
        else if (t.includes('oppo a')) specs.screen = '6.56"';
        else if (t.includes('realme c')) specs.screen = '6.74"';
        else if (t.includes('realme 11') || t.includes('realme 12')) specs.screen = '6.7"';
        
        // Regex Fallback (Keep as secondary)
        if (specs.screen === "Unknown") {
             const titleUpper = p.title.toUpperCase();
             const screenMatch = titleUpper.match(/(\d+\.\d+|\d+)\s*(?:PO|INCH|''|")|ECRAN\s*(\d+\.\d+)/);
             if (screenMatch) {
                  const size = screenMatch[1] || screenMatch[2];
                  specs.screen = size + '"';
             }
        }
    }
    
    // Robust Fallback for Unknown Specs (Existing Storage Logic)
    if (specs.storage === "Unknown" || specs.storage === "0GB") {
        const titleUpper = p.title.toUpperCase();
        const matches = titleUpper.match(/(\d+)\s*(?:GO|GB|G|TO|TB)/g);
        
        if (matches) {
            // Parse numbers. Handle 1TB=1024GB if needed, for now just numbers.
            const values = matches.map(m => {
                const num = parseInt(m.match(/\d+/)[0]);
                if (m.includes('T')) return num * 1024;
                return num;
            }).sort((a, b) => b - a); // Descending (Storage usually > RAM)
            
            if (values.length > 0) {
                // Largest is Storage
                let storageVal = values[0];
                specs.storage = storageVal >= 1000 ? (storageVal/1024) + "TB" : storageVal + "GB";
                
                // Second largest might be RAM if RAM is unknown
                if ((specs.ram === "Unknown" || !specs.ram) && values.length > 1) {
                    specs.ram = values[1] + "GB";
                }
            }
        }
        // Specific fix for user mention "capasite stockage" if it appears in raw attributes (unlikely based on file view but harmless)
    }

    return {
        ...p,
        brand: brand,
        specs: specs
    };
});

const MobilesPage = () => {
    const navigate = useNavigate();
    
    // Hooks for Card Logic
    const { addToCompare, removeFromCompare, compareList, isInCompare } = useCompare();
    const { wishlist, toggleWishlist, isInWishlist } = useWishlist();

    // State
    const [products, setProducts] = useState(normalizedMobileData);
    const [filteredProducts, setFilteredProducts] = useState(normalizedMobileData);
    const [searchQuery, setSearchQuery] = useState('');
    const [priceRange, setPriceRange] = useState({ min: 0, max: 10000 });
    const [viewFavorites, setViewFavorites] = useState(false);
    const [isGroupView, setIsGroupView] = useState(false);

    // Scroll to Top on Mount
    useEffect(() => {
        window.scrollTo(0, 0);
    }, []);
    
    // Filters State
    const [filters, setFilters] = useState({
        brand: [],
        storage: [],
        ram: [],
        screen: []
    });

    // Helper to get Counts
    const getCounts = (key) => {
        const counts = {};
        normalizedMobileData.forEach(p => {
            const val = key === 'brand' ? p.brand : (p.specs[key] || 'Unknown');
            counts[val] = (counts[val] || 0) + 1;
        });
        return counts;
    };

    // Filter Options
    const filterOptions = {
        brand: [...new Set(normalizedMobileData.map(p => p.brand))].sort(),
        storage: [...new Set(normalizedMobileData.map(p => p.specs.storage))].sort(),
        ram: [...new Set(normalizedMobileData.map(p => p.specs.ram))].sort(),
        screen: [...new Set(normalizedMobileData.map(p => p.specs.screen))].sort()
    };

    // Toggle Filter Handler
    const toggleFilter = (key, value) => {
        setFilters(prev => {
            const current = prev[key];
            const updated = current.includes(value) 
                ? current.filter(i => i !== value)
                : [...current, value];
            return { ...prev, [key]: updated };
        });
    };

    // Reset Handlers
    const resetAll = () => {
        setFilters({ brand: [], storage: [], ram: [], screen: [] });
        setPriceRange({ min: 0, max: 10000 });
        setSearchQuery('');
    };

    // Filter Logic
    useEffect(() => {
        let result = normalizedMobileData;

        // 0. Wishlist Filter
        if (viewFavorites) {
             const wishlistIds = wishlist.map(w => w.id);
             result = result.filter(p => wishlistIds.includes(p.id));
        }

        // Brand
        if (filters.brand.length > 0) {
            result = result.filter(p => filters.brand.includes(p.brand));
        }
        
        // Specs
        ['storage', 'ram', 'screen'].forEach(key => {
            if (filters[key].length > 0) {
                result = result.filter(p => filters[key].includes(p.specs[key]));
            }
        });

        // Price
        result = result.filter(p => p.price >= priceRange.min && p.price <= priceRange.max);

        // Search
        if (searchQuery) {
            const q = searchQuery.toLowerCase();
            result = result.filter(p => 
                p.title.toLowerCase().includes(q) || 
                p.brand.toLowerCase().includes(q)
            );
        }

        // Grouping Logic
        if (isGroupView) {
            const groups = {};
            result.forEach(p => {
                 const key = generateVariantKey(p);
                 if (!groups[key]) {
                     groups[key] = {
                         ...p,
                         key,
                         baseProduct: p,
                         variants: [],
                         minPrice: p.price,
                         id: `group-${key}`,
                         isGroup: true
                     };
                 }
                 groups[key].variants.push(p);
                 
                 // Keep lowest price as face
                 if (p.price < groups[key].minPrice) {
                     groups[key].minPrice = p.price;
                     groups[key].baseProduct = p;
                     groups[key].price = p.price;
                     groups[key].image = p.image;
                     groups[key].title = p.title;
                 }
            });
            result = Object.values(groups);
        }

        setProducts(result);
    }, [filters, priceRange, searchQuery, viewFavorites, isGroupView, wishlist]);

    return (
        <div className="products-layout-final" style={{
            display: 'grid',
            gridTemplateColumns: '240px 1fr',
            minHeight: '100vh',
            backgroundColor: '#02040a',
            backgroundImage: `radial-gradient(circle at 15% 50%, rgba(56, 189, 248, 0.08) 0%, transparent 25%), 
                              radial-gradient(circle at 85% 30%, rgba(168, 85, 247, 0.08) 0%, transparent 25%)`,
            color: '#e2e8f0',
            fontFamily: "'Inter', sans-serif"
        }}>
            {/* SIDEBAR */}
            <aside className="sidebar">
                <div className="sidebar-header" style={{ padding: '20px', borderBottom: '1px solid rgba(255,255,255,0.05)' }}>
                    <button onClick={() => navigate('/')} style={{ background: 'none', border: 'none', color: 'white', display: 'flex', alignItems: 'center', gap: '8px', cursor: 'pointer', fontSize: '1rem', fontWeight: 'bold' }}>
                        <ArrowLeft size={18} /> Back Home
                    </button>
                </div>

                <div className="filter-header-row" style={{ padding: '15px 20px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <h3 style={{ margin: 0, fontSize: '0.8rem', textTransform: 'uppercase', letterSpacing: '1px', color: '#64748b' }}>Filters</h3>
                    <button onClick={resetAll} className="reset-btn"><RefreshCw size={14} /> Reset</button>
                </div>

                <div className="scroll-filters" style={{ flex: 1, overflowY: 'auto' }}>
                     <FilterSection title="Price Range" isOpen={true}>
                        <div className="price-inputs">
                            <input type="number" value={priceRange.min} onChange={(e) => setPriceRange({...priceRange, min: Number(e.target.value)})} />
                            <span>to</span>
                            <input type="number" value={priceRange.max} onChange={(e) => setPriceRange({...priceRange, max: Number(e.target.value)})} />
                        </div>
                    </FilterSection>

                    <FilterSection title="Brand" options={filterOptions.brand} selected={filters.brand} onSelect={(v) => toggleFilter('brand', v)} isOpen={true} counts={getCounts('brand')} />
                    <FilterSection title="Storage" options={filterOptions.storage} selected={filters.storage} onSelect={(v) => toggleFilter('storage', v)} counts={getCounts('storage')} />
                    <FilterSection title="RAM" options={filterOptions.ram} selected={filters.ram} onSelect={(v) => toggleFilter('ram', v)} counts={getCounts('ram')} />
                    <FilterSection title="Screen Size" options={filterOptions.screen} selected={filters.screen} onSelect={(v) => toggleFilter('screen', v)} counts={getCounts('screen')} />
                </div>
            </aside>

            {/* MAIN CONTENT */}
            <main className="products-main" style={{ padding: '40px' }}>
                <div className="products-header" style={{ marginBottom: '30px' }}>
                    <h1 style={{ fontSize: '2.5rem', fontWeight: 'bold', background: 'linear-gradient(to right, #fff, #94a3b8)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent', margin: 0 }}>
                        Mobile Marketplace
                    </h1>
                    <p style={{ color: '#00f2ff', marginTop: '5px' }}>
                        Active Items: {products.length} • Latest Smartphones
                    </p>
                </div>

                <div className="top-toolbar" style={{ display: 'flex', gap: '20px', marginBottom: '30px', paddingBottom: '20px', borderBottom: '1px solid rgba(255,255,255,0.05)' }}>
                    <div className="search-box" style={{ flex: 1,  background: 'rgba(30, 41, 59, 0.3)', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '8px', padding: '10px 15px', display: 'flex', alignItems: 'center', gap: '10px' }}>
                        <Search size={18} color="#94a3b8" />
                        <input 
                            type="text" 
                            placeholder="Search phones..." 
                            value={searchQuery}
                            onChange={(e) => setSearchQuery(e.target.value)}
                            style={{ background: 'transparent', border: 'none', color: 'white', width: '100%', outline: 'none' }}
                        />
                    </div>

                    {/* Group Toggle */}
                    <button 
                        onClick={() => setIsGroupView(!isGroupView)}
                        style={{
                            background: isGroupView ? '#00f2ff' : 'rgba(30, 41, 59, 0.3)',
                            color: isGroupView ? '#000' : '#fff',
                            border: '1px solid rgba(255,255,255,0.1)',
                            borderRadius: '8px',
                            padding: '0 15px',
                            cursor: 'pointer',
                            fontWeight: '600',
                            display: 'flex',
                            alignItems: 'center',
                            gap: '8px',
                            transition: 'all 0.3s ease'
                        }}
                    >
                        {isGroupView ? <Scale size={18} /> : <Laptop size={18} />}
                        {isGroupView ? "Ungroup" : "Group"}
                    </button>

                    {/* Favorites Toggle */}
                     <button 
                        onClick={() => setViewFavorites(!viewFavorites)}
                        style={{
                            display: 'flex',
                            alignItems: 'center',
                            gap: '8px',
                            background: viewFavorites ? '#ff0055' : 'rgba(255,255,255,0.1)',
                            color: viewFavorites ? 'white' : '#cbd5e1',
                            border: 'none',
                            padding: '8px 16px',
                            borderRadius: '8px',
                            cursor: 'pointer',
                            fontWeight: '600',
                            transition: 'all 0.3s ease'
                        }}
                     >
                        <Heart size={18} fill={viewFavorites ? "white" : "none"} />
                        {viewFavorites ? "Show All" : "Show Favorites"}
                     </button>
                </div>

                {products.length === 0 ? (
                    <div className="empty-state" style={{ textAlign: 'center', padding: '60px', color: '#64748b' }}>
                        <h2>No phones found</h2>
                        <button onClick={resetAll} style={{ marginTop: '20px', padding: '10px 20px', background: '#00f2ff', border: 'none', borderRadius: '8px', cursor: 'pointer', fontWeight: 'bold' }}>
                            Clear Filters
                        </button>
                    </div>
                ) : (
                    <div className="grid" style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(240px, 1fr))', gap: '20px' }}>
                        {products.map(product => (
                            <ProductCard 
                                key={product.id}
                                product={product}
                                addToCompare={addToCompare}
                                toggleWishlist={toggleWishlist}
                                isInCompare={isInCompare(product.id)}
                                isFavorite={isInWishlist(product.id)}
                                isGroupCard={product.isGroup}
                                groupCount={product.variants?.length}
                                onGroupSelect={() => navigate(`/group/${product.key}`)}
                            />
                        ))}
                    </div>
                )}
            </main>
        </div>
    );
};

export default MobilesPage;
