import React from 'react';
import { X, ShoppingBag } from 'lucide-react';
import { Link } from 'react-router-dom';
import './QuickLookModal.css';

const QuickLookModal = ({ product, isOpen, onClose }) => {
  if (!isOpen || !product) return null;

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={e => e.stopPropagation()}>
        <button className="modal-close" onClick={onClose}>
          <X size={24} />
        </button>
        
        <div className="modal-body">
          {/* Left Column: Image */}
          <div className="modal-image-col">
            <img src={product.image} alt={product.title} />
          </div>

          {/* Right Column: Details */}
          <div className="modal-details-col">
            <h2 className="modal-title">{product.title}</h2>
            <div className="modal-price">{product.price.toFixed(3)} TND</div>
            
            <div className="modal-specs">
              {product.specs.cpu && <div className="spec-row"><strong>CPU:</strong> {product.specs.cpu}</div>}
              {product.specs.gpu && <div className="spec-row"><strong>GPU:</strong> {product.specs.gpu}</div>}
              {product.specs.ram && <div className="spec-row"><strong>RAM:</strong> {product.specs.ram}</div>}
              {product.specs.storage && <div className="spec-row"><strong>Storage:</strong> {product.specs.storage}</div>}
              {product.specs.screen && <div className="spec-row"><strong>Screen:</strong> {product.specs.screen}</div>}
            </div>

            <div className="modal-actions">
                <Link to={`/product/${product.id}`} className="modal-btn-primary">
                    View Full Details
                </Link>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default QuickLookModal;
