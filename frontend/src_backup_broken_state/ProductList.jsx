import { useState, useEffect } from 'react'
import axios from 'axios'
import { Link, useNavigate, useLocation } from 'react-router-dom'
import { useCompare } from './CompareContext' // <--- IMPORT
import Navbar from './components/Navbar' // <--- IMPORT
import { useAuth } from './AuthContext' // <--- IMPORT

function ProductList() {
  const { addToCompare, compareList, removeFromCompare } = useCompare(); 
  const [products, setProducts] = useState([])
  const [loading, setLoading] = useState(true)
  
  // --- PAGINATION & SORT STATE ---
  const [page, setPage] = useState(1)
  const [totalPages, setTotalPages] = useState(1)
  const [ordering, setOrdering] = useState("price") // default
  
  // --- FILTER STATES ---
  const [searchTerm, setSearchTerm] = useState("")
  const [selectedBrand, setSelectedBrand] = useState("All")
  const [selectedSector, setSelectedSector] = useState("All")
  const [selectedRam, setSelectedRam] = useState("All")
  const [selectedStorage, setSelectedStorage] = useState("All")
  const [selectedCpu, setSelectedCpu] = useState("All")
  const [selectedGpu, setSelectedGpu] = useState("All")
  const [selectedScreen, setSelectedScreen] = useState("All")
  const [selectedPriceRange, setSelectedPriceRange] = useState("All") // <--- NEW STATE

  // --- WISHLIST STATE ---
  const { user } = useAuth()
  const [wishlistMap, setWishlistMap] = useState({})
  useEffect(() => {
    if (user) {
        axios.get('http://127.0.0.1:8000/api/wishlist/')
             .then(res => {
                 const newMap = {};
                 res.data.forEach(item => {
                     newMap[item.product] = item.id;
                 });
                 setWishlistMap(newMap);
             })
             .catch(console.error)
    } else {
        setWishlistMap({});
    }
  }, [user])

  const navigate = useNavigate();
  const location = useLocation();

  const toggleLike = (e, productId) => {
    e.preventDefault(); 
    if (!user) {
        navigate('/login', { state: { from: location } });
        return;
    }

    const wishlistId = wishlistMap[productId];
    if (wishlistId) {
        // DELETE
        const newMap = { ...wishlistMap };
        delete newMap[productId];
        setWishlistMap(newMap); 
        axios.delete(`http://127.0.0.1:8000/api/wishlist/${wishlistId}/`).catch(() => fetchWishlist()); 
    } else {
        // CREATE
        axios.post('http://127.0.0.1:8000/api/wishlist/', { product: productId })
             .then(res => {
                 setWishlistMap(prev => ({ ...prev, [productId]: res.data.id }));
             });
    }
  }

  // --- FETCH PRODUCTS ---
  useEffect(() => {
    setLoading(true)
    const params = {
        page: page,
        ordering: ordering,
        search: searchTerm,
        brand__name: selectedBrand !== "All" ? selectedBrand : undefined,
        sector__name: selectedSector !== "All" ? selectedSector : undefined, // CHANGED from 'sector' to 'sector__name'
        ram: selectedRam !== "All" ? selectedRam : undefined,
        storage: selectedStorage !== "All" ? selectedStorage : undefined,
        cpu: selectedCpu !== "All" ? selectedCpu : undefined,
        gpu: selectedGpu !== "All" ? selectedGpu : undefined,
        screen_size: selectedScreen !== "All" ? selectedScreen : undefined
    }

    // Parse Price Range
    if (selectedPriceRange !== "All") {
        const [min, max] = selectedPriceRange.split("-");
        if (min) params.min_price = min;
        if (max) params.max_price = max;
    }

    // Clean undefined
    Object.keys(params).forEach(key => params[key] === undefined && delete params[key]);

    axios.get('http://127.0.0.1:8000/api/products/', { params })
      .then(response => {
        // Log the raw data to console so we can see it
        console.log("RAW API RESPONSE:", response.data);
        // Check if we received a paginated object (Django default)
        if (response.data.results) {
            console.log("Pagination detected");
            setProducts(response.data.results);
            setTotalPages(Math.ceil(response.data.count / 24));
        } else {
            console.log("No pagination detected, using array directly");
            // Fallback for simple array
            setProducts(response.data);
            // If it's a direct array, assume it's one page or calculate based on length if needed
            // For now, let's assume if it's not paginated, it's just one list.
            // But to avoid "Page 1 of NaN", let's handle it safely:
            const count = Array.isArray(response.data) ? response.data.length : 0;
            setTotalPages(Math.max(1, Math.ceil(count / 24))); 
        }
        setLoading(false)
      })
      .catch(error => {
        console.error("Error fetching data:", error)
        setLoading(false)
      })
  }, [page, ordering, selectedBrand, selectedSector, selectedRam, selectedStorage, selectedCpu, selectedGpu, selectedScreen, selectedPriceRange, searchTerm]) // Dependencies trigger re-fetch

  // Reset page when filters change
  useEffect(() => {
      setPage(1);
  }, [selectedBrand, selectedSector, selectedRam, selectedStorage, selectedCpu, selectedGpu, selectedScreen, selectedPriceRange, searchTerm])


  // --- GET FILTER OPTIONS (Ideally should come from a separate API to show all options even when filtered) ---
  // For now, we extract from current page which is imperfect but works for simple apps. 
  // BETTER: Extract from a separate "all products" call or cached list. 
  // Let's keep it simple: extracting from 'products' locally only shows options for CURRENT PAGE.
  // FIX: The user asked for filtering + pagination. Doing client-side option extraction on paginated data is bad UX (options disappear).
  // Strategy: We will stick to the existing options logic BUT it's flawed with server-side pagination.
  // Ideally we need an endpoint /api/filters/ or load all unique brands once.
  // For this task, I will assume the user accepts that filters might be limited to current view OR I should fetch all filters once.
  // Let's implement a 'Fetch All' for filters once on mount.
  
  const [filterOptions, setFilterOptions] = useState({
      brands: [], sectors: [], rams: [], storages: [], cpus: [], gpus: [], screens: []
  })

  useEffect(() => {
     axios.get('http://127.0.0.1:8000/api/filters/')
        .then(res => {
            const data = res.data;
            
            // Helper for numeric sort (e.g. "16Go" -> 16)
            const parseSize = (s) => {
                if (!s || s === "N/A") return 0;
                return parseFloat(s.replace(/[^0-9.]/g, '')) || 0;
            };

            setFilterOptions({
                brands: ["All", ...data.brands],
                sectors: ["All", ...data.sectors],
                // Apply numeric sort to RAM and Storage since backend sends strings
                rams: ["All", ...data.rams.sort((a,b) => parseSize(a) - parseSize(b))],
                storages: ["All", ...data.storages.sort((a,b) => parseSize(a) - parseSize(b))],
                cpus: ["All", ...data.cpus],
                gpus: ["All", ...data.gpus],
                screens: ["All", ...data.screens]
            })
        })
        .catch(console.error)
  }, [])

  return (
    <div style={{ width: '100%', minHeight: '100vh', backgroundColor: '#f8f9fa', fontFamily: '"Inter", sans-serif' }}>
      
      {/* NAVBAR */}
      <Navbar searchTerm={searchTerm} setSearchTerm={setSearchTerm} />

      <div style={{ display: 'flex', maxWidth: '1400px', margin: '0 auto', padding: '30px' }}>
        
        {/* --- SIDEBAR FILTERS --- */}
        <aside style={{ width: '250px', paddingRight: '30px', flexShrink: 0, height: 'calc(100vh - 100px)', overflowY: 'auto' }}>
          
         {/* PRICE RANGE FILTER */}
          <div style={{ marginBottom: '30px' }}>
            <h3 style={{ fontSize: '1rem', fontWeight: '700', marginBottom: '10px', color: '#333' }}>Price Range (TND)</h3>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', fontSize: '0.9rem', color: '#555' }}>
                <label style={{ cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <input type="radio" checked={selectedPriceRange === "All"} onChange={() => setSelectedPriceRange("All")} /> 
                    All Prices
                </label>
                <label style={{ cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <input type="radio" checked={selectedPriceRange === "-1000"} onChange={() => setSelectedPriceRange("-1000")} /> 
                    Under 1000 TND (Budget)
                </label>
                <label style={{ cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <input type="radio" checked={selectedPriceRange === "1000-1500"} onChange={() => setSelectedPriceRange("1000-1500")} /> 
                    1000 - 1500 TND
                </label>
                <label style={{ cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <input type="radio" checked={selectedPriceRange === "1500-2000"} onChange={() => setSelectedPriceRange("1500-2000")} /> 
                    1500 - 2000 TND
                </label>
                <label style={{ cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <input type="radio" checked={selectedPriceRange === "2000-3000"} onChange={() => setSelectedPriceRange("2000-3000")} /> 
                    2000 - 3000 TND
                </label>
                <label style={{ cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <input type="radio" checked={selectedPriceRange === "3000-"} onChange={() => setSelectedPriceRange("3000-")} /> 
                    Above 3000 TND (Ultra)
                </label>
            </div>
          </div>
          
          <FilterSection title="Brands" options={filterOptions.brands} selected={selectedBrand} setSelected={setSelectedBrand} />
          <FilterSection title="Sectors" options={filterOptions.sectors} selected={selectedSector} setSelected={setSelectedSector} />
          
          <hr style={{margin: '20px 0', border: 'none', borderTop: '1px solid #eee'}} />
          
          <FilterSection title="Graphics Card" options={filterOptions.gpus} selected={selectedGpu} setSelected={setSelectedGpu} />
          <FilterSection title="Processor" options={filterOptions.cpus} selected={selectedCpu} setSelected={setSelectedCpu} />
          <FilterSection title="RAM Memory" options={filterOptions.rams} selected={selectedRam} setSelected={setSelectedRam} />
          <FilterSection title="Storage" options={filterOptions.storages} selected={selectedStorage} setSelected={setSelectedStorage} />
          <FilterSection title="Screen Size" options={filterOptions.screens} selected={selectedScreen} setSelected={setSelectedScreen} />

        </aside>

        {/* CONTENT */}
        <main style={{ flex: 1 }}>
          <div style={{ marginBottom: '20px', color: '#666', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <span>Page <strong>{page}</strong> of {totalPages}</span>
            
            {/* SORT DROPDOWN - New Options */}
            <select 
              value={ordering} 
              onChange={(e) => setOrdering(e.target.value)}
              style={{ padding: '8px 12px', borderRadius: '8px', border: '1px solid #ddd', cursor: 'pointer' }}
            >
              <option value="price">Price: Low to High ⬆</option>
              <option value="-price">Price: High to Low ⬇</option>
              <option value="-created_at">Newest First ✨</option>
            </select>
          </div>
          
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))', gap: '25px' }}>
            {products.map(product => {
              // Get best price for display
              const prices = product.prices.map(p => parseFloat(p.price))
              const bestPrice = prices.length > 0 ? Math.min(...prices) : 0;
              const safePrices = product.prices || [];

              return (
                <Link to={`/product/${product.id}`} key={product.id} style={{ textDecoration: 'none' }}>
                  <div style={{ backgroundColor: 'white', borderRadius: '12px', overflow: 'hidden', border: '1px solid #eee', cursor: 'pointer', transition: 'box-shadow 0.2s', height: '100%', position: 'relative' }}
                    onMouseEnter={(e) => e.currentTarget.style.boxShadow = '0 10px 20px rgba(0,0,0,0.1)'}
                    onMouseLeave={(e) => e.currentTarget.style.boxShadow = 'none'}
                  >
                     {/* COMPARE CHECKBOX */}
                    <div style={{ position: 'absolute', top: '10px', left: '10px', zIndex: 10, display: 'flex', gap: '10px' }} onClick={(e) => e.preventDefault()}>
                      <input 
                        type="checkbox" 
                        checked={compareList.some(p => p.id === product.id)}
                        onChange={(e) => {
                          if (e.target.checked) addToCompare(product);
                          else removeFromCompare(product.id);
                        }}
                        style={{ width: '18px', height: '18px', cursor: 'pointer', accentColor: '#2563eb' }}
                      />
                      <button onClick={(e) => toggleLike(e, product.id)} 
                        style={{ 
                            background: 'white', border: 'none', borderRadius: '50%', width: '24px', height: '24px', 
                            cursor: 'pointer', fontSize: '14px', padding: 0,
                            boxShadow: '0 2px 4px rgba(0,0,0,0.1)' 
                        }}>
                        {wishlistMap[product.id] ? '❤️' : '🤍'}
                      </button>
                    </div>
                    
                    <div style={{ height: '180px', padding: '20px', display: 'flex', alignItems: 'center', justifyContent: 'center', position: 'relative' }}>
                      <span style={{ position: 'absolute', top: '10px', right: '10px', background: '#f0f0f0', padding: '4px 8px', borderRadius: '4px', fontSize: '0.7rem', color: '#666' }}>{product.sector}</span>
                      <img src={product.image_url} alt={product.name} style={{ maxHeight: '100%', maxWidth: '100%', objectFit: 'contain' }} />
                    </div>
                    <div style={{ padding: '15px' }}>
                      <h3 style={{ fontSize: '1rem', color: '#333', height: '40px', overflow: 'hidden', marginBottom: '15px' }}>{product.name}</h3>
                      
                      {/* MINI SPECS PREVIEW */}
                      <div style={{ display: 'flex', gap: '5px', marginBottom: '15px', fontSize: '0.75rem', color: '#666', flexWrap: 'wrap' }}>
                        <span style={{ background: '#f8f9fa', padding: '2px 6px', borderRadius: '4px' }}>{product.gpu || "?"}</span>
                        <span style={{ background: '#f8f9fa', padding: '2px 6px', borderRadius: '4px' }}>{product.ram || "?"}</span>
                        <span style={{ background: '#f8f9fa', padding: '2px 6px', borderRadius: '4px' }}>{product.storage || "?"}</span>
                      </div>

                      <div style={{ display: 'flex', flexDirection: 'column', gap: '5px' }}>
                        {safePrices.length > 0 ? (
                          safePrices.map((deal, idx) => {
                            const isBest = parseFloat(deal.price) === bestPrice;
                            return (
                              <div key={idx} style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.9rem' }}>
                                <span style={{ color: isBest ? '#007bff' : '#888' }}>{deal.shop ? deal.shop.name : "Shop"}</span>
                                <span style={{ fontWeight: 'bold', color: isBest ? '#28a745' : '#333' }}>{deal.price} TND</span>
                              </div>
                            )
                          })
                        ) : (
                          <div style={{fontSize: '0.9rem', color: '#999'}}>No prices yet</div>
                        )}
                      </div>
                    </div>
                  </div>
                </Link>
              )
            })}
          </div>

          {/* PAGINATION CONTROLS */}
          <div style={{ display: 'flex', justifyContent: 'center', gap: '15px', marginTop: '40px', marginBottom: '20px' }}>
            <button 
                disabled={page === 1} 
                onClick={() => setPage(p => Math.max(1, p - 1))}
                style={{ padding: '10px 20px', borderRadius: '8px', border: '1px solid #ddd', background: page === 1 ? '#eee' : 'white', cursor: page === 1 ? 'default' : 'pointer' }}
            >
                Previous
            </button>
            <span style={{ display: 'flex', alignItems: 'center' }}>Page {page} of {totalPages}</span>
            <button 
                disabled={page >= totalPages} 
                onClick={() => setPage(p => p + 1)}
                style={{ padding: '10px 20px', borderRadius: '8px', border: '1px solid #ddd', background: page >= totalPages ? '#eee' : 'white', cursor: page >= totalPages ? 'default' : 'pointer' }}
            >
                Next
            </button>
          </div>

        </main>
      </div>
    </div>
  )
}

function FilterSection({ title, options, selected, setSelected }) {
  return (
    <div style={{ marginBottom: '30px' }}>
      <h3 style={{ fontSize: '1rem', fontWeight: '700', marginBottom: '10px', color: '#333' }}>{title}</h3>
      <div style={{ display: 'flex', flexDirection: 'column', gap: '5px' }}>
        {options.map(option => (
          <button key={option} onClick={() => setSelected(option)}
            style={{ 
              padding: '6px 10px', textAlign: 'left', borderRadius: '6px', border: 'none', cursor: 'pointer', fontSize: '0.9rem',
              backgroundColor: selected === option ? '#e7f1ff' : 'transparent', 
              color: selected === option ? '#007bff' : '#555', 
              fontWeight: selected === option ? '600' : '400' 
            }}>
            {option === 'N/A' ? 'Other' : option}
          </button>
        ))}
      </div>
    </div>
  )
}

export default ProductList