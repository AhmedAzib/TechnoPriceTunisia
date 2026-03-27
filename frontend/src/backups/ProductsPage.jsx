import React, { useState, useMemo, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { ChevronDown, ChevronUp, Sliders, Search, ArrowUpDown, Scale, X, Heart, Home, ChevronLeft, ChevronRight, AlertCircle, RefreshCw } from 'lucide-react';
import productData from './data/products.json';
import { useCompare } from './context/CompareContext';
import { useWishlist } from './context/WishlistContext';
import './ProductsPage.css';

// Reusable Collapsible Filter Component
const FilterSection = ({ title, options, selected, onSelect, isOpen = false }) => {
  const [open, setOpen] = useState(isOpen);
  
  return (
    <div className="filter-section">
      <div className="fs-header" onClick={() => setOpen(!open)}>
        <span>{title}</span>
        {open ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
      </div>
      {open && (
        <div className="fs-body">
          {options.map(opt => (
            <label key={opt} className="checkbox-row">
              <input 
                type="checkbox" 
                checked={selected.includes(opt)} 
                onChange={() => onSelect(opt)}
              />
              {opt}
            </label>
          ))}
        </div>
      )}
    </div>
  );
};

const ProductsPage = () => {
  const { addToCompare, compareList, removeFromCompare } = useCompare();
  const { toggleWishlist, isInWishlist, wishlist } = useWishlist();
  
  // --- STATE ---
  const [priceRange, setPriceRange] = useState({ min: 0, max: 20000 });
  const [searchQuery, setSearchQuery] = useState(""); 
  const [sortOption, setSortOption] = useState("default"); 

  // --- PAGINATION STATE ---
  const [currentPage, setCurrentPage] = useState(1);
  const itemsPerPage = 24;

  // Filter State
  const [filters, setFilters] = useState({
    brand: [], category: [], cpu: [], gpu: [], ram: [], storage: [], 
    hz: [], screen: [], res: [], panel: [], os: []
  });

  // Extract Options
  const getOptions = (key) => [...new Set(productData.map(p => p.specs[key] || 'Unknown'))].sort();

  const filterOptions = {
    brand: [...new Set(productData.map(p => p.brand))].sort(),
    category: getOptions('category'),
    cpu: getOptions('cpu'),
    gpu: getOptions('gpu'),
    ram: getOptions('ram'),
    storage: getOptions('storage'),
    hz: getOptions('hz'),
    screen: getOptions('screen'),
    res: getOptions('res'),
    panel: getOptions('panel'),
    os: getOptions('os')
  };

  const toggleFilter = (key, value) => {
    setFilters(prev => {
      const current = prev[key];
      return {
        ...prev,
        [key]: current.includes(value) 
          ? current.filter(i => i !== value)
          : [...current, value]
      };
    });
  };

  // Reset to Page 1 when filters change
  useEffect(() => {
    setCurrentPage(1);
  }, [filters, priceRange, searchQuery, sortOption]);

  const resetAll = () => {
    setFilters({ brand: [], category: [], cpu: [], gpu: [], ram: [], storage: [], hz: [], screen: [], res: [], panel: [], os: [] });
    setPriceRange({ min: 0, max: 20000 });
    setSearchQuery("");
  };

  // --- FILTERING & SORTING LOGIC ---
  const filtered = useMemo(() => {
    // 1. Filter
    let result = productData.filter(p => {
      // Price Check (Min & Max)
      if (p.price < priceRange.min || p.price > priceRange.max) return false;
      
      // Search Query Check
      if (searchQuery && !p.title.toLowerCase().includes(searchQuery.toLowerCase())) return false;

      // Attribute Checks
      for (const key of Object.keys(filters)) {
        const productValue = key === 'brand' ? p.brand : p.specs[key];
        
        if (filters[key].length > 0 && !filters[key].includes(productValue)) {
          return false;
        }
      }
      return true;
    });

    // 2. Sort
    if (sortOption === "price-asc") {
        result.sort((a, b) => a.price - b.price);
    } else if (sortOption === "price-desc") {
        result.sort((a, b) => b.price - a.price);
    } else if (sortOption === "name-asc") {
        result.sort((a, b) => a.title.localeCompare(b.title));
    }
    return result;
  }, [priceRange, filters, searchQuery, sortOption]);

  // --- PAGINATION LOGIC ---
  const indexOfLastItem = currentPage * itemsPerPage;
  const indexOfFirstItem = indexOfLastItem - itemsPerPage;
  const currentItems = filtered.slice(indexOfFirstItem, indexOfLastItem);
  const totalPages = Math.ceil(filtered.length / itemsPerPage);

  const paginate = (pageNumber) => {
    setCurrentPage(pageNumber);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  return (
    <div className="products-layout">
      <aside className="sidebar">
        {/* HOME LINK - EXIT BUTTON */}
        <Link to="/" className="home-link">
            <Home size={20} />
            <span>ANTIGRAVITY STORE</span>
        </Link>

        {/* HEADER WITH FILTERS & WISHLIST */}
        <div className="sidebar-header" style={{ justifyContent: 'space-between' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <Sliders size={18} />
            <span style={{ fontWeight: 'bold' }}>Pro Filters</span>
          </div>
          <Link to="/wishlist" className="heart-link" title="My Wishlist">
            <Heart size={20} fill={wishlist.length > 0 ? "#ff0055" : "none"} color={wishlist.length > 0 ? "#ff0055" : "white"} />
            {wishlist.length > 0 && <span style={{ fontSize: '0.8rem' }}>{wishlist.length}</span>}
          </Link>
        </div>
        
        {/* SEARCH BAR */}
        <div className="search-box">
            <Search size={16} className="search-icon"/>
            <input 
                type="text" 
                placeholder="Search model..." 
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
            />
        </div>

        {/* PRICE INPUTS */}
        <div className="price-box">
          <label>Price Range (TND)</label>
          <div className="price-inputs">
            <input 
              type="number" 
              placeholder="Min" 
              value={priceRange.min} 
              onChange={(e) => setPriceRange({ ...priceRange, min: Number(e.target.value) })}
            />
            <span>-</span>
            <input 
              type="number" 
              placeholder="Max" 
              value={priceRange.max} 
              onChange={(e) => setPriceRange({ ...priceRange, max: Number(e.target.value) })}
            />
          </div>
        </div>

        <div className="scroll-filters">
          <FilterSection title="Brand" options={filterOptions.brand} selected={filters.brand} onSelect={v => toggleFilter('brand', v)} isOpen={true} />
          <FilterSection title="Category" options={filterOptions.category} selected={filters.category} onSelect={v => toggleFilter('category', v)} isOpen={true} />
          
          <FilterSection title="Processor" options={filterOptions.cpu} selected={filters.cpu} onSelect={v => toggleFilter('cpu', v)} />
          <FilterSection title="Graphics Card" options={filterOptions.gpu} selected={filters.gpu} onSelect={v => toggleFilter('gpu', v)} />
          <FilterSection title="RAM" options={filterOptions.ram} selected={filters.ram} onSelect={v => toggleFilter('ram', v)} />
          <FilterSection title="Storage" options={filterOptions.storage} selected={filters.storage} onSelect={v => toggleFilter('storage', v)} />
          
          <FilterSection title="Refresh Rate" options={filterOptions.hz} selected={filters.hz} onSelect={v => toggleFilter('hz', v)} />
          <FilterSection title="Screen Size" options={filterOptions.screen} selected={filters.screen} onSelect={v => toggleFilter('screen', v)} />
          <FilterSection title="Resolution" options={filterOptions.res} selected={filters.res} onSelect={v => toggleFilter('res', v)} />
          
          <FilterSection title="Panel Type" options={filterOptions.panel} selected={filters.panel} onSelect={v => toggleFilter('panel', v)} />
          <FilterSection title="Operating System" options={filterOptions.os} selected={filters.os} onSelect={v => toggleFilter('os', v)} />
        </div>
      </aside>

      <main className="catalog">
        {/* HEADER WITH SORT */}
        <header className="catalog-header">
            <h1>Inventory <span className="highlight">({filtered.length})</span></h1>
            <div className="sort-box">
                <ArrowUpDown size={16}/>
                <select onChange={(e) => setSortOption(e.target.value)} value={sortOption}>
                    <option value="default">Relevance</option>
                    <option value="price-asc">Price: Low to High</option>
                    <option value="price-desc">Price: High to Low</option>
                    <option value="name-asc">Name: A-Z</option>
                </select>
            </div>
        </header>

        {/* --- ZERO RESULTS CHECK --- */}
        {filtered.length === 0 ? (
            <div className="empty-state">
                <AlertCircle size={60} color="#334155"/>
                <h2>No Systems Found</h2>
                <p>Try adjusting your filters or search criteria.</p>
                <button onClick={resetAll} className="reset-btn">
                    <RefreshCw size={16}/> Reset Filters
                </button>
            </div>
        ) : (
            <>
                <div className="grid">
                  {currentItems.map(p => (
                    <Link to={`/product/${p.id}`} key={p.id} className="card">
                      <div className="img-box">
                         <img src={p.image} loading="lazy" alt={p.title}/>
                         {p.specs.hz && p.specs.hz !== '60Hz' && <span className="tag">{p.specs.hz}</span>}
                         <button 
                            className="heart-btn" 
                            onClick={(e) => {
                              e.preventDefault();
                              toggleWishlist(p);
                            }}
                         >
                            <Heart size={18} fill={isInWishlist(p.id) ? "#ff0055" : "rgba(0,0,0,0.5)"} color={isInWishlist(p.id) ? "#ff0055" : "black"} />
                         </button>
                      </div>
                      <div className="details">
                        <h4>{p.title}</h4>
                        <div className="specs-mini">
                          <span>{p.specs.cpu}</span> • <span>{p.specs.gpu}</span> • <span>{p.specs.ram}</span>
                        </div>
                        
                        <div className="price-row">
                          <div className="price">{p.price.toFixed(3)} TND</div>
                          <button 
                            className="compare-add-btn" 
                            onClick={(e) => {
                              e.preventDefault();
                              addToCompare(p);
                            }}
                          >
                            + Compare
                          </button>
                        </div>
                      </div>
                    </Link>
                  ))}
                </div>

                {/* --- PAGINATION CONTROLS --- */}
                {totalPages > 1 && (
                    <div className="pagination">
                        <button 
                            disabled={currentPage === 1} 
                            onClick={() => paginate(currentPage - 1)}
                        >
                            <ChevronLeft size={20}/>
                        </button>
                        <span className="page-info">Page {currentPage} of {totalPages}</span>
                        <button 
                            disabled={currentPage === totalPages} 
                            onClick={() => paginate(currentPage + 1)}
                        >
                            <ChevronRight size={20}/>
                        </button>
                    </div>
                )}
            </>
        )}
      </main>

      {/* FLOATING DOCK */}
      {compareList.length > 0 && (
        <div className="compare-dock">
          <div className="dock-info">
            <Scale className="text-neon" />
            <span>{compareList.length} / 3 Selected</span>
          </div>
          <div className="dock-thumbs">
             {compareList.map(p => (
               <div key={p.id} className="dock-thumb">
                 <img src={p.image} alt={p.title} />
                 <div className="dock-x" onClick={() => removeFromCompare(p.id)}>
                   <X size={16}/>
                 </div>
               </div>
             ))}
          </div>
          <Link to="/compare" className="dock-btn">
             COMPARE NOW <ChevronUp size={16}/>
          </Link>
        </div>
      )}
    </div>
  );
};

export default ProductsPage;
