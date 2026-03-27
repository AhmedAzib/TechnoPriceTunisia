import React from 'react';
import { Link } from 'react-router-dom';
import { useWishlist } from './context/WishlistContext';
import { Heart, ArrowLeft, Trash2 } from 'lucide-react';
import './ProductsPage.css'; // Reuse existing styles

const WishlistPage = () => {
  const { wishlist, toggleWishlist } = useWishlist();

  return (
    <div className="products-layout" style={{ display: 'block', padding: '50px 5%' }}>
      <header style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '40px' }}>
         <div style={{ display: 'flex', alignItems: 'center', gap: '20px' }}>
            <Link to="/products" className="back-btn" style={{marginBottom: 0}}>
                <ArrowLeft size={20} /> Back
            </Link>
            <h1>My Wishlist <span className="highlight">({wishlist.length})</span></h1>
         </div>
      </header>

      {wishlist.length === 0 ? (
        <div className="empty-state" style={{ textAlign: 'center', color: '#94a3b8', marginTop: '100px' }}>
          <Heart size={60} color="#334155" />
          <h2>Your heart is empty</h2>
          <Link to="/products" className="dock-btn" style={{ display: 'inline-flex', marginTop: '20px' }}>Start Browsing</Link>
        </div>
      ) : (
        <div className="grid">
          {wishlist.map(p => (
            <div key={p.id} className="card">
              <div className="img-box">
                 <img src={p.image} alt={p.title}/>
                 {p.specs.hz !== '60Hz' && <span className="tag">{p.specs.hz}</span>}
                 <button 
                    onClick={() => toggleWishlist(p)}
                    style={{ 
                        position: 'absolute', top: '10px', left: '10px', 
                        background: 'rgba(0,0,0,0.5)', border: 'none', borderRadius: '50%', 
                        padding: '8px', cursor: 'pointer', color: '#ff0055' 
                    }}
                 >
                    <Trash2 size={16} />
                 </button>
              </div>
              <Link to={`/product/${p.id}`} style={{ textDecoration: 'none', color: 'inherit' }}>
                  <div className="details">
                    <h4>{p.title}</h4>
                    <div className="specs-mini">
                      <span>{p.specs.cpu}</span> • <span>{p.specs.gpu}</span>
                    </div>
                    <div className="price">{p.price.toFixed(3)} TND</div>
                  </div>
              </Link>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default WishlistPage;
