import React, { useState, useMemo, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { ChevronDown, ChevronUp, Sliders, Search, ArrowUpDown, Scale, X, RefreshCw, Eye, SearchX, Laptop, Trash2, ArrowUp, TrendingUp, Home, Heart, ChevronRight, ArrowLeft } from 'lucide-react';
import { useCompare } from './context/CompareContext';
import { useWishlist } from './context/WishlistContext';
import QuickLookModal from './QuickLookModal';
import ComparisonView from './ComparisonView'; 
import PriceAlertModal from './PriceAlertModal'; 
import PriceHistoryModal from './PriceHistoryModal'; 
import { Bell } from 'lucide-react'; 
import './ProductsPageV3.css';

// UTILS IMPORT
import { normalizeProductData, generateVariantKey, sortSizes } from './utils/productUtils';

// --- DATA IMPORT ---
// --- DATA IMPORT --- (Now via masterData.js)
import { MASTER_DATA } from './data/masterData';

// Legacy imports removed (they are in masterData.js now)
// import tunisianetData ...
// import spacenetData ...
// import mytekData ...
// import wikiData ...

// --- MASTER LIST REMOVED (Imported) ---

// --- COMPONENTS ---

// --- FILTER SECTION REMOVED (Extracted to components/FilterSection.jsx) ---
import FilterSection from './components/FilterSection';

// --- PRODUCT CARD COMPONENT (Step 17) ---
// --- PRODUCT CARD COMPONENT (Step 17) ---
// --- HELPER: STORE LOGO MAPPING (Step 37) ---
// --- HELPER: STORE LOGO MAPPING (Step 37) ---
import ProductCard from './ProductCard';


// --- PRODUCTS PAGE COMPONENT ---
const ProductsPage = () => {
  const navigate = useNavigate();
  const { addToCompare, compareList, removeFromCompare, isInCompare } = useCompare();
  // WISHLIST HOOK USE (Step 19)
  const { toggleWishlist, isInWishlist, wishlist } = useWishlist();

  // Step 2: Normalize Data immediately
  const [cleanData, setCleanData] = useState(() => normalizeProductData(MASTER_DATA));
  
  // Force Data Refresh on Mount (To fix stale HMR data)
  useEffect(() => {
     console.log("--- PRODUCTS PAGE LOADED V3 - CSS SHOULD BE VISIBLE ---");
     // Filter OUT Mobiles/Tablets for this view (Computers Only)
     const params = new URLSearchParams(window.location.search);
     const categoryParam = params.get('category'); // Checking for active category linkage

     const validData = MASTER_DATA.filter(p => {
        const cat = (p.category || '').toLowerCase();
        const t = (p.title || '').toLowerCase();
        const source = (p.source || '');

        // 1. GLOBAL EXCLUSION: Mobiles/Tablets (Always hide these from ProductsPage)
        if (cat === 'smartphone' || cat === 'tablet' || cat === 'feature phone' || cat === 'mobile') return false;
        if (p.id && p.id.toString().includes('MK-MOB')) return false;
        if (t.includes('galaxy s') && !t.includes('book') && !t.includes('tab')) return false;

        // 2. CONDITIONAL INCLUSION: Components
        // If we are navigating to a specific component category (e.g. ?category=cpu), SHOW IT.
        // Otherwise (default view), HIDE "TechnoPrice Components" to keep "Computer Page" clean.
        
        if (source === 'TechnoPrice Components') {
            // If URL has a category param, we check if this product matches it.
            // If match -> Keep it.
            // If no category param -> Hide it (Default to Computers only).
            if (categoryParam) {
                 // Loose match: if param is 'cpu', product category 'cpu' matches.
                 // Also handling arrays if multiple cats selected (future proofing)
                 const activeCats = categoryParam.split(',').map(c => c.toLowerCase());
                 return activeCats.includes(cat);
            } else {
                 return false; // Hide components from default view
            }
        }

        return true; // Keep Laptops/Desktops
     });
     
     const fresh = normalizeProductData(validData);
     setCleanData(fresh);
  }, []);

  // State initialization
  const [displayedProducts, setDisplayedProducts] = useState(cleanData);
  
  // Grouping State
  const [isGroupView, setIsGroupView] = useState(false);
  const [groupedProducts, setGroupedProducts] = useState([]);
  const [selectedGroup, setSelectedGroup] = useState(null); // For Modal
  const [searchQuery, setSearchQuery] = useState("");  
  const [debouncedSearchQuery, setDebouncedSearchQuery] = useState("");
  const [sortOption, setSortOption] = useState("default"); 
  const [quickLookProduct, setQuickLookProduct] = useState(null); 
  
  // Step 20: Favorites View Mode
  const [viewFavorites, setViewFavorites] = useState(false);
  const [isComparing, setIsComparing] = useState(false); // Step 26: Full Screen Comparison State
  const [priceAlertProduct, setPriceAlertProduct] = useState(null); // Step 29: Alert Logic
  
  // Price State
  const [priceRange, setPriceRange] = useState({ min: 0, max: 20000 });
  const [debouncedPriceRange, setDebouncedPriceRange] = useState({ min: 0, max: 20000 });

  const [historyProduct, setHistoryProduct] = useState(null); // Step 40: Price History Modal

  // Filter State
  const [filters, setFilters] = useState({
    brand: [], category: [], cpu: [], gpu: [], ram: [], storage: [], 
    hz: [], screen: [], res: [], panel: [], os: [], store: []
  });

  // Price Debounce (Step 6)
  useEffect(() => {
    const handler = setTimeout(() => {
        setDebouncedPriceRange(priceRange);
    }, 300);
    return () => clearTimeout(handler);
  }, [priceRange]);

  // Search Debounce (Step 9)
  useEffect(() => {
      const handler = setTimeout(() => {
          setDebouncedSearchQuery(searchQuery);
      }, 200);
      return () => clearTimeout(handler);
  }, [searchQuery]);
  
  // Pagination State (Step 23: Load More Logic)
  const [visibleCount, setVisibleCount] = useState(12); // Start with 12 items
  // const itemsPerPage = 24; // REMOVED
  
  // Scroll to Top State (Step 36)
  const [showScrollButton, setShowScrollButton] = useState(false);
  
  // Stock Filter State (Step 38)
  const [showOnlyInStock, setShowOnlyInStock] = useState(false);

  useEffect(() => {
      const handleScroll = () => {
          if (window.scrollY > 400) {
              setShowScrollButton(true);
          } else {
              setShowScrollButton(false);
          }
      };
      
      window.addEventListener("scroll", handleScroll);
      return () => window.removeEventListener("scroll", handleScroll);
  }, []);


  // --- INTELLIGENT COUNTS (Step 8) ---
  const getCounts = (key) => {
      // 1. Get base data (filtered by STORE only, or all if no store selected)
      let baseData = cleanData;
      if (filters.store.length > 0) {
          baseData = cleanData.filter(p => filters.store.includes(p.source));
      }

      // 2. Count Occurrences
      const counts = {};
      baseData.forEach(p => {
          // Special handling for nested specs vs top-level (brand/source)
          const val = key === 'brand' ? p.brand : (p.specs[key] || 'Unknown');
          counts[val] = (counts[val] || 0) + 1;
      });
      return counts;
  };

  const filterOptions = {
    // ... existing options ...
    store: [...new Set(cleanData.map(p => p.source))].sort(),
    brand: [...new Set(cleanData.map(p => p.brand))].sort(),
    category: [...new Set(cleanData.map(p => p.specs.category || 'Unknown'))].sort(),
    cpu: [...new Set(cleanData.map(p => p.specs.cpu || 'Unknown'))].sort(),
    gpu: [...new Set(cleanData.map(p => p.specs.gpu || 'Unknown'))].sort(),
    ram: sortSizes([...new Set(cleanData.map(p => p.specs.ram || 'Unknown'))]), // FIX: Numeric Sort
    storage: sortSizes([...new Set(cleanData.map(p => p.specs.storage || 'Unknown'))]), // FIX: Numeric Sort
    hz: [...new Set(cleanData.map(p => p.specs.hz || 'Unknown'))].sort(),
    screen: [...new Set(cleanData.map(p => p.specs.screen || 'Unknown'))].sort(),
    res: [...new Set(cleanData.map(p => p.specs.res || 'Unknown'))].sort(),
    panel: [...new Set(cleanData.map(p => p.specs.panel || 'Unknown'))].sort(),
    os: [...new Set(cleanData.map(p => p.specs.os || 'Unknown'))].sort()
  };

  // Filter Handler
  const toggleFilter = (key, value) => {
    setFilters(prev => {
      const current = prev[key];
      const updated = current.includes(value) 
          ? current.filter(i => i !== value)
          : [...current, value];
      return { ...prev, [key]: updated };
    });
  };

  const resetAll = () => {
    setFilters({ brand: [], category: [], cpu: [], gpu: [], ram: [], storage: [], hz: [], screen: [], res: [], panel: [], os: [], store: [] });
    setPriceRange({ min: 0, max: 20000 });
    setSearchQuery("");
    setViewFavorites(false); // Reset favorites view too
  };

  // --- FILTER ENGINE (Step 3 & 4) ---
  const getFilteredProducts = () => {
      let result = cleanData;

      // 1. Store Filter (Step 10: Multi-Select Logic)
      if (filters.store.length > 0) {
          // OR logic: Keep if product source matches ANY selected store
          result = result.filter(p => filters.store.includes(p.source));
      }

      // 2. Brand Filter (Step 10: Multi-Select Logic)
      if (filters.brand.length > 0) {
          // Strict Filtering (Step 21.1 Final Fix)
          const selectedBrands = filters.brand; // Use raw brands, we compare dynamically
          result = result.filter(p => 
              p.brand && selectedBrands.some(b => b.toLowerCase() === p.brand.toLowerCase())
          );
      }

      // 3. Price Filter (Step 4 & 6)
      result = result.filter(p => {
        const price = parseFloat(p.price || 0);
        return price >= debouncedPriceRange.min && price <= debouncedPriceRange.max;
      });

      // 4. Specs Filter
      const specKeys = ['category', 'cpu', 'gpu', 'ram', 'storage', 'hz', 'screen', 'res', 'panel', 'os'];
      specKeys.forEach(key => {
        if (filters[key].length > 0) {
          result = result.filter(p => {
             const val = p.specs[key] || 'Unknown';
             return filters[key].includes(val);
          });
        }
      });

      return result;
  };

  // --- THE STABLE FILTER LOGIC (useEffect) ---
  useEffect(() => {
    // 0. The Purge (Step 9.9 - Dependency Fix)
    setDisplayedProducts([]); 

    let result;

    // Step 20: Favorites Mode Check
    if (viewFavorites) {
        // Source from Wishlist IDs matched against Clean Data (to ensure fresh data)
        const wishlistIds = wishlist.map(w => w.id);
        result = cleanData.filter(p => wishlistIds.includes(p.id));
    } else {
        // 1. Run the Base Filter Engine (Store, Brand, Specs, Price)
        result = getFilteredProducts();
    }

    // 1.5 Stock Filter (Step 38)
    if (showOnlyInStock) {
        result = result.filter(p => p.availability === 'in-stock');
    }

    // 2. Search Logic Override (Final Authority)
    // We allow search to work INSIDE favorites too if needed, or keeping it separate. 
    // User asked "Do all other laptops disappear...". 
    // Let's apply search ONLY if not in favorites mode OR if user insists. 
    // Actually, usually you might want to search your favorites. Let's allow it.
    const currentSearch = searchQuery.toLowerCase().trim();
    
    if (currentSearch !== '') {
        if (currentSearch.includes('ryzen')) {
             // Force Ryzen Only
             result = result.filter(p => p.title.toLowerCase().includes('ryzen'));
        } else {
             // General Search
             result = result.filter(p => 
                (p.title && p.title.toLowerCase().includes(currentSearch)) || 
                (p.brand && p.brand.toLowerCase().includes(currentSearch)) ||
                (p.description && p.description.toLowerCase().includes(currentSearch))
             );
        }
    }

    // 3. Sort the Results
    let sortedResult = [...result];
    if (sortOption === "price-asc") sortedResult.sort((a, b) => parseFloat(a.price) - parseFloat(b.price));
    else if (sortOption === "price-desc") sortedResult.sort((a, b) => parseFloat(b.price) - parseFloat(a.price));
    else if (sortOption === "name-asc") sortedResult.sort((a, b) => a.title.localeCompare(b.title));
    else if (sortOption === "discount-desc") {
        sortedResult.sort((a, b) => {
            const priceA = parseFloat(a.price) || 0;
            const oldA = parseFloat(a.oldPrice) || 0;
            const discountA = (oldA > priceA && oldA > 0) ? ((oldA - priceA) / oldA) : 0;
            
            const priceB = parseFloat(b.price) || 0;
            const oldB = parseFloat(b.oldPrice) || 0;
            const discountB = (oldB > priceB && oldB > 0) ? ((oldB - priceB) / oldB) : 0;
            
            return discountB - discountA; // Descending (Higher discount first)
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

    // --- GROUPING LOGIC (New) ---
    if (isGroupView) {
        const groups = {};
        sortedResult.forEach(p => {
             const key = generateVariantKey(p);
             if (!groups[key]) {
                 groups[key] = {
                     ...p, // INHERIT ALL PROPS (Title, Image, Brand, Specs) from first item
                     key,
                     baseProduct: p,
                     variants: [],
                     minPrice: p.price,
                     maxPrice: p.price,
                     id: `group-${key}`, // Synthetic ID
                     isGroup: true // Flag for Card to maybe show "3 Variants" etc.
                 };
             }
             groups[key].variants.push(p);
             
             // Update min/max prices and base product (thumbnail)
             // If we find a cheaper variant, that becomes the "Face" of the group
             if (p.price < groups[key].minPrice) {
                 groups[key].minPrice = p.price;
                 groups[key].baseProduct = p;
                 groups[key].price = p.price;
                 
                 // Update Visuals to match the Cheapest Option
                 groups[key].title = p.title;
                 groups[key].image = p.image;
                 groups[key].brand = p.brand;
                 groups[key].source = p.source;
                 groups[key].specs = p.specs;
             }
             if (p.price > groups[key].maxPrice) groups[key].maxPrice = p.price;
        });
        setDisplayedProducts(Object.values(groups));
    } else {
        setDisplayedProducts(sortedResult);
    }

    setVisibleCount(12); // Reset to top
  }, [filters, debouncedPriceRange, searchQuery, sortOption, cleanData, viewFavorites, wishlist, showOnlyInStock, isGroupView]);

  // Pagination Logic (Step 23: Load More Slicing)
  const currentItems = displayedProducts.slice(0, visibleCount);
  
  // const totalPages = Math.ceil(displayedProducts.length / itemsPerPage); // REMOVED
  // const paginate = (pageNumber) => setCurrentPage(pageNumber); // REMOVED

  // --- COMPARE LOGIC (Step 24) ---
  const toggleCompare = (product) => {
    if (compareList.some(p => p.id === product.id)) {
        removeFromCompare(product.id);
    } else {
        addToCompare(product);
    }
  };

  // --- DEEP LINKING LOGIC (Step 28) ---
  const { setCompareList } = useCompare(); // Ensure this is destructured



  useEffect(() => {
    try {
        const params = new URLSearchParams(window.location.search);
        
        // 1. Handle Compare Links
        const compareIds = params.get('compare');
        if (compareIds) {
            const ids = compareIds.split(',');
            // STABILITY FIX: Use MASTER_DATA directly to ensure products are found even before state settles
            const rawFound = MASTER_DATA.filter(p => ids.includes(p.id));
            
            if (rawFound.length > 0) {
                // Normalize on the fly to match the app's data structure
                const cleanFound = normalizeProductData(rawFound);
                setCompareList(cleanFound);
                setIsComparing(true);
            } else {
                 console.warn("No products found for comparison link:", ids);
            }
        }

        // 2. Handle Filter Links (Category, Brand, etc.)
        const categoryParam = params.get('category');
        if (categoryParam) {
            // Support explicit "category" param mapping to the filter state
            // If comma separated, split it
            const categories = categoryParam.split(',');
            setFilters(prev => ({ ...prev, category: categories }));
        }

    } catch (error) {
          console.error("Error parsing URL parameters:", error);
    }
  }, [setCompareList]); // Run once on mount (effectively)

  // Move isInCompare directly to hook destructuring


  // --- FULL SCREEN VIEW LOGIC (Step 26) ---
  if (isComparing) {
      return <ComparisonView 
                selectedProducts={compareList} 
                onClose={() => setIsComparing(false)} 
                removeFromCompare={removeFromCompare}
             />;
  }

  return (
    <div 
        className="products-layout-final" 
        style={{
            backgroundColor: '#E8F1F5',
            minHeight: '100vh',
            display: 'grid',
            gridTemplateColumns: '240px 1fr',
            color: '#1A2B48',
            fontFamily: "'Inter', sans-serif"
        }}
    >
      <style>{`
        /* --- INJECTED CRITICAL STYLES (THE NUCLEAR OPTION) --- */
        .products-layout-final {
            display: grid;
            grid-template-columns: 240px 1fr;
            min-height: 100vh;
            background-color: #E8F1F5 !important;
            background-image: none !important;
            background-attachment: fixed;
            color: #1A2B48;
            font-family: 'Inter', system-ui, -apple-system, sans-serif;
        }

        .products-main {
            background: transparent !important;
            padding: 20px 40px;
        }

        .sidebar {
            height: 100vh;
            position: sticky;
            top: 0;
            display: flex;
            flex-direction: column;
            background: white !important;
            backdrop-filter: blur(12px) !important;
            z-index: 50;
            border-right: 1px solid #e2e8f0 !important;
        }

        /* RESET CHILDREN */
        .sidebar-header, .filter-header-row, .scroll-filters, .filter-section {
            background: transparent !important;
            border-color: #e2e8f0 !important;
        }

        /* CARD GLASSMORPHISM ENFORCER */
        .product-card-glass {
            background: white !important;
            backdrop-filter: blur(10px) !important;
            border: 1px solid #e2e8f0 !important;
            border-radius: 20px !important;
            color: #1A2B48 !important;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03) !important;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
            padding: 15px; /* Ensure padding if missing from CSS file */
        }

        .product-card-glass:hover {
            transform: translateY(-5px) !important;
            box-shadow: 0 20px 40px -12px rgba(0, 0, 0, 0.15) !important;
            border-color: #5F8D8B !important;
        }

        .product-card-glass h3 { color: #1A2B48 !important; }

        /* SCROLLBAR */
        ::-webkit-scrollbar { width: 8px; }
        ::-webkit-scrollbar-track { background: #E8F1F5; }
        ::-webkit-scrollbar-thumb { background: #94a3b8; border-radius: 4px; }
        ::-webkit-scrollbar-thumb:hover { background: #64748b; }
      `}</style>
        <aside className="filters-sidebar">
            <div className="sidebar">
                <div className="sidebar-header">
                    {filters.category && filters.category.length > 0 ? (
                        <Link to="/components" className="home-link">
                            <ArrowLeft size={20} />
                            <span>Back to Components</span>
                        </Link>
                    ) : (
                        <Link to="/" className="home-link">
                            <Home size={20} />
                            <span>Home Page</span>
                        </Link>
                    )}
                </div>

                <div className="filter-header-row">
                    <h3>Filters</h3>
                    <button onClick={resetAll} className="reset-btn"><RefreshCw size={14} /> Reset</button>
                </div>

                <div className="scroll-filters">
                    <FilterSection 
                        title="Vendeur (Store)" 
                        options={filterOptions.store} 
                        selected={filters.store} 
                        onSelect={(v) => toggleFilter('store', v)} 
                        isOpen={true} 
                        onClear={() => setFilters(prev => ({ ...prev, store: [] }))}
                    />
                    
                    <FilterSection title="Price Range" isOpen={true}>
                        <div className="price-inputs">
                            <input type="number" value={priceRange.min} onChange={(e) => setPriceRange({...priceRange, min: Number(e.target.value)})} />
                            <span>to</span>
                            <input type="number" value={priceRange.max} onChange={(e) => setPriceRange({...priceRange, max: Number(e.target.value)})} />
                        </div>
                    </FilterSection>

                    <FilterSection title="Brand" options={filterOptions.brand} selected={filters.brand} onSelect={(v) => toggleFilter('brand', v)} isOpen={true} counts={getCounts('brand')} disableZero={true} onClear={() => setFilters(prev => ({ ...prev, brand: [] }))} />
                    <FilterSection title="CPU" options={filterOptions.cpu} selected={filters.cpu} onSelect={(v) => toggleFilter('cpu', v)} counts={getCounts('cpu')} disableZero={true} onClear={() => setFilters(prev => ({ ...prev, cpu: [] }))} />
                    <FilterSection title="RAM" options={filterOptions.ram} selected={filters.ram} onSelect={(v) => toggleFilter('ram', v)} counts={getCounts('ram')} disableZero={true} onClear={() => setFilters(prev => ({ ...prev, ram: [] }))} />
                    <FilterSection title="Storage" options={filterOptions.storage} selected={filters.storage} onSelect={(v) => toggleFilter('storage', v)} counts={getCounts('storage')} disableZero={true} onClear={() => setFilters(prev => ({ ...prev, storage: [] }))} />
                    <FilterSection title="Screen Size" options={filterOptions.screen} selected={filters.screen} onSelect={(v) => toggleFilter('screen', v)} counts={getCounts('screen')} disableZero={true} onClear={() => setFilters(prev => ({ ...prev, screen: [] }))} />
                    <FilterSection title="GPU" options={filterOptions.gpu} selected={filters.gpu} onSelect={(v) => toggleFilter('gpu', v)} counts={getCounts('gpu')} disableZero={true} onClear={() => setFilters(prev => ({ ...prev, gpu: [] }))} />
                    <FilterSection title="Category" options={filterOptions.category} selected={filters.category} onSelect={(v) => toggleFilter('category', v)} counts={getCounts('category')} disableZero={true} onClear={() => setFilters(prev => ({ ...prev, category: [] }))} />
                    <FilterSection title="Systeme (OS)" options={filterOptions.os} selected={filters.os} onSelect={(v) => toggleFilter('os', v)} counts={getCounts('os')} disableZero={true} onClear={() => setFilters(prev => ({ ...prev, os: [] }))} />
                    <FilterSection title="Refresh Rate" options={filterOptions.hz} selected={filters.hz} onSelect={(v) => toggleFilter('hz', v)} counts={getCounts('hz')} disableZero={true} onClear={() => setFilters(prev => ({ ...prev, hz: [] }))} />
                </div>
            </div>
        </aside>

        <main className="products-main">
            <div className="products-header">
                <h1 style={{ background: 'linear-gradient(to right, #1A2B48, #475569)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent', fontSize: '2.5rem' }}>
                    PREMIUM MARKETPLACE
                </h1>
                <p className="subtitle" style={{ color: '#5F8D8B' }}>
                    <span style={{ fontWeight: 'bold' }}>Active: {displayedProducts.length} Items</span> • Top Laptops from Tunisianet, MyTek, Wiki & Spacenet
                </p>
            </div>

            <div className="top-toolbar">
                <div className="search-box">
                    <Search size={18} />
                    <input type="text" placeholder="Search by name..." value={searchQuery} onChange={(e) => setSearchQuery(e.target.value)} />
                </div>
                
                {/* Grouping Toggle (New) */}
                <button 
                    onClick={() => setIsGroupView(!isGroupView)}
                    style={{
                        background: isGroupView ? '#5F8D8B' : 'white',
                        color: isGroupView ? '#fff' : '#1A2B48',
                        border: '1px solid #e2e8f0',
                        borderRadius: '8px',
                        padding: '0 15px',
                        cursor: 'pointer',
                        fontWeight: '600',
                        display: 'flex',
                        alignItems: 'center',
                        gap: '8px',
                        marginLeft: '15px',
                        transition: 'all 0.3s ease'
                    }}
                >
                    {isGroupView ? <Scale size={18} /> : <Laptop size={18} />}
                    {isGroupView ? "Ungroup" : "Group"}
                </button>
                
                {/* FAVORITES TOGGLE (Step 20) */}
                 <button 
                    onClick={() => setViewFavorites(!viewFavorites)}
                    className="favorites-toggle-btn"
                    style={{
                        display: 'flex',
                        alignItems: 'center',
                        gap: '8px',
                        background: viewFavorites ? '#ff0055' : 'white',
                        color: viewFavorites ? 'white' : '#475569',
                        border: 'none',
                        padding: '8px 16px',
                        borderRadius: '8px',
                        cursor: 'pointer',
                        fontWeight: '600',
                        marginLeft: '20px',
                        transition: 'all 0.3s ease'
                    }}
                 >
                    <Heart size={18} fill={viewFavorites ? "white" : "none"} />
                    {viewFavorites ? "Show All" : "Show Favorites"}
                 </button>

                {/* HERO HEART LINK IN HEADER (Updated Step 19) */}
                <Link to="/wishlist" 
                    onClick={(e) => { e.preventDefault(); setViewFavorites(!viewFavorites); }}
                    className="header-heart-link" style={{
                    color: viewFavorites ? '#ff0055' : '#1A2B48', 
                    display: 'flex', 
                    alignItems: 'center', 
                    gap: '8px',
                    textDecoration: 'none',
                    marginRight: 'auto',
                    marginLeft: '20px'
                }}>
                    <Heart size={24} color={viewFavorites ? "#ff0055" : "#ff0055"} fill={viewFavorites ? "#ff0055" : "none"} />
                    <span style={{fontWeight:'bold', fontSize:'0.9rem'}}>Wishlist ({wishlist.length})</span>
                </Link>

                <div className="sort-box">
                    <ArrowUpDown size={18} />
                    <select value={sortOption} onChange={(e) => setSortOption(e.target.value)}>
                        <option value="default">Sort By: Featured</option>
                        <option value="price-asc">Price: Low to High</option>
                        <option value="price-desc">Price: High to Low</option>
                        <option value="name-asc">Name: A to Z</option>
                        <option value="discount-desc">Biggest Discount</option>
                        <option value="value-ram">Best Value (Price/RAM)</option>
                    </select>
                </div>
            </div>

            {/* --- STORE FILTER BAR (Step 31) --- */}
            <div className="store-filter-bar" style={{
                display: 'flex',
                overflowX: 'auto',
                gap: '10px',
                padding: '10px 0',
                margin: '0 20px 10px',
                scrollbarWidth: 'none', /* Firefox */
                msOverflowStyle: 'none'  /* IE 10+ */
            }}>
                <style>{`
                    .store-filter-bar::-webkit-scrollbar { 
                        display: none; 
                    }
                `}</style>
                {/* 'All Stores' Option */}
                <button
                    onClick={() => setFilters(prev => ({ ...prev, store: [] }))}
                    style={{
                        padding: '8px 16px',
                        borderRadius: '20px',
                        border: filters.store.length === 0 ? '1px solid #5F8D8B' : '1px solid #e2e8f0',
                        background: filters.store.length === 0 ? '#5F8D8B' : 'white',
                        color: filters.store.length === 0 ? 'white' : '#1A2B48',
                        cursor: 'pointer',
                        whiteSpace: 'nowrap',
                        fontWeight: filters.store.length === 0 ? '600' : '400',
                        transition: 'all 0.2s'
                    }}
                >
                    All Stores
                </button>

                {filterOptions.store.map(store => (
                    <button
                        key={store}
                        onClick={() => toggleFilter('store', store)}
                        style={{
                            padding: '8px 16px',
                            borderRadius: '20px',
                            border: filters.store.includes(store) ? '1px solid #5F8D8B' : '1px solid #e2e8f0',
                            background: filters.store.includes(store) ? '#5F8D8B' : 'white',
                            color: filters.store.includes(store) ? 'white' : '#1A2B48',
                            cursor: 'pointer',
                            whiteSpace: 'nowrap',
                            display: 'flex',
                            alignItems: 'center',
                            gap: '8px',
                            fontWeight: filters.store.includes(store) ? '600' : '400',
                             transition: 'all 0.2s'
                        }}
                    >
                        <span>{store.charAt(0).toUpperCase() + store.slice(1)}</span>
                        {filters.store.includes(store) && <X size={12} />}
                    </button>
                ))}
            </div>

            {/* --- BRAND FILTER BAR (Step 34) --- */}
            <div className="brand-filter-bar" style={{
                display: 'flex',
                overflowX: 'auto',
                gap: '8px',
                padding: '0 0 10px',
                margin: '0 20px 10px',
                scrollbarWidth: 'none',
                msOverflowStyle: 'none'
            }}>
                <style>{`
                    .brand-filter-bar::-webkit-scrollbar { display: none; }
                `}</style>
                {/* 'All Brands' Pill */}
                 <button
                    onClick={() => setFilters(prev => ({ ...prev, brand: [] }))}
                    style={{
                        padding: '6px 14px',
                        borderRadius: '16px',
                        border: filters.brand.length === 0 ? '1px solid #5F8D8B' : '1px solid #e2e8f0',
                        background: filters.brand.length === 0 ? '#5F8D8B' : 'white',
                        color: filters.brand.length === 0 ? 'white' : '#1A2B48',
                        cursor: 'pointer',
                        whiteSpace: 'nowrap',
                        fontSize: '0.85rem',
                        fontWeight: filters.brand.length === 0 ? '600' : '400',
                        transition: 'all 0.2s'
                    }}
                >
                    All Brands
                </button>

                {filterOptions.brand.map(brand => (
                    <button
                        key={brand}
                        onClick={() => toggleFilter('brand', brand)}
                        style={{
                            padding: '6px 14px',
                            borderRadius: '16px',
                            border: filters.brand.includes(brand) ? '1px solid #5F8D8B' : '1px solid #e2e8f0',
                            background: filters.brand.includes(brand) ? '#5F8D8B' : 'white',
                            color: filters.brand.includes(brand) ? 'white' : '#475569',
                            cursor: 'pointer',
                            whiteSpace: 'nowrap',
                            display: 'flex',
                            alignItems: 'center',
                            gap: '6px',
                            fontSize: '0.85rem',
                            fontWeight: filters.brand.includes(brand) ? '600' : '400',
                             transition: 'all 0.2s'
                        }}
                    >
                        <span>{brand}</span>
                        {filters.brand.includes(brand) && <X size={10} />}
                    </button>
                ))}
            </div>

            {/* --- RESULTS COUNT & RESET (Step 35) --- */}
            <div className="results-count-bar" style={{
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
                margin: '0 20px 15px',
                padding: '0 5px'
            }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '15px' }}>
                    <span style={{ fontSize: '13px', color: '#64748b' }}>
                        {displayedProducts.length} laptops found
                    </span>

                    {/* Step 38: In-Stock Toggle */}
                    <label style={{ display: 'flex', alignItems: 'center', gap: '8px', cursor: 'pointer' }}>
                        <div style={{ position: 'relative', width: '32px', height: '18px' }}>
                            <input 
                                type="checkbox" 
                                checked={showOnlyInStock}
                                onChange={(e) => setShowOnlyInStock(e.target.checked)}
                                style={{ opacity: 0, width: 0, height: 0 }}
                            />
                            <div style={{
                                position: 'absolute', cursor: 'pointer',
                                top: 0, left: 0, right: 0, bottom: 0,
                                backgroundColor: showOnlyInStock ? '#10b981' : '#ccc',
                                transition: '0.4s', borderRadius: '18px'
                            }}></div>
                            <div style={{
                                position: 'absolute',
                                content: '""',
                                height: '14px', width: '14px',
                                left: showOnlyInStock ? '16px' : '2px',
                                bottom: '2px',
                                backgroundColor: 'white',
                                transition: '0.4s', borderRadius: '50%'
                            }}></div>
                        </div>
                        <span style={{ fontSize: '13px', color: '#475569' }}>In Stock Only</span>
                    </label>
                </div>
                
                {(filters.store.length > 0 || filters.brand.length > 0 || searchQuery || filters.cpu.length > 0) && (
                    <button 
                        onClick={resetAll}
                        style={{
                            background: 'transparent',
                            border: 'none',
                            color: '#64748b',
                            cursor: 'pointer',
                            fontSize: '13px',
                            display: 'flex',
                            alignItems: 'center',
                            gap: '5px'
                        }}
                    >
                        <Trash2 size={13} />
                        Clear All Filters
                    </button>
                )}
            </div>

            {/* --- ACTIVE FILTERS CHIPS (Step 7) --- */}
            {/* --- ACTIVE FILTERS PILLS (Step 22) --- */}
            {(filters.store.length > 0 || filters.brand.length > 0 || searchQuery) && !viewFavorites && (
              <div className="active-filters-row">
                {/* Search Pill */}
                {searchQuery && (
                    <div className="filter-chip" onClick={() => setSearchQuery("")} style={{ borderColor: '#5F8D8B', color: '#5F8D8B' }}>
                        Search: "{searchQuery}"
                        <X size={14} />
                    </div>
                )}

                {/* Store Pills */}
                {filters.store.map(store => (
                  <div key={store} className="filter-chip" onClick={() => toggleFilter('store', store)}>
                    {store === 'spacenet' ? 'Spacenet' : 
                     store === 'mytek' ? 'MyTek' : 
                     store === 'wiki' ? 'Wiki' : 'Tunisianet'}
                    <X size={14} />
                  </div>
                ))}

                {/* Brand Pills */}
                {filters.brand.map(brand => (
                  <div key={brand} className="filter-chip" onClick={() => toggleFilter('brand', brand)}>
                    {brand}
                    <X size={14} />
                  </div>
                ))}

                {/* Clear All Button */}
                <button 
                    onClick={resetAll}
                    style={{
                        background: 'transparent',
                        border: 'none',
                        color: '#64748b',
                        textDecoration: 'underline',
                        cursor: 'pointer',
                        fontSize: '0.85rem',
                        marginLeft: '10px'
                    }}
                >
                    Clear All
                </button>
              </div>
            )}



            <div className="grid" style={{
                display: 'grid', 
                gridTemplateColumns: 'repeat(4, minmax(0, 1fr))', 
                gap: '20px',
                paddingBottom: '60px'
            }}>
                {(() => {
                    // Step 30: Calculate Best Deal in current view
                    // Filter out 0 or invalid prices first
                    const validPrices = displayedProducts
                        .map(p => p.price)
                        .filter(p => typeof p === 'number' && p > 0);
                        
                    const globalMinPrice = validPrices.length > 0 ? Math.min(...validPrices) : 0;
                    
                    return currentItems.map(item => {
                         // Determine if it's a Group or a Product
                         // Robust check: Render as group if it has variants, regardless of view mode (handles state transitions)
                         const isGroup = item.variants && Array.isArray(item.variants);
                         
                         if (isGroup) {
                             // --- GROUP CARD RENDERING (Step 31 Update) ---
                             // We now treat the group object itself as a "product" because we synthesized 
                             // all the visual props (title, image, price) onto it in the grouping step.
                             return (
                                <ProductCard 
                                    key={item.id} 
                                    product={item} 
                                    addToCompare={addToCompare}
                                    toggleWishlist={toggleWishlist}
                                    isFavorite={isInWishlist(item.id)}
                                    isInCompare={isInCompare(item.id)}
                                    // Custom handler for "View" button to go to Details Group
                                    isGroupCard={true} 
                                    groupCount={item.variants.length}
                                    onGroupSelect={() => navigate(`/group/${encodeURIComponent(item.key)}`)}
                                />
                             );
                         } else {
                             // Render Standard ProductCard
                             return (
                                <ProductCard 
                                    key={item.id || item.link} 
                                    product={item} 
                                    isFavorite={wishlist.some(w => w.id === item.id)}
                                    toggleWishlist={toggleWishlist}
                                    addToCompare={toggleCompare}
                                    isInCompare={isInCompare(item.id)}
                                    isBestDeal={item.price === globalMinPrice && item.price > 0}
                                    onShowHistory={setHistoryProduct}
                                />
                             );
                         }
                    });
                })()}
            </div>

            {/* --- LOAD MORE BUTTON (Step 23) --- */}
            {displayedProducts.length > visibleCount && (
                <div className="pagination" style={{ marginTop: '40px', display: 'flex', justifyContent: 'center' }}>
                    <button 
                        onClick={() => setVisibleCount(prev => prev + 12)}
                        style={{
                            background: 'white',
                            border: '1px solid #10b981',
                            color: '#10b981',
                            padding: '12px 30px',
                            fontWeight: 'bold',
                            borderRadius: '50px',
                            cursor: 'pointer',
                            fontSize: '1rem',
                            display: 'flex',
                            alignItems: 'center',
                            gap: '10px',
                            transition: 'all 0.3s ease',
                            width: 'auto',
                            height: 'auto'
                        }}
                        onMouseEnter={(e) => {
                            e.target.style.background = '#10b981';
                            e.target.style.color = '#020617';
                            e.target.style.boxShadow = '0 0 20px rgba(16, 185, 129, 0.4)';
                        }}
                        onMouseLeave={(e) => {
                            e.target.style.background = 'white';
                            e.target.style.color = '#10b981';
                            e.target.style.boxShadow = 'none';
                        }}
                    >
                        Load More Products ({displayedProducts.length - visibleCount} remaining)
                        <ChevronDown size={20} />
                    </button>
                </div>
            )}  {displayedProducts.length === 0 && (
                <div className="empty-state">
                    {viewFavorites ? (
                        <>
                            <Heart size={48} color="#ff0055" />
                            <p>No favorites yet. Click the heart on products you love!</p>
                        </>
                    ) : (
                        <>
                            <p style={{ color: '#64748b', marginBottom: '30px' }}>Try removing some filters or searching for something less specific.</p>
                            <button
                                onClick={resetAll}
                                style={{
                                    padding: '12px 24px',
                                    background: '#5F8D8B',
                                    color: 'white',
                                    border: 'none',
                                    borderRadius: '8px',
                                    fontWeight: 'bold',
                                    cursor: 'pointer',
                                    fontSize: '1rem'
                                }}
                            >
                                Reset All Filters
                            </button>
                        </>
                    )}
                </div>
            )}
        </main>

      
      {/* Compare Dock */}
      {compareList.length > 0 && (
        <div className="compare-dock">
          <div className="dock-info">
             <Scale size={20} />
             <span>{compareList.length} Items</span>
          </div>
          <div className="dock-thumbs">
             {compareList.map(p => (
                 <div key={p.id} className="dock-thumb" onClick={() => removeFromCompare(p.id)}>
                     <img src={p.image} alt={p.title} />
                     <div className="dock-x"><X size={14}/></div>
                 </div>
             ))}
          </div>
          <button className="compare-action-btn" onClick={() => setIsComparing(true)}>
                Compare Now ({compareList.length}) <ChevronRight size={16} />
            </button>
        </div>
      )}
      
      {quickLookProduct && <QuickLookModal product={quickLookProduct} onClose={() => setQuickLookProduct(null)} />}
      
      {/* --- PRICE ALERT MODAL (Step 29) --- */}
      <PriceAlertModal 
        product={priceAlertProduct} 
        onClose={() => setPriceAlertProduct(null)} 
      />

      {/* --- PRICE HISTORY MODAL (Step 40) --- */}
      <PriceHistoryModal 
        product={historyProduct} 
        onClose={() => setHistoryProduct(null)} 
      />

      {/* --- SCROLL TO TOP BUTTON (Step 36) --- */}
      {showScrollButton && (
          <button
              onClick={() => window.scrollTo({ top: 0, behavior: 'smooth' })}
              style={{
                  position: 'fixed',
                  bottom: '30px',
                  right: '30px',
                  width: '45px',
                  height: '45px',
                  borderRadius: '50%',
                  background: '#5F8D8B',
                  border: 'none',
                  color: 'black',
                  display: 'flex',
                  justifyContent: 'center',
                  alignItems: 'center',
                  boxShadow: '0 4px 15px rgba(95, 141, 139, 0.4)',
                  cursor: 'pointer',
                  zIndex: 50,
                  transition: 'all 0.3s ease',
                  animation: 'fadeIn 0.3s'
              }}
          >
              <ArrowUp size={24} strokeWidth={2.5} />
          </button>
      )}

      {/* --- VARIANT SELECTION MODAL (New) --- */}
      {selectedGroup && (
        <div className="compare-modal-overlay" onClick={() => setSelectedGroup(null)} style={{ zIndex: 9999 }}>
            <div className="compare-modal-content" onClick={e => e.stopPropagation()} style={{ maxWidth: '600px', maxHeight: '80vh', overflowY: 'auto' }}>
                <button className="modal-close-btn" onClick={() => setSelectedGroup(null)}><X size={24} /></button>
                <h2 style={{ color: '#1A2B48', marginBottom: '10px', fontSize: '1.2rem', borderBottom: '1px solid #e2e8f0', paddingBottom: '10px' }}>
                    Select Configuration
                </h2>
                <p style={{ color: '#64748b', marginBottom: '20px', fontSize: '0.9rem' }}>{selectedGroup.key}</p>
                
                <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
                    {selectedGroup.variants.sort((a,b) => a.price - b.price).map((v, idx) => (
                        <div key={idx} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', background: '#f1f5f9', padding: '15px', borderRadius: '10px', border: '1px solid #e2e8f0' }}>
                            <div style={{ flex: 1 }}>
                                <div style={{ color: '#1A2B48', fontWeight: '600', display: 'flex', alignItems: 'center', gap: '10px' }}>
                                    <span>{v.specs.ram} RAM</span>
                                    <span style={{ color: '#94a3b8' }}>/</span>
                                    <span>{v.specs.storage} SSD</span>
                                </div>
                                <div style={{ fontSize: '0.75rem', color: '#64748b', marginTop: '4px' }}>
                                    {v.source} • {v.specs.os}
                                </div>
                            </div>
                            <div style={{ display: 'flex', alignItems: 'center', gap: '15px' }}>
                                <div style={{ color: '#10b981', fontWeight: 'bold', fontSize: '1.1rem' }}>{v.price} TND</div>
                                <a href={v.link} target="_blank" rel="noopener noreferrer" className="dock-btn" style={{ background: '#5F8D8B', color: 'white', border: 'none', textDecoration: 'none', padding: '8px 16px', borderRadius: '6px', fontWeight: 'bold' }}>
                                    View
                                </a>
                            </div>
                        </div>
                    ))}
                </div>
            </div>
        </div>
      )}
    </div>
  );
};

export default ProductsPage;
