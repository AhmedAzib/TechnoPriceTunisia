import React, { useState, useEffect } from 'react';
import { Smartphone, ArrowLeft, RefreshCw, Search, ArrowUpDown, Filter, Heart, Scale, Laptop, ChevronRight, ChevronDown, X, Menu, Home, Cpu, Monitor, CircuitBoard, Server, Grid, List } from 'lucide-react';
import { useNavigate, Link } from 'react-router-dom';
import './ProductsPage.css';
import './spinner.css';
import pixelImage from './assets/pixel_9_pro.png';
import ProductCard from './ProductCardItem';
import FilterSection from './components/FilterSection';
import { useCompare } from './context/CompareContext';
import { useWishlist } from './context/WishlistContext';
import { MASTER_DATA } from './data/masterData';
import { normalizeProductData, generateVariantKey } from './utils/productUtils';
import CompareModal from './CompareModal';
import ComparisonView from './ComparisonView';
import Footer from './Footer';

// Normalized Mobile Data
// Uses shared normalizeProductData for consistency with GroupDetails and Strict Rules.
const allNormalizedData = normalizeProductData(MASTER_DATA);

const normalizedMobileData = allNormalizedData.filter(product => {
     if (!product) return false;

     // 1. Category-based: Only smartphones
     const category = product.specs?.category || product.category || '';
     const catLower = category.toLowerCase();

     if (catLower === 'smartphone') {
         return true;
     }

     // 2. Fallback - Check title for phone-related terms only
     const t = (product.title || '').toLowerCase();

     return t.includes('smartphone') ||
            t.includes('iphone') ||
            t.includes('galaxy s') ||
            t.includes('galaxy a') ||
            t.includes('galaxy z') ||
            t.includes('redmi') ||
            t.includes('poco') ||
            t.includes('oppo') ||
            t.includes('realme') ||
            t.includes('infinix') ||
            t.includes('tecno') ||
            t.includes('itel') ||
            t.includes('honor') ||
            t.includes('pixel');
}).filter(p => {
    // Exclude non-phone items (safety net)
    const t = (p.title || '').toLowerCase();
    if (t.includes('laptop') || t.includes('portable') || t.includes('notebook') ||
        t.includes('desktop') || t.includes('macbook') || t.includes('pc ') ||
        t.includes('tablette') || t.includes('tablet') || t.includes('smartwatch') ||
        t.includes('bracelet') || t.includes('cable') || t.includes('chargeur') ||
        t.includes('coque') || t.includes('protection') || t.includes('housse') ||
        t.includes('etui') || t.includes('accessoire') || t.includes('casque') ||
        t.includes('bicyclette') || t.includes('tv') || t.includes('refrigerateur') ||
        t.includes('montre') || t.includes('imprimante') || t.includes('ecran')) return false;
    return true;
});

// --- HELPER: Screen Classing (New UX) ---
const getClassedSize = (sizeStr) => {
    if (!sizeStr || sizeStr === "Unknown") return "Unknown";
    const match = sizeStr.toString().match(/(\d+\.?\d*)/);
    if (!match) return "Unknown";
    const size = parseFloat(match[1]);
    
    // Compact: < 6.1"
    if (size < 6.1) return "Compact (< 6.1\")";
    // Standard: 6.1" - 6.6"
    if (size >= 6.1 && size <= 6.6) return "Standard (6.1\" - 6.6\")";
    // Large: > 6.6"
    return "Large / Phablet (> 6.6\")";
};

