import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useWishlist } from './context/WishlistContext';
import { Heart, ArrowLeft, Trash2, ExternalLink, Smartphone, Laptop } from 'lucide-react';
import './WishlistPage.css';

const WishlistPage = () => {
  const { wishlist, toggleWishlist } = useWishlist();
  const navigate = useNavigate();

  // Detect if a product is a phone
  const isPhone = (p) => {
    const cat = (p.specs?.category || p.category || '').toLowerCase();
    const t = (p.title || '').toLowerCase();
    return cat === 'smartphone' || t.includes('smartphone') || t.includes('iphone') ||
           t.includes('galaxy') || t.includes('redmi') || t.includes('poco');
  };

  // Smart back navigation
  const goBack = () => {
    if (window.history.length > 1) {
      navigate(-1);
    } else {
      navigate('/');
    }
  };

  // Safe price display
  const formatPrice = (price) => {
    const num = parseFloat(price);
    if (!num || isNaN(num)) return '—';
    return num.toFixed(3) + ' DT';
  };

  // Store badge color
  const getStoreColor = (source) => {
    const s = (source || '').toLowerCase();
    if (s.includes('mytek')) return '#ef4444';
    if (s.includes('spacenet')) return '#10b981';
    if (s.includes('wiki')) return '#8b5cf6';
    if (s.includes('tunisiatech')) return '#06b6d4';
    if (s.includes('tdiscount')) return '#f97316';
    if (s.includes('megapc')) return '#eab308';
    if (s.includes('skymil')) return '#3b82f6';
    if (s.includes('techspace')) return '#ec4899';
    if (s.includes('samsung')) return '#1d4ed8';
    return '#5F8D8B';
  };

  return (
    <div style={{
      minHeight: '100vh',
      backgroundColor: '#E8F1F5',
      padding: '30px 5%',
      fontFamily: "'Inter', sans-serif",
      color: '#1A2B48'
    }}>
      {/* HEADER */}
      <header style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '30px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '15px' }}>
          <button
            onClick={goBack}
            style={{
              display: 'flex', alignItems: 'center', gap: '8px',
              background: 'white', border: '1px solid #e2e8f0',
              borderRadius: '10px', padding: '10px 18px', cursor: 'pointer',
              fontWeight: '600', color: '#1A2B48', fontSize: '0.9rem',
              transition: '0.2s'
            }}
          >
            <ArrowLeft size={18} /> Back
          </button>
          <div>
            <h1 style={{ margin: 0, fontSize: '1.8rem', fontWeight: '800' }}>
              My Wishlist <span style={{ color: '#5F8D8B' }}>({wishlist.length})</span>
            </h1>
          </div>
        </div>
      </header>

      {wishlist.length === 0 ? (
        <div style={{
          textAlign: 'center', padding: '80px 20px',
          background: 'white', borderRadius: '20px',
          border: '1px solid #e2e8f0'
        }}>
          <Heart size={60} color="#cbd5e1" />
          <h2 style={{ color: '#64748b', marginTop: '20px' }}>Your wishlist is empty</h2>
          <p style={{ color: '#94a3b8', marginBottom: '20px' }}>Start browsing and heart the products you love</p>
          <div style={{ display: 'flex', gap: '12px', justifyContent: 'center' }}>
            <Link to="/mobiles" style={{
              display: 'inline-flex', alignItems: 'center', gap: '8px',
              background: '#5F8D8B', color: 'white', padding: '12px 24px',
              borderRadius: '10px', textDecoration: 'none', fontWeight: '600'
            }}>
              <Smartphone size={18} /> Browse Phones
            </Link>
            <Link to="/products" style={{
              display: 'inline-flex', alignItems: 'center', gap: '8px',
              background: '#1A2B48', color: 'white', padding: '12px 24px',
              borderRadius: '10px', textDecoration: 'none', fontWeight: '600'
            }}>
              <Laptop size={18} /> Browse Computers
            </Link>
          </div>
        </div>
      ) : (
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(4, minmax(0, 1fr))',
          gap: '20px'
        }}>
          {wishlist.map(p => {
            const phone = isPhone(p);
            return (
              <div key={p.id} style={{
                background: 'white',
                borderRadius: '16px',
                border: '1px solid #e2e8f0',
                overflow: 'hidden',
                transition: 'all 0.3s ease',
                display: 'flex',
                flexDirection: 'column',
                boxShadow: '0 2px 8px rgba(0,0,0,0.04)'
              }}>
                {/* IMAGE */}
                <div style={{
                  height: '180px', background: 'white',
                  display: 'flex', justifyContent: 'center', alignItems: 'center',
                  padding: '15px', position: 'relative',
                  borderBottom: '1px solid #f1f5f9'
                }}>
                  <img
                    src={p.image}
                    alt={p.title}
                    style={{ maxHeight: '100%', maxWidth: '100%', objectFit: 'contain' }}
                    onError={(e) => { e.target.style.display = 'none'; }}
                  />
                  {/* Store badge */}
                  {p.source && (
                    <span style={{
                      position: 'absolute', top: '10px', right: '10px',
                      background: getStoreColor(p.source), color: 'white',
                      padding: '3px 8px', borderRadius: '4px',
                      fontSize: '0.7rem', fontWeight: '800', textTransform: 'uppercase'
                    }}>
                      {p.source}
                    </span>
                  )}
                  {/* Delete button */}
                  <button
                    onClick={() => toggleWishlist(p)}
                    style={{
                      position: 'absolute', top: '10px', left: '10px',
                      background: 'white', border: '1px solid #fee2e2',
                      borderRadius: '50%', width: '34px', height: '34px',
                      cursor: 'pointer', display: 'flex',
                      alignItems: 'center', justifyContent: 'center',
                      color: '#ef4444', boxShadow: '0 2px 6px rgba(0,0,0,0.1)',
                      transition: '0.2s'
                    }}
                  >
                    <Trash2 size={15} />
                  </button>
                </div>

                {/* DETAILS */}
                <div style={{ padding: '12px', flex: 1, display: 'flex', flexDirection: 'column' }}>
                  <h4 style={{
                    margin: '0 0 8px', fontSize: '0.85rem', fontWeight: '600',
                    color: '#1A2B48', lineHeight: '1.2',
                    height: '2.4em', overflow: 'hidden',
                    display: '-webkit-box', WebkitLineClamp: 2,
                    WebkitBoxOrient: 'vertical'
                  }}>
                    {p.title}
                  </h4>

                  {/* Specs - phone vs computer */}
                  <div style={{ fontSize: '0.78rem', color: '#64748b', marginBottom: '8px', display: 'flex', gap: '6px', flexWrap: 'wrap' }}>
                    {phone ? (
                      <>
                        {p.specs?.cpu && <span>{p.specs.cpu}</span>}
                        {p.specs?.ram && <span>•{p.specs.ram}</span>}
                        {p.specs?.storage && <span>•{p.specs.storage}</span>}
                      </>
                    ) : (
                      <>
                        {p.specs?.cpu && <span>{p.specs.cpu}</span>}
                        {p.specs?.ram && <span>•{p.specs.ram}</span>}
                        {p.specs?.gpu && p.specs.gpu !== 'Unknown' && <span>•{p.specs.gpu}</span>}
                      </>
                    )}
                  </div>

                  {/* Price */}
                  <div style={{ marginTop: 'auto', display: 'flex', justifyContent: 'space-between', alignItems: 'center', paddingTop: '8px', borderTop: '1px solid #f1f5f9' }}>
                    <span style={{ fontSize: '1rem', fontWeight: '800', color: '#10b981' }}>
                      {formatPrice(p.price)}
                    </span>

                    {/* View button */}
                    {p.link && (
                      <a
                        href={p.link}
                        target="_blank"
                        rel="noopener noreferrer"
                        style={{
                          display: 'flex', alignItems: 'center', gap: '5px',
                          background: '#5F8D8B', color: 'white',
                          padding: '6px 14px', borderRadius: '8px',
                          fontSize: '0.8rem', fontWeight: '600',
                          textDecoration: 'none', transition: '0.2s'
                        }}
                      >
                        View <ExternalLink size={13} />
                      </a>
                    )}
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};

export default WishlistPage;
