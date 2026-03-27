import { useState, useEffect } from 'react'
import { useParams, Link, useNavigate, useLocation } from 'react-router-dom'
import axios from 'axios'
import { useCompare } from './CompareContext' // <--- IMPORT
import { useAuth } from './AuthContext' // <--- IMPORT

function ProductDetail() {
  const { id } = useParams() // Get the ID from the URL (e.g., product/1)
  const [product, setProduct] = useState(null)
  const [loading, setLoading] = useState(true)

  // HOOKS MUST BE AT THE TOP
  const { addToCompare, compareList, removeFromCompare } = useCompare(); 
  const { user } = useAuth()
  const [isLiked, setIsLiked] = useState(false)
  const [wishlistId, setWishlistId] = useState(null)
  const navigate = useNavigate();
  const location = useLocation();

  // --- FETCH PRODUCTS ---
  useEffect(() => {
    axios.get(`http://127.0.0.1:8000/api/products/${id}/`)
      .then(response => {
        setProduct(response.data)
        setLoading(false)
      })
      .catch(error => {
        console.error("Error:", error)
        setLoading(false)
      })
  }, [id])

  // --- WISHLIST LOGIC ---
  useEffect(() => {
    // Check if user and product exist before running logic
    if (user && product?.id) {
       checkIfLiked();
    }
  }, [user, product?.id]) // Safe dependency

  const checkIfLiked = () => {
     if (!product) return;
     axios.get('http://127.0.0.1:8000/api/wishlist/')
      .then(res => {
         const found = res.data.find(item => item.product === product.id);
         if (found) {
             setIsLiked(true);
             setWishlistId(found.id);
         }
      })
  }

  const toggleLike = () => {
      if (!user) {
          navigate('/login', { state: { from: location } });
          return;
      }
      if (isLiked) {
          axios.delete(`http://127.0.0.1:8000/api/wishlist/${wishlistId}/`).then(() => {
              setIsLiked(false);
              setWishlistId(null);
          })
      } else {
          if (!product) return;
          axios.post('http://127.0.0.1:8000/api/wishlist/', { product: product.id }).then(res => {
              setIsLiked(true);
              setWishlistId(res.data.id);
          })
      }
  }

  // --- CONDITIONAL RETURNS MUST BE AFTER HOOKS ---
  if (loading) return <div style={{textAlign: 'center', marginTop: '50px'}}>Loading details...</div>
  if (!product) return <div>Product not found</div>

  // Find best price again for highlighting
  const prices = product.prices.map(p => parseFloat(p.price))
  const bestPrice = Math.min(...prices)

  const isInCompare = compareList.some(p => p.id === product.id);

  return (
    <div style={{ maxWidth: '1000px', margin: '40px auto', padding: '20px', fontFamily: '"Inter", sans-serif' }}>
      
      {/* HEADER NAV */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Link to="/" style={{ textDecoration: 'none', color: '#666', fontSize: '0.9rem' }}>
            ← Back to Search
        </Link>
        
        <div style={{ display: 'flex', gap: '10px' }}>
            <button onClick={toggleLike} style={{ background: 'none', border: 'none', fontSize: '1.5rem', cursor: 'pointer' }}>
                {isLiked ? '❤️' : '🤍'}
            </button>

            <button 
            onClick={() => isInCompare ? removeFromCompare(product.id) : addToCompare(product)}
            style={{ 
                padding: '8px 20px', borderRadius: '8px', 
                background: isInCompare ? '#ffe4e6' : '#eff6ff', 
                color: isInCompare ? '#e11d48' : '#2563eb',
                border: 'none', fontWeight: '600', cursor: 'pointer'
            }}
            >
            {isInCompare ? "Remove from Compare" : "+ Add to Compare"}
            </button>
        </div>
      </div>

      <div style={{ display: 'flex', gap: '50px', marginTop: '30px', flexWrap: 'wrap' }}>
        
        {/* LEFT: BIG IMAGE */}
        <div style={{ flex: 1, minWidth: '300px', backgroundColor: 'white', padding: '40px', borderRadius: '20px', border: '1px solid #eee' }}>
          <img src={product.image_url} alt={product.name} style={{ width: '100%', objectFit: 'contain' }} />
        </div>

        {/* RIGHT: SPECS & PRICES */}
        <div style={{ flex: 1, minWidth: '300px' }}>
          <h1 style={{ fontSize: '2rem', marginBottom: '10px' }}>{product.name}</h1>
          <div style={{ color: '#007bff', fontWeight: 'bold', marginBottom: '20px', fontSize: '1.2rem' }}>
            {product.brand.name} | {product.sector}
          </div>

          {/* MAIN SPECS GRID */}
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '15px', marginBottom: '30px' }}>
            <SpecBox label="Processor" value={product.cpu} />
            <SpecBox label="Graphics Card" value={product.gpu} />
            <SpecBox label="RAM" value={product.ram} />
            <SpecBox label="Storage" value={product.storage} />
            <SpecBox label="Screen" value={product.screen_size} />
          </div>

          {/* 🆕 TECHNICAL SPECIFICATIONS TABLE */}
          <h3 style={{ borderBottom: '2px solid #eee', paddingBottom: '10px', marginTop: '20px' }}>Technical Specifications</h3>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '15px', marginTop: '15px', marginBottom: '30px' }}>
             {/* Only show if valuable */}
             <SpecBox label="Resolution" value={product.resolution} />
             <SpecBox label="Refresh Rate" value={product.refresh_rate} />
             <SpecBox label="OS" value={product.os} />
             <SpecBox label="Ports" value={product.ports} fullWidth={true} />
          </div>

          {/* PRICES LIST */}
          <h3 style={{ borderBottom: '2px solid #eee', paddingBottom: '10px' }}>Store Prices</h3>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '10px', marginTop: '15px' }}>
            {product.prices.map((deal, index) => (
              <div key={index} style={{ 
                display: 'flex', justifyContent: 'space-between', alignItems: 'center',
                padding: '15px', borderRadius: '10px',
                border: parseFloat(deal.price) === bestPrice ? '2px solid #28a745' : '1px solid #ddd',
                backgroundColor: parseFloat(deal.price) === bestPrice ? '#f0fff4' : 'white'
              }}>
                <span style={{ fontWeight: 'bold' }}>{deal.shop.name}</span>
                <div style={{ textAlign: 'right' }}>
                  <div style={{ fontSize: '1.2rem', fontWeight: 'bold', color: parseFloat(deal.price) === bestPrice ? '#28a745' : '#333' }}>
                    {deal.price} TND
                  </div>
                  {parseFloat(deal.price) === bestPrice && <small style={{ color: '#28a745' }}>🏆 Best Deal</small>}
                </div>
              </div>
            ))}
          </div>

        </div>
      </div>
    </div>
  )
}

// Small helper component for the grey spec boxes
function SpecBox({ label, value, fullWidth }) {
  if (!value || value === "N/A") return null; // Don't show empty boxes
  return (
    <div style={{ background: '#f8f9fa', padding: '10px', borderRadius: '8px', gridColumn: fullWidth ? 'span 2' : 'auto' }}>
      <div style={{ fontSize: '0.8rem', color: '#888' }}>{label}</div>
      <div style={{ fontWeight: '600', color: '#333' }}>{value}</div>
    </div>
  )
}

export default ProductDetail