const MobilesPage = () => {
    const navigate = useNavigate();
    const [showMobileMenu, setShowMobileMenu] = useState(false);
    const [isMobile, setIsMobile] = useState(window.innerWidth <= 1024);
    const sidebarWidth = isMobile ? '0' : '260px';

    useEffect(() => {
        const handleResize = () => setIsMobile(window.innerWidth <= 1024);
        window.addEventListener('resize', handleResize);
        return () => window.removeEventListener('resize', handleResize);
    }, []);
    
    // Hooks for Card Logic
    const { addToCompare, removeFromCompare, compareList, isInCompare, setCompareList } = useCompare();

    // Toggle Filter Handler
    // ... (previous filter code)

    // --- SMART WISHLIST HANDLER (Fix for stuck groups) ---
    const { wishlist, toggleWishlist, isInWishlist, removeMultipleFromWishlist } = useWishlist();

    const handleToggleWishlist = (product) => {
        // 1. If it's a Group Card
        if (product.isGroup) {
            // Check if ANY part of this group is in wishlist
            const isGroupHearted = isInWishlist(product.id);
            const isVariantHearted = product.variants && product.variants.some(v => isInWishlist(v.id));
            
            // If it appears Red (Hearted) -> We want to UNHEART everything
            if (isGroupHearted || isVariantHearted) {
                const idsToRemove = [product.id]; // Remove Group ID
                if (product.variants) {
                    product.variants.forEach(v => idsToRemove.push(v.id)); // Remove ALL Variant IDs
                }
                removeMultipleFromWishlist(idsToRemove);
            } else {
                // If it's Grey -> Heart just the Group
                toggleWishlist(product);
            }
        } 
        // 2. If it's a regular card (shouldn't happen on main page given current logic, but safe fallback)
        else {
            toggleWishlist(product);
        }
    };


    const toggleCompare = (product) => {
        if (isInCompare(product.id)) {
            removeFromCompare(product.id);
        } else {
            addToCompare(product);
        }
    };

    // State
    const [products, setProducts] = useState(normalizedMobileData);
    const [filteredProducts, setFilteredProducts] = useState(normalizedMobileData);
    const [searchQuery, setSearchQuery] = useState('');
    const [sortOption, setSortOption] = useState("default"); // Added Sort State
    const [priceRange, setPriceRange] = useState({ min: 0, max: 20000 });
    const [viewFavorites, setViewFavorites] = useState(false);
    const [isGroupView, setIsGroupView] = useState(true);
    const [isCompareModalOpen, setIsCompareModalOpen] = useState(false);
    const [selectedGroup, setSelectedGroup] = useState(null);

    // Pagination State
    const [currentPage, setCurrentPage] = useState(1);
    const [itemsPerPage] = useState(20);

    // Pagination Helper
    const paginate = (pageNumber) => {
        setCurrentPage(pageNumber);
        window.scrollTo({ top: 0, behavior: 'smooth' }); // Scroll to top on page change
    };

    // Scroll to Top on Mount
    useEffect(() => {
        window.scrollTo(0, 0);
    }, []);
    
    // Filters State
    const [filters, setFilters] = useState({
        source: [],
        brand: [],
        storage: [],
        ram: [],
        screen: [],
        processor: [],
        hz: [],
        battery: [],
    });

    // Helper to get Counts
    const getCounts = (key) => {
        const counts = {};
        normalizedMobileData.forEach(p => {
             let val;
             if (key === 'screen') {
                 val = getClassedSize(p.specs.screen);
             } else if (key === 'processor') {
                 // --- GROUPING LOGIC (Must Match FilterOptions Exact) ---
                 const cpu = (p.specs.cpu || 'Unknown');
                 if (cpu.startsWith("Unisoc")) val = "Unisoc";
                 else if (cpu.startsWith("Snapdragon") || cpu.includes("Qualcomm")) val = "Snapdragon";
                 else if (cpu.startsWith("Exynos") || cpu.includes("Samsung Exynos")) val = "Samsung Exynos";
                 else if (cpu.startsWith("MediaTek") || cpu.includes("Dimensity") || cpu.includes("Helio")) val = "MediaTek";
                 else if (cpu.includes("Apple") || cpu.includes("A14") || cpu.includes("A15") || cpu.includes("A16")) val = "Apple";
                 else if (cpu.includes("Google Tensor") || cpu.includes("Tensor")) val = "Google Tensor";
                 else if (cpu.includes("Kirin")) val = "Kirin";
                 else if (cpu.includes("Octa Core")) val = "Octa Core";
                 else if (cpu.includes("Quad Core")) val = "Quad Core";
                 else if (cpu === "Unknown") val = "Unknown";
                 else val = "Other"; 
             } else if (key === 'ram') {
                 // VALIDATE RAM VALUES - Only allow standard values
                 const ramValue = p.specs.ram;
                 const validRams = ["2GB", "3GB", "4GB", "6GB", "8GB", "12GB", "16GB"];
                 val = validRams.includes(ramValue) ? ramValue : "Unknown";
             } else if (key === 'storage') {
                // VALIDATE STORAGE VALUES - Only allow standard values  
                const storageValue = p.specs.storage;
                const validStorages = ["16GB", "32GB", "64GB", "128GB", "256GB", "512GB"];
                val = validStorages.includes(storageValue) ? storageValue : "Unknown";
            } else {
                 val = key === 'brand' ? p.brand : (key === 'source' ? p.source : (key === 'hz' ? p.specs?.hz : (key === 'battery' ? p.specs?.battery : p.specs?.[key])));
             }
             counts[val] = (counts[val] || 0) + 1;
        });
        return counts;
    };

    // Filter Options
    const filterOptions = {
        source: ["MyTek", "Tunisianet", "TunisiaTech", "Wiki", "Tdiscount", "SpaceNet", "Samsung Tunisie"],
        brand: [...new Set(normalizedMobileData.map(p => p.brand))].sort(),
        storage: ["16GB", "32GB", "64GB", "128GB", "256GB", "512GB"],
        ram: ["2GB", "3GB", "4GB", "6GB", "8GB", "12GB", "16GB"],
        battery: ["2000 mAh", "2500 mAh", "3000 mAh", "4000 mAh", "5000 mAh", "6000 mAh"],
        refreshRate: ["Coming Soon"],
        screen: ["Coming Soon"],
        processor: [...new Set(normalizedMobileData.map(p => {
            const cpu = (p.specs.cpu || 'Unknown');

            // STRICT BUCKETING - Only specific high-level families allowed
            if (cpu.startsWith("Unisoc")) return "Unisoc";
            if (cpu.startsWith("Snapdragon") || cpu.includes("Qualcomm")) return "Snapdragon";
            if (cpu.startsWith("Exynos") || cpu.includes("Samsung Exynos")) return "Samsung Exynos";
            if (cpu.startsWith("MediaTek") || cpu.includes("Dimensity") || cpu.includes("Helio")) return "MediaTek";
            if (cpu.includes("Apple") || cpu.includes("A14") || cpu.includes("A15") || cpu.includes("A16")) return "Apple";
            if (cpu.includes("Google Tensor") || cpu.includes("Tensor")) return "Google Tensor";
            if (cpu.includes("Kirin")) return "Kirin";
            if (cpu.includes("Octa Core")) return "Octa Core";
            if (cpu.includes("Quad Core")) return "Quad Core";

            if (["Unisoc", "Snapdragon", "Samsung Exynos", "MediaTek", "Apple", "Google Tensor", "Kirin", "Octa Core", "Quad Core"].includes(cpu)) return cpu;

            if (cpu === "Unknown") return "Unknown";

            return "Other";
        }))].filter(c => ["Unisoc", "Snapdragon", "Samsung Exynos", "MediaTek", "Apple", "Google Tensor", "Kirin", "Octa Core", "Quad Core", "Unknown", "Other"].includes(c)).sort(),
        hz: ["60Hz", "90Hz", "120Hz", "144Hz"],
    };

    // Toggle Filter Handler
    const toggleFilter = (key, value) => {
        setFilters(prev => {
            // Source (Store) Filter: Exclusive Logic
            if (key === 'source') {
                const isAlreadySelected = prev.source.includes(value);
                return {
                    ...prev,
                    source: isAlreadySelected ? [] : [value]
                };
            }

            // Standard Multi-Select Logic for other filters
            const current = prev[key];
            const updated = current.includes(value)
                ? current.filter(i => i !== value)
                : [...current, value];
            return { ...prev, [key]: updated };
        });
    };

    // Reset Handlers
    const resetAll = () => {
        setFilters({ source: [], brand: [], storage: [], ram: [], screen: [], processor: [], hz: [], battery: [], refreshRate: [] });
        setPriceRange({ min: 0, max: 20000 });
        setSearchQuery('');
    };

    // --- DEEP LINKING LOGIC ---
    useEffect(() => {
        const params = new URLSearchParams(window.location.search);
        const compareIds = params.get('compare');

        if (compareIds) {
            const ids = compareIds.split(',');
            const found = normalizedMobileData.filter(p => ids.includes(p.id));

            if (found.length > 0) {
                setCompareList(found);
                setIsCompareModalOpen(true);
            }
        }
    }, []); // Run once on mount

// Filter Logic - Robust Version
useEffect(() => {
    let result = [...normalizedMobileData]; // Fresh copy each time
    
    console.log('Mobile Data Sources:', [...new Set(normalizedMobileData.map(p => p.source))].sort());
    console.log('Total Mobile Products:', normalizedMobileData.length);
    console.log('Current Filters:', filters);

    // 0. Wishlist Filter
    if (viewFavorites && wishlist.length > 0) {
        const wishlistIds = new Set(wishlist.map(w => w.id));
        result = result.filter(p => {
            // Direct Match
            if (wishlistIds.has(p.id)) return true;
            // Group Match
            const gKey = generateVariantKey(p);
            const gId = `group-${gKey}`;
            if (wishlistIds.has(gId)) return true;
            return false;
        });
        console.log('After wishlist filter:', result.length);
    }

    // Source Filter - Simplified
    if (filters.source && filters.source.length > 0) {
        const sourceFilter = filters.source[0]; // Take first selected source
        result = result.filter(p => {
            const pSource = String(p?.source || '').trim().toLowerCase();
            return pSource === sourceFilter.toLowerCase();
        });
        console.log('After source filter:', result.length);
    }

    // Brand Filter
    if (filters.brand && filters.brand.length > 0) {
        result = result.filter(p => filters.brand.includes(p.brand));
        console.log('After brand filter:', result.length);
    }
    
    // Storage Filter
    if (filters.storage && filters.storage.length > 0) {
        result = result.filter(p => filters.storage.includes(p.specs.storage));
        console.log('After storage filter:', result.length);
    }

    // RAM Filter
    if (filters.ram && filters.ram.length > 0) {
        result = result.filter(p => filters.ram.includes(p.specs.ram));
        console.log('After RAM filter:', result.length);
    }

    // Screen Filter
    if (filters.screen && filters.screen.length > 0) {
        result = result.filter(p => {
            const pClass = getClassedSize(p.specs.screen);
            return filters.screen.includes(pClass);
        });
        console.log('After screen filter:', result.length);
    }

    // Refresh Rate Filter
    if (filters.refreshRate && filters.refreshRate.length > 0) {
        result = result.filter(p => {
            const pHz = p.specs.hz || 'Unknown';
            return filters.refreshRate.includes(pHz);
        });
        console.log('After refreshRate filter:', result.length);
    }

    // Processor Filter
    if (filters.processor && filters.processor.length > 0) {
        result = result.filter(p => {
            const cpu = p.specs.cpu || 'Unknown';
            return filters.processor.some(f => {
                if (f === "Unisoc") return cpu.startsWith("Unisoc");
                if (f === "Snapdragon") return cpu.startsWith("Snapdragon") || cpu.includes("Qualcomm");
                if (f === "Samsung Exynos") return cpu.startsWith("Exynos") || cpu.includes("Samsung Exynos");
                if (f === "MediaTek") return cpu.startsWith("MediaTek") || cpu.includes("Dimensity") || cpu.includes("Helio");
                if (f === "Apple") return cpu.includes("Apple") || cpu.includes("A14") || cpu.includes("A15");
                if (f === "Octa Core") return cpu.includes("Octa Core");
                if (f === "Quad Core") return cpu.includes("Quad Core");
                if (f === "Unknown") return cpu === "Unknown";
                if (f === "Other") {
                    const mainBuckets = ["Unisoc", "Snapdragon", "Exynos", "Samsung Exynos", "MediaTek", "Dimensity", "Helio", "Apple", "Octa Core", "Quad Core", "Unknown"];
                    return !mainBuckets.some(b => cpu.includes(b));
                }
                return f === cpu;
            });
        });
        console.log('After processor filter:', result.length);
    }

    // Hz Filter
    if (filters.hz && filters.hz.length > 0) {
        result = result.filter(p => filters.hz.includes(p.specs.hz || 'Unknown'));
        console.log('After Hz filter:', result.length);
    }

    // Battery Filter
    if (filters.battery && filters.battery.length > 0) {
        result = result.filter(p => {
            const battStr = (p.specs.battery || "").toString();
            return filters.battery.includes(battStr);
        });
        console.log('After battery filter:', result.length);
    }

    // Price Filter - exclude items with illogical prices (< 50 DT for phones)
    if (priceRange) {
        result = result.filter(p => {
            const price = parseFloat(p.price);
            if (!price || isNaN(price) || price < 50) return false;
            return price >= priceRange.min && price <= priceRange.max;
        });
        console.log('After price filter:', result.length);
    }

    // Search Filter
    if (searchQuery && searchQuery.trim()) {
        const q = searchQuery.toLowerCase().trim();
        result = result.filter(p =>
            (p?.title || '').toLowerCase().includes(q) ||
            (p?.brand || '').toLowerCase().includes(q)
        );
        console.log('After search filter:', result.length);
    }

    // Sort Logic
    let sortedResult = [...result];
    if (sortOption === "price-asc") {
        sortedResult.sort((a, b) => parseFloat(a.price) - parseFloat(b.price));
    } else if (sortOption === "price-desc") {
        sortedResult.sort((a, b) => parseFloat(b.price) - parseFloat(a.price));
    } else if (sortOption === "name-asc") {
        sortedResult.sort((a, b) => (a.title || '').localeCompare(b.title || ''));
    } else if (sortOption === "name-desc") {
        sortedResult.sort((a, b) => (b.title || '').localeCompare(a.title || ''));
    } else if (sortOption === "discount") {
        sortedResult.sort((a, b) => {
                const priceA = parseFloat(a.price) || 0;
                const oldA = parseFloat(a.oldPrice) || 0;
                const discountA = (oldA > priceA && oldA > 0) ? ((oldA - priceA) / oldA) : 0;
                const priceB = parseFloat(b.price) || 0;
                const oldB = parseFloat(b.oldPrice) || 0;
                const discountB = (oldB > priceB && oldB > 0) ? ((oldB - priceB) / oldB) : 0;

                return discountB - discountA; // Descending
            });
        } else if (sortOption === "value-ram") {
            sortedResult.sort((a, b) => {
                const getRatio = (p) => {
                    const ramStr = p.specs && p.specs.ram ? String(p.specs.ram).toLowerCase() : '';
                    const match = ramStr.match(/(\d+)/);
                    const ram = match ? parseInt(match[0]) : 0;
                    return (ram > 0 && parseFloat(p.price) > 0) ? (parseFloat(p.price) / ram) : 99999; 
                };
                return getRatio(a) - getRatio(b); // Lower is better
            });
        }
        
        // Grouping Logic
        if (isGroupView) {
            const groups = {};
            sortedResult.forEach(p => {
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
                 
                 // Keep lowest price as face - UPDATE: Handle sorting impact
                 // Actually, if we are sorting by price, the 'face' might change?
                 // For now, standard behavior: Lowest Price is the face.
                 if (p.price < groups[key].minPrice) {
                     groups[key].minPrice = p.price;
                     groups[key].baseProduct = p;
                     groups[key].price = p.price;
                     groups[key].image = p.image;
                     groups[key].title = p.title;
                 }
            });
            result = Object.values(groups);
            
            // Re-sort the groups if needed (e.g. by face price)
            if (sortOption === "price-asc") result.sort((a, b) => parseFloat(a.minPrice) - parseFloat(b.minPrice));
            else if (sortOption === "price-desc") result.sort((a, b) => parseFloat(b.minPrice) - parseFloat(a.minPrice));
            // Name/Discount logic for groups is tricky, usually defaults to face. 
            // We'll leave it as natural order of sorted input for others.
        } else {
             result = sortedResult;
        }

        setProducts(result);
        setCurrentPage(1); // Reset to page 1 on filter change
    }, [filters, priceRange, searchQuery, viewFavorites, isGroupView, wishlist, sortOption]);

    // Full Screen Comparison Mode
    if (isCompareModalOpen) {
        return (
            <ComparisonView 
                selectedProducts={compareList} 
                onClose={() => setIsCompareModalOpen(false)} 
                removeFromCompare={removeFromCompare} 
            />
        );
    }

    return (
        <div className="products-layout-final" style={{
            display: 'flex',
            minHeight: '100vh',
            backgroundColor: '#E8F1F5',
            backgroundImage: `radial-gradient(circle at 50% 0%, rgba(255, 255, 255, 0.6) 0%, transparent 60%),
                              radial-gradient(circle at 0% 100%, rgba(255, 255, 255, 0.4) 0%, transparent 50%)`,
            color: '#1A2B48',
            fontFamily: "'Inter', sans-serif",
            position: 'relative'
        }}>
            {/* SIDEBAR */}
            <aside className="products-sidebar-v2" style={{ 
                width: isMobile ? '0' : '260px', 
                flexShrink: 0,
                borderRight: '1px solid #e2e8f0',
                background: 'white',
                height: '100vh',
                position: 'fixed',
                top: 0,
                bottom: 0,
                left: 0,
                zIndex: 3000,
                display: 'flex',
                flexDirection: 'column'
            }}>
                <div className="sidebar-banner-final" style={{ 
                    padding: '0 20px', 
                    background: '#0F172A', 
                    height: '80px',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    flexShrink: 0
                }}>
                    <Link to="/" style={{ color: 'white', textDecoration: 'none', display: 'flex', alignItems: 'center', gap: '8px', fontSize: '1rem', fontWeight: 'bold' }}>
                        <Home size={18} /> Home
                    </Link>
                </div>

                <div className="filter-header-row" style={{ padding: '15px 20px', display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexShrink: 0 }}>
                    <h3 style={{ margin: 0, fontSize: '0.8rem', textTransform: 'uppercase', letterSpacing: '1px', color: '#64748b' }}>Filters</h3>
                    <button onClick={resetAll} className="reset-btn" style={{ background: '#f1f5f9', color: '#444' }}><RefreshCw size={14} /> Reset</button>
                </div>

                <div className="scroll-filters" style={{ flex: 1, overflowY: 'auto', height: 0 }}>
                     <FilterSection title="Store" options={filterOptions.source} selected={filters.source} onSelect={(v) => toggleFilter('source', v)} isOpen={true} counts={getCounts('source')} />
                     <FilterSection title="Brand" options={filterOptions.brand} selected={filters.brand} onSelect={(v) => toggleFilter('brand', v)} isOpen={true} counts={getCounts('brand')} />
                     
                     <FilterSection title="Price Range (DT)" isOpen={true}>
                        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '8px', marginBottom: '10px' }}>
                            {[
                                { label: '< 1000 DT', min: 0, max: 1000 },
                                { label: '1000 - 1500', min: 1000, max: 1500 },
                                { label: '1500 - 2000', min: 1500, max: 2000 },
                                { label: '2000 - 3000', min: 2000, max: 3000 },
                                { label: '3000 - 4500', min: 3000, max: 4500 },
                                { label: '4500 DT +', min: 4500, max: 20000 }
                            ].map(range => (
                                <button
                                    key={range.label}
                                    onClick={() => {
                                        if (priceRange.min === range.min && priceRange.max === range.max) {
                                            setPriceRange({ min: 0, max: 20000 }); // Uncheck
                                        } else {
                                            setPriceRange({ min: range.min, max: range.max });
                                        }
                                    }}
                                    style={{
                                        padding: '6px 4px',
                                        fontSize: '0.75rem',
                                        borderRadius: '6px',
                                        border: (priceRange.min === range.min && priceRange.max === range.max) ? '1px solid #1A2B48' : '1px solid #e2e8f0',
                                        background: (priceRange.min === range.min && priceRange.max === range.max) ? '#1A2B48' : 'white',
                                        color: (priceRange.min === range.min && priceRange.max === range.max) ? '#fff' : '#1A2B48',
                                        cursor: 'pointer',
                                        fontWeight: '600',
                                        transition: '0.2s'
                                    }}
                                >
                                    {range.label}
                                </button>
                            ))}
                        0</div>
                        <div className="price-inputs" style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
                            <input 
                                type="number" 
                                value={priceRange.min} 
                                onChange={(e) => setPriceRange({...priceRange, min: Number(e.target.value)})} 
                                style={{ background: 'white', border: '1px solid #e2e8f0', color: '#1A2B48', padding: '6px 10px', borderRadius: '8px', width: '100%', fontSize: '0.85rem' }}
                            />
                            <span style={{ color: '#64748b', fontSize: '0.8rem' }}>to</span>
                            <input 
                                type="number" 
                                value={priceRange.max} 
                                onChange={(e) => setPriceRange({...priceRange, max: Number(e.target.value)})} 
                                style={{ background: 'white', border: '1px solid #e2e8f0', color: '#1A2B48', padding: '6px 10px', borderRadius: '8px', width: '100%', fontSize: '0.85rem' }}
                            />
                        </div>
                    </FilterSection>

                    <FilterSection title="CPU" options={filterOptions.processor} selected={filters.processor} onSelect={(v) => toggleFilter('processor', v)} counts={getCounts('processor')} />
                    <FilterSection title="RAM" options={filterOptions.ram} selected={filters.ram} onSelect={(v) => toggleFilter('ram', v)} counts={getCounts('ram')} />
                    <FilterSection title="Storage" options={filterOptions.storage} selected={filters.storage} onSelect={(v) => toggleFilter('storage', v)} counts={getCounts('storage')} />
                    <FilterSection title="Battery (Coming Soon)" options={[]} selected={[]}>
                        <p style={{ color: '#94a3b8', fontSize: '0.8rem', fontStyle: 'italic', margin: '0 0 8px' }}>Coming Soon</p>
                    </FilterSection>
                    <FilterSection title="Refresh Rate (Coming Soon)" options={[]} selected={[]}>
                        <p style={{ color: '#94a3b8', fontSize: '0.8rem', fontStyle: 'italic', margin: '0 0 8px' }}>Coming Soon</p>
                    </FilterSection>
                    <FilterSection title="Screen Size (Coming Soon)" options={[]} selected={[]}>
                        <p style={{ color: '#94a3b8', fontSize: '0.8rem', fontStyle: 'italic', margin: '0 0 8px' }}>Coming Soon</p>
                    </FilterSection>
                </div>
            </aside>

            {/* MAIN CONTENT */}
            <main className="products-main" style={{ 
                flex: 1, 
                padding: '80px 40px 40px', 
                position: 'relative',
                marginLeft: sidebarWidth,
                minWidth: 0
            }}>
                
                {/* STICKY TOP BANNER (Exact Match: Fixed at top, starting after sidebar) */}
                <div className="sleek-sticky-banner" style={{
                    position: 'fixed',
                    top: 0,
                    left: sidebarWidth,
                    width: isMobile ? '100%' : `calc(100% - ${sidebarWidth})`,
                    height: '80px',
                    background: '#0F172A',
                    backdropFilter: 'blur(20px)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    zIndex: 2000,
                    borderBottom: '2px solid #5F8D8B',
                    boxShadow: '0 10px 15px -3px rgba(0,0,0,0.2)',
                    padding: '0 20px'
                }}>
                    <button 
                        onClick={() => setShowMobileMenu(true)}
                        style={{ position: 'absolute', left: isMobile ? '20px' : '40px', background: 'none', border: 'none', cursor: 'pointer', display: 'flex', alignItems: 'center' }}
                    >
                        <Menu size={28} color="white" />
                    </button>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '15px' }}>
                        <span style={{ color: 'white', fontWeight: '900', fontSize: '2rem', letterSpacing: '-0.5px', textShadow: '0 2px 10px rgba(0,0,0,0.5)' }}>
                            Techno<span style={{ color: '#5F8D8B' }}>Price</span>
                        </span>
                        
                        {/* HEART AND COMPARE ICONS NEXT TO LOGO - DON'T MOVE */}
                        <Link to="/wishlist" style={{ 
                            display: 'flex', 
                            alignItems: 'center', 
                            justifyContent: 'center', 
                            padding: '4px',
                            color: '#F8FAFC',
                            textDecoration: 'none'
                        }}>
                            <Heart size={24} strokeWidth={2} />
                        </Link>

                        <button onClick={() => setIsCompareModalOpen(true)} style={{ 
                            display: 'flex', 
                            alignItems: 'center', 
                            justifyContent: 'center', 
                            padding: '4px',
                            color: '#F8FAFC',
                            background: 'none',
                            border: 'none',
                            cursor: 'pointer'
                        }}>
                            <Scale size={24} strokeWidth={2} />
                        </button>
                    </div>
                </div>

                {/* BREADCRUMBS */}
                <div className="breadcrumbs" style={{ padding: '20px 0 0 0', display: 'flex', alignItems: 'center', gap: '8px', fontSize: '0.9rem', color: '#64748b', fontWeight: '500' }}>
                    <Link to="/" style={{ color: '#64748b', textDecoration: 'none' }}>Home</Link>
                    <ChevronRight size={14} />
                    <span style={{ color: '#1A2B48' }}>Mobiles</span>
                </div>

                <div className="products-header" style={{ paddingTop: '40px', marginBottom: '40px' }}>
                    <h1 style={{ 
                        fontSize: '3.5rem', 
                        fontWeight: '900', 
                        margin: 0, 
                        letterSpacing: '-2px',
                        background: 'linear-gradient(90deg, #1A2B48 0%, #4D7C7B 100%)',
                        WebkitBackgroundClip: 'text',
                        WebkitTextFillColor: 'transparent',
                        textShadow: '0 10px 20px rgba(26, 43, 72, 0.05)'
                    }}>
                        PHONE MARKETPLACE
                    </h1>
                    <p style={{ color: '#5F8D8B', marginTop: '10px', fontSize: '1.1rem', fontWeight: '500' }}>
                        <span style={{ fontWeight: 'bold' }}>Active: {normalizedMobileData.length} Items</span> • Top Smartphones from Tunisianet, MyTek, Wiki & Spacenet
                    </p>
                </div>

                <div className="top-toolbar" style={{
                    position: 'sticky',
                    top: '80px', /* Sticky below the fixed 80px banner */
                    zIndex: '100',
                    background: 'rgba(232, 241, 245, 0.95)',
                    backdropFilter: 'blur(12px)',
                    margin: '0 -20px 20px -20px', 
                    padding: '15px 20px',
                    borderRadius: '0 0 16px 16px',
                    borderBottom: '1px solid rgba(26, 43, 72, 0.05)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                    gap: '20px'
                }}>
                    {/* LOGO IN TOOLBAR (Desktop Only) */}
                    <div className="desktop-logo" style={{ marginRight: 'auto' }}>
                        <span style={{ fontSize: '1.5rem', fontWeight: '900', color: '#1A2B48', letterSpacing: '-0.5px' }}>
                            Techno<span style={{ color: '#5F8D8B' }}>Price</span>
                        </span>
                    </div>

                    <div className="search-box" style={{ 
                        width: '100%', maxWidth: '400px', 
                        background: 'white', 
                        border: '1px solid #cbd5e1', 
                        display: 'flex', 
                        alignItems: 'center', 
                        gap: '10px', 
                        padding: '8px 15px', 
                        borderRadius: '12px',
                        boxShadow: '0 2px 4px rgba(0,0,0,0.05)'
                    }}>
                        <Link to="/" style={{ color: '#0F172A', marginRight: '5px' }}>
                            <Home size={20} />
                        </Link>
                        <Search size={18} color="#64748b" />
                        <input 
                            type="text" 
                            placeholder="Search by name, brand, or specs..." 
                            value={searchQuery}
                            onChange={(e) => setSearchQuery(e.target.value)}
                            style={{ background: 'transparent', border: 'none', outline: 'none', color: '#0F172A', width: '100%', fontSize: '0.95rem', fontWeight: '500' }}
                        />
                    </div>



                    <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                        <button 
                            onClick={() => setViewFavorites(!viewFavorites)}
                            style={{
                                display: 'flex',
                                alignItems: 'center',
                                gap: '8px',
                                background: viewFavorites ? '#5F8D8B' : '#0F172A', 
                                color: 'white',
                                border: 'none',
                                padding: '10px 16px',
                                borderRadius: '8px',
                                cursor: 'pointer',
                                fontWeight: '700',
                                whiteSpace: 'nowrap',
                                transition: 'all 0.3s'
                            }}
                        >
                            Show Favorites
                        </button>
                        <span style={{ color: '#64748b', fontSize: '0.9rem', fontWeight: '600' }}>Wishlist (0)</span>
                        <div style={{
                            background: '#0F172A',
                            color: 'white',
                            display: 'flex',
                            alignItems: 'center',
                            gap: '8px',
                            padding: '0 16px',
                            borderRadius: '8px',
                            whiteSpace: 'nowrap',
                            fontWeight: '600',
                            height: '42px'
                        }}>
                             <ArrowUpDown size={16} /> 
                             <select 
                                value={sortOption} 
                                onChange={(e) => setSortOption(e.target.value)}
                                style={{
                                    background: 'transparent',
                                    border: 'none',
                                    color: 'white',
                                    fontWeight: '600',
                                    fontSize: '0.9rem',
                                    outline: 'none',
                                    cursor: 'pointer',
                                    padding: '8px 0'
                                }}
                             >
                                <option value="default" style={{ background: '#0F172A' }}>Sort By: Featured</option>
                                <option value="price-asc" style={{ background: '#0F172A' }}>Price: Low to High</option>
                                <option value="price-desc" style={{ background: '#0F172A' }}>Price: High to Low</option>
                                <option value="name-asc" style={{ background: '#0F172A' }}>Name: A-Z</option>
                                <option value="discount-desc" style={{ background: '#0F172A' }}>Best Discount</option>
                                <option value="value-ram" style={{ background: '#0F172A' }}>Best RAM Value</option>
                             </select>
                        </div>
                    </div>
                </div>

            <div className="store-filter-bar" style={{ display: 'flex', flexWrap: 'wrap', gap: '10px', marginBottom: '15px' }}>
                <button 
                    onClick={() => setFilters({...filters, source: []})}
                    style={{
                        padding: '10px 25px',
                        borderRadius: '30px',
                        background: filters.source.length === 0 ? '#3b82f6' : '#94a3b8',
                        color: 'white',
                        border: 'none',
                        fontWeight: 'bold',
                        cursor: 'pointer'
                    }}
                >
                    All Stores
                </button>
                {filterOptions.source.map(store => (
                    <button 
                        key={store}
                        onClick={() => toggleFilter('source', store)}
                        style={{
                            padding: '10px 20px',
                            borderRadius: '30px',
                            background: filters.source.includes(store) ? '#3b82f6' : '#94a3b8',
                            color: 'white',
                            border: 'none',
                            fontWeight: 'bold',
                            cursor: 'pointer'
                        }}
                    >
                        {store.charAt(0).toUpperCase() + store.slice(1)}
                    </button>
                ))}
            </div>

            <div className="brand-filter-bar" style={{ display: 'flex', flexWrap: 'wrap', gap: '10px', marginBottom: '20px' }}>
                <button 
                    onClick={() => setFilters({...filters, brand: []})}
                    style={{
                        padding: '10px 25px',
                        borderRadius: '30px',
                        background: filters.brand.length === 0 ? '#8b5cf6' : '#94a3b8',
                        color: 'white',
                        border: 'none',
                        fontWeight: 'bold',
                        cursor: 'pointer'
                    }}
                >
                    All Brands
                </button>
                {filterOptions.brand.map(brand => (
                    <button 
                        key={brand}
                        onClick={() => toggleFilter('brand', brand)}
                        style={{
                            padding: '10px 18px',
                            borderRadius: '30px',
                            background: filters.brand.includes(brand) ? '#8b5cf6' : '#94a3b8',
                            color: 'white',
                            border: 'none',
                            fontWeight: 'bold',
                            cursor: 'pointer'
                        }}
                    >
                        {brand}
                    </button>
                ))}
            </div>

            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px', borderBottom: '1px solid rgba(0,0,0,0.05)', paddingBottom: '10px' }}>
                <span style={{ fontSize: '0.9rem', color: '#64748b', fontWeight: 'bold' }}>{products.length} phones found</span>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <div style={{ width: '40px', height: '20px', background: '#e2e8f0', borderRadius: '10px', position: 'relative', cursor: 'pointer' }}>
                         <div style={{ width: '16px', height: '16px', background: 'white', borderRadius: '50%', position: 'absolute', top: '2px', left: '2px', boxShadow: '0 2px 4px rgba(0,0,0,0.1)' }} />
                    </div>
                    <span style={{ fontSize: '0.85rem', color: '#64748b', fontWeight: '500' }}>In Stock Only</span>
                </div>
            </div>

                {products.length === 0 ? (
                    <div className="empty-state" style={{ textAlign: 'center', padding: '60px', color: '#64748b' }}>
                        {/* Empty State Trigger - Force Reload */}
                        <h2>No phones found</h2>
                        <button onClick={resetAll} style={{ marginTop: '20px', padding: '10px 20px', background: '#5F8D8B', border: 'none', borderRadius: '8px', cursor: 'pointer', fontWeight: 'bold', color: 'white' }}>
                            Clear Filters
                        </button>
                    </div>
                ) : (
                    <>
                        <div className="grid" key={filters.source.join(',')} style={{ display: 'grid', gridTemplateColumns: 'repeat(4, minmax(0, 1fr))', gap: '20px' }}> 
                        {(() => {
                            const indexOfLastItem = currentPage * itemsPerPage;
                            const indexOfFirstItem = indexOfLastItem - itemsPerPage;
                            const currentItems = products.slice(indexOfFirstItem, indexOfLastItem);
                            
                            return (
                                currentItems.map((product) => {
                                    if (!product) return null;
                                    return (
                                        <ProductCard 
                                            key={product.id} 
                                            product={product} 
                                            addToCompare={toggleCompare}
                                            isInCompare={isInCompare(product.id)}
                                            toggleWishlist={handleToggleWishlist}
                                            isFavorite={isInWishlist(product.id) || (product.isGroup && product.variants && product.variants.some(v => isInWishlist(v.id)))}
                                            isGroupCard={product.isGroup}
                                            groupCount={product.variants?.length}
                                            onGroupSelect={() => navigate(`/mobile-group/${encodeURIComponent(product.key)}`)}
                                            onViewVariants={() => setSelectedGroup(product)}
                                            theme="light"
                                        />
                                    );
                                })
                            );
                        })()}
                    </div>

                    {/* PAGINATION CONTROLS (Moved Outside Grid) */}
                    {(() => {
                        const totalPages = Math.ceil(products.length / itemsPerPage);
                        if (totalPages <= 1) return null;
                        return (
                            <div className="pagination-controls" style={{ 
                                display: 'flex', 
                                justifyContent: 'center', 
                                alignItems: 'center', 
                                gap: '10px',
                                marginTop: '40px',
                                paddingTop: '20px',
                                borderTop: '1px solid rgba(0,0,0,0.05)'
                            }}>
                                 {/* Prev Button */}
                                 <button 
                                    onClick={() => paginate(currentPage - 1)}
                                    disabled={currentPage === 1}
                                    style={{
                                        background: currentPage === 1 ? '#e2e8f0' : '#1A2B48', 
                                        color: currentPage === 1 ? '#64748b' : 'white',
                                        border: 'none',
                                        padding: '10px 20px',
                                        borderRadius: '8px',
                                        cursor: currentPage === 1 ? 'default' : 'pointer',
                                        transition: 'all 0.2s',
                                        display: 'flex',
                                        alignItems: 'center',
                                        gap: '5px'
                                    }}
                                >
                                    <ChevronDown size={16} style={{ transform: 'rotate(90deg)' }} /> 
                                    Prev
                                </button>

                                {/* Page Numbers */}
                                {(() => {
                                    const pages = [];
                                    // Always show First Page
                                    pages.push(
                                        <button key={1} onClick={() => paginate(1)} style={{
                                            background: currentPage === 1 ? '#5F8D8B' : 'white',
                                            color: currentPage === 1 ? 'white' : '#1A2B48',
                                            border: '1px solid #e2e8f0',
                                            width: '36px', height: '36px', borderRadius: '8px', cursor: 'pointer', fontWeight: 'bold'
                                        }}>{1}</button>
                                    );

                                    if (currentPage > 3) pages.push(<span key="start-elip" style={{ color: '#64748b' }}>...</span>);

                                    for (let i = Math.max(2, currentPage - 1); i <= Math.min(totalPages - 1, currentPage + 1); i++) {
                                         pages.push(
                                            <button key={i} onClick={() => paginate(i)} style={{
                                                background: currentPage === i ? '#5F8D8B' : 'white',
                                                color: currentPage === i ? 'white' : '#1A2B48',
                                                border: '1px solid #e2e8f0',
                                                width: '36px', height: '36px', borderRadius: '8px', cursor: 'pointer', fontWeight: 'bold'
                                            }}>{i}</button>
                                        );
                                    }

                                    if (currentPage < totalPages - 2) pages.push(<span key="end-elip" style={{ color: '#64748b' }}>...</span>);

                                    if (totalPages > 1) {
                                         pages.push(
                                            <button key={totalPages} onClick={() => paginate(totalPages)} style={{
                                                background: currentPage === totalPages ? '#5F8D8B' : 'white',
                                                color: currentPage === totalPages ? 'white' : '#1A2B48',
                                                border: '1px solid #e2e8f0',
                                                width: '36px', height: '36px', borderRadius: '8px', cursor: 'pointer', fontWeight: 'bold'
                                            }}>{totalPages}</button>
                                        );
                                    }
                                    return pages;
                                })()}

                                {/* Next Button */}
                                <button 
                                    onClick={() => paginate(currentPage + 1)}
                                    disabled={currentPage === totalPages}
                                    style={{
                                        background: currentPage === totalPages ? '#e2e8f0' : '#1A2B48', 
                                        color: currentPage === totalPages ? '#64748b' : 'white',
                                        border: 'none',
                                        padding: '10px 20px',
                                        borderRadius: '8px',
                                        cursor: currentPage === totalPages ? 'default' : 'pointer',
                                        transition: 'all 0.2s',
                                        display: 'flex',
                                        alignItems: 'center',
                                        gap: '5px'
                                    }}
                                >
                                    Next
                                    <ChevronDown size={16} style={{ transform: 'rotate(-90deg)' }} />
                                </button>
                            </div>
                        );
                    })()}
                    </>
                )}
                {/* --- FOOTER IN MAIN --- */}
                <div style={{ marginTop: '100px', width: '100%' }}>
                    <Footer />
                </div>
            </main>

            {/* --- VARIANT SELECTION MODAL (Mobiles) --- */}
            {selectedGroup && (
                <div 
                    className="compare-modal-overlay" 
                    onClick={() => setSelectedGroup(null)} 
                    style={{ 
                        position: 'fixed',
                        top: 0,
                        left: 0,
                        width: '100vw',
                        height: '100vh',
                        background: 'rgba(0, 0, 0, 0.85)',
                        backdropFilter: 'blur(8px)',
                        zIndex: 2147483647,
                        display: 'flex',
                        justifyContent: 'center',
                        alignItems: 'center',
                        padding: '20px',
                        margin: 0,
                        inset: 0
                    }}
                >
                    <div 
                        className="compare-modal-content" 
                        onClick={e => e.stopPropagation()} 
                        style={{ 
                            position: 'relative',
                            background: '#0F172A',
                            border: '1px solid rgba(255, 255, 255, 0.1)',
                            borderRadius: '20px',
                            boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.5)',
                            width: '100%',
                            maxWidth: '600px',
                            maxHeight: '85vh',
                            overflowY: 'auto',
                            padding: '24px'
                        }}
                    >
                        <button 
                            className="modal-close-btn" 
                            onClick={() => setSelectedGroup(null)}
                            style={{
                                position: 'absolute',
                                top: '15px',
                                right: '15px',
                                background: 'rgba(255, 255, 255, 0.05)',
                                border: '1px solid rgba(255, 255, 255, 0.1)',
                                borderRadius: '50%',
                                width: '36px',
                                height: '36px',
                                display: 'flex',
                                justifyContent: 'center',
                                alignItems: 'center',
                                cursor: 'pointer',
                                color: 'white',
                                zIndex: 10
                            }}
                        >
                            <X size={24} />
                        </button>
                        <h2 style={{ color: 'white', marginBottom: '10px', fontSize: '1.2rem', borderBottom: '1px solid rgba(255,255,255,0.1)', paddingBottom: '10px' }}>
                            Select Configuration
                        </h2>
                        <p style={{ color: '#94a3b8', marginBottom: '20px', fontSize: '0.9rem' }}>{selectedGroup.key}</p>
                        
                        <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
                            {selectedGroup.variants.sort((a,b) => a.price - b.price).map((v, idx) => (
                                <div key={idx} style={{ 
                                    display: 'flex', 
                                    justifyContent: 'space-between', 
                                    alignItems: 'center', 
                                    background: 'rgba(255,255,255,0.03)', 
                                    padding: '15px', 
                                    borderRadius: '10px', 
                                    border: '1px solid rgba(255,255,255,0.05)',
                                    gap: '15px'
                                }}>
                                    <div style={{ flex: 1 }}>
                                        <div style={{ color: 'white', fontWeight: '600', display: 'flex', alignItems: 'center', gap: '10px', flexWrap: 'wrap' }}>
                                            <span>{v.specs.ram} RAM</span>
                                            <span style={{ color: '#64748b' }}>/</span>
                                            <span>{v.specs.storage} Storage</span>
                                        </div>
                                        <div style={{ fontSize: '0.75rem', color: '#64748b', marginTop: '4px' }}>
                                            {v.source} • {v.specs.os || 'Android'}
                                        </div>
                                    </div>
                                    <div style={{ display: 'flex', alignItems: 'center', gap: '15px' }}>
                                        <div style={{ color: '#10b981', fontWeight: 'bold', fontSize: '1.1rem', whiteSpace: 'nowrap' }}>
                                            {typeof v.price === 'number' ? v.price.toFixed(3) : v.price} TND
                                        </div>
                                        <a 
                                            href={v.link} 
                                            target="_blank" 
                                            rel="noopener noreferrer" 
                                            onClick={(e) => e.stopPropagation()}
                                            style={{ 
                                                background: '#5F8D8B', 
                                                color: 'white', 
                                                border: 'none', 
                                                textDecoration: 'none', 
                                                padding: '8px 16px', 
                                                borderRadius: '6px', 
                                                fontWeight: 'bold',
                                                cursor: 'pointer',
                                                fontSize: '0.9rem'
                                            }}
                                        >
                                            View
                                        </a>
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>
                </div>
            )}

            {/* Comparison Floating Bar & Modal */}
            {/* Compare Dock */}
            {compareList.length > 0 && (
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
                        onClick={() => setIsCompareModalOpen(true)}
                    >
                        Compare Now <ChevronRight size={16} />
                    </button>
                </div>
            )}

            {/* --- VARIANT SELECTION MODAL --- */}
            {/* MOBILE MENU DRAWER (Docked Under Icon, Full Remaining Height) */}
            {showMobileMenu && (
                <div 
                    style={{ 
                        position: 'fixed', 
                        top: '80px', 
                        left: 0, 
                        right: 0, 
                        bottom: 0, 
                        background: 'rgba(0,0,0,0.4)', 
                        zIndex: 10000 
                    }} 
                    onClick={() => setShowMobileMenu(false)}
                >
                    <div 
                        style={{ 
                            width: '300px', 
                            height: '100%', 
                            background: '#0F172A', 
                            padding: '30px 20px', 
                            display: 'flex', 
                            flexDirection: 'column', 
                            gap: '20px',
                            boxShadow: '10px 0 25px rgba(0,0,0,0.3)',
                            borderRight: '1px solid rgba(255,255,255,0.1)'
                        }} 
                        onClick={e => e.stopPropagation()}
                    >
                        <Link to="/" style={{ color: 'white', textDecoration: 'none', fontSize: '1.1rem', display: 'flex', alignItems: 'center', gap: '10px' }} onClick={() => setShowMobileMenu(false)}>
                            <Home size={20} /> Home
                        </Link>
                        <Link to="/products" style={{ color: 'white', textDecoration: 'none', fontSize: '1.1rem', display: 'flex', alignItems: 'center', gap: '10px' }} onClick={() => setShowMobileMenu(false)}>
                            <Laptop size={20} /> Computers
                        </Link>
                        <Link to="/mobiles" style={{ color: '#5F8D8B', textDecoration: 'none', fontSize: '1.1rem', fontWeight: 'bold', display: 'flex', alignItems: 'center', gap: '10px' }} onClick={() => setShowMobileMenu(false)}>
                            <Smartphone size={20} /> Mobiles
                        </Link>

                        <div style={{ height: '1px', background: 'rgba(255,255,255,0.1)', margin: '10px 0' }} />

                        <Link to="/components" style={{ color: 'white', textDecoration: 'none', fontSize: '1.1rem', display: 'flex', alignItems: 'center', gap: '10px' }} onClick={() => setShowMobileMenu(false)}>
                            <CircuitBoard size={20} /> Components
                        </Link>
                        
                        <div style={{ paddingLeft: '30px', display: 'flex', flexDirection: 'column', gap: '15px' }}>
                            <Link to="/products?category=cpu" style={{ color: '#94a3b8', textDecoration: 'none', fontSize: '1rem', display: 'flex', alignItems: 'center', gap: '10px' }} onClick={() => setShowMobileMenu(false)}>
                                <Cpu size={18} /> Processors
                            </Link>
                            <Link to="/products?category=gpu" style={{ color: '#94a3b8', textDecoration: 'none', fontSize: '1rem', display: 'flex', alignItems: 'center', gap: '10px' }} onClick={() => setShowMobileMenu(false)}>
                                <Monitor size={18} /> Graphics Cards
                            </Link>
                            <Link to="/products?category=motherboard" style={{ color: '#94a3b8', textDecoration: 'none', fontSize: '1rem', display: 'flex', alignItems: 'center', gap: '10px' }} onClick={() => setShowMobileMenu(false)}>
                                <CircuitBoard size={18} /> Motherboards
                            </Link>
                            <Link to="/products?category=ram" style={{ color: '#94a3b8', textDecoration: 'none', fontSize: '1rem', display: 'flex', alignItems: 'center', gap: '10px' }} onClick={() => setShowMobileMenu(false)}>
                                <Server size={18} /> RAM
                            </Link>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

export default MobilesPage;

