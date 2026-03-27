import React, { useMemo } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { 
  ArrowLeft, ShoppingCart, Cpu, Layers, Monitor, Zap, 
  HardDrive, Maximize, Scan, Grid, Command, Box, Heart 
} from 'lucide-react';
import productData from './data/products.json';
import spacenetData from './data/spacenet_products.json';
import { useWishlist } from './context/WishlistContext';
import './ProductDetailsPage.css';

const ProductDetailsPage = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const { toggleWishlist, isInWishlist } = useWishlist();

  // 1. Merge Data Sources
  const allProducts = useMemo(() => [...productData, ...spacenetData], []);

  // 2. Find Current Product (Handle both numeric and string IDs)
  const product = allProducts.find(p => p.id == id);

  // 3. Recommendation Logic (Universal)
  const relatedProducts = useMemo(() => {
    if (!product) return [];
    return allProducts
      .filter(p => 
        p.id !== product.id &&                // Don't show itself
        p.specs.category === product.specs.category && // Same Category
        Math.abs(p.price - product.price) < 1000       // Similar Price (+/- 1000 TND)
      )
      .sort(() => 0.5 - Math.random()) // Randomize
      .slice(0, 4); // Take only 4
  }, [product, allProducts]);

  if (!product) return (
      <div className="product-details-container" style={{textAlign:'center', marginTop: '100px'}}>
        <h2>Product Not Found</h2>
        <button onClick={() => navigate('/products')} className="back-btn" style={{display:'inline-flex'}}>
            <ArrowLeft size={20} /> Back to Inventory
        </button>
      </div>
  );

  // Helper to handle defaults for Spacenet
  const getSpec = (key) => {
    const val = product.specs[key];
    if (val && val !== 'Unknown') return val;
    
    // Defaults if missing (Common for Spacenet)
    if (key === 'res') return "FHD (1920x1080)";
    if (key === 'panel') return "IPS";
    if (key === 'hz') return "60Hz";
    if (key === 'os') return "FreeDOS";
    
    return "Unknown";
  };

  const isSpacenet = product.source === 'Spacenet' || typeof product.id === 'string';

  return (
    <div className="product-details-container">
      <div className="details-header">
         <button onClick={() => navigate(-1)} className="back-btn">
            <ArrowLeft size={20} /> Back to Browse
         </button>
      </div>

      <div className="details-grid">
        {/* LEFT COLUMN: VISUALS */}
        <div className="visuals-section">
          <div className="main-image-frame">
            <img src={product.image} alt={product.title} />
            {getSpec('hz') !== '60Hz' && <div className="neon-badge">{getSpec('hz')}</div>}
            <button className="heart-btn-large" onClick={() => toggleWishlist(product)}>
                <Heart size={24} fill={isInWishlist(product.id) ? "#ff0055" : "rgba(0,0,0,0.1)"} color={isInWishlist(product.id) ? "#ff0055" : "black"} />
            </button>
          </div>
        </div>

        {/* RIGHT COLUMN: DATA */}
        <div className="info-section">
          <div className="brand-tag">{getSpec('brand')} // {getSpec('category')}</div>
          <h1 className="product-title">{product.title}</h1>
          <div className="price-tag">{product.price.toFixed(3)} <span className="currency">TND</span></div>
          
          <h3 className="section-title">Technical Specifications</h3>
          <div className="specs-grid-full">
            <div className="spec-card"><Cpu className="icon" size={20}/><div><small>Processor</small><strong>{getSpec('cpu')}</strong></div></div>
            <div className="spec-card"><Layers className="icon" size={20}/><div><small>Graphics</small><strong>{getSpec('gpu')}</strong></div></div>
            <div className="spec-card"><Box className="icon" size={20}/><div><small>RAM</small><strong>{getSpec('ram')}</strong></div></div>
            <div className="spec-card"><HardDrive className="icon" size={20}/><div><small>Storage</small><strong>{getSpec('storage')}</strong></div></div>
            <div className="spec-card"><Zap className="icon" size={20}/><div><small>Refresh Rate</small><strong>{getSpec('hz')}</strong></div></div>
            <div className="spec-card"><Maximize className="icon" size={20}/><div><small>Size</small><strong>{getSpec('screen')}</strong></div></div>
            <div className="spec-card"><Scan className="icon" size={20}/><div><small>Resolution</small><strong>{getSpec('res')}</strong></div></div>
            <div className="spec-card"><Grid className="icon" size={20}/><div><small>Panel Type</small><strong>{getSpec('panel')}</strong></div></div>
            <div className="spec-card"><Command className="icon" size={20}/><div><small>OS</small><strong>{getSpec('os')}</strong></div></div>
          </div>

          <a href={product.link} target="_blank" rel="noopener noreferrer" className="buy-button" 
             style={{ background: isSpacenet ? 'linear-gradient(45deg, #10b981, #059669)' : undefined }}>
            {isSpacenet ? 'ORDER ON SPACENET' : 'ORDER ON TUNISIANET'} <ShoppingCart size={20} />
          </a>
        </div>
      </div>

      {/* --- NEW RELATED PRODUCTS SECTION --- */}
      {relatedProducts.length > 0 && (
        <div className="related-section">
            <h2 className="related-title">Similar Systems Detected</h2>
            <div className="related-grid">
                {relatedProducts.map(p => (
                    <Link to={`/product/${p.id}`} key={p.id} className="related-card" onClick={() => window.scrollTo(0,0)}>
                        <div className="r-img"><img src={p.image} alt={p.title}/></div>
                        <div className="r-info">
                            <h5>{p.title}</h5>
                            <div className="r-price">{p.price.toFixed(3)} TND</div>
                        </div>
                    </Link>
                ))}
            </div>
        </div>
      )}
    </div>
  );
};

export default ProductDetailsPage;
