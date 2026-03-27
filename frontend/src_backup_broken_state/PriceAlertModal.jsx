import React, { useState } from 'react';
import { X, Bell, Check } from 'lucide-react';
import './ProductsPage.css';

const PriceAlertModal = ({ product, onClose }) => {
    const [email, setEmail] = useState('');
    const [targetPrice, setTargetPrice] = useState(
        product ? Math.max(0, product.price - 50) : 0
    );
    const [isSubmitted, setIsSubmitted] = useState(false);

    if (!product) return null;

    const handleSubmit = (e) => {
        e.preventDefault();
        // Here we would send the data to the backend
        console.log("Setting alert for:", product.id, "at", targetPrice, "for", email);
        
        setIsSubmitted(true);
        setTimeout(() => {
            onClose();
        }, 2000);
    };

    return (
        <div className="modal-overlay" onClick={onClose}>
            <div className="modal-content price-alert-modal" onClick={e => e.stopPropagation()}>
                <button className="modal-close-btn" onClick={onClose}>
                    <X size={24} />
                </button>

                {!isSubmitted ? (
                    <>
                        <div className="modal-header">
                            <Bell size={32} className="alert-icon-large" />
                            <h2>Price Alert</h2>
                        </div>
                        
                        <div className="alert-product-summary">
                            <img src={product.image} alt={product.title} />
                            <div>
                                <h4>{product.title}</h4>
                                <span className="current-price">Current: {product.price.toFixed(3)} DT</span>
                            </div>
                        </div>

                        <p className="alert-instruction">
                            Notify me when the price drops below:
                        </p>

                        <form onSubmit={handleSubmit} className="alert-form">
                            <div className="form-group">
                                <label>Target Price (DT)</label>
                                <input 
                                    type="number" 
                                    value={targetPrice} 
                                    onChange={(e) => setTargetPrice(Number(e.target.value))}
                                    required
                                />
                            </div>

                            <div className="form-group">
                                <label>Email Address</label>
                                <input 
                                    type="email" 
                                    placeholder="your@email.com" 
                                    value={email} 
                                    onChange={(e) => setEmail(e.target.value)}
                                    required
                                />
                            </div>

                            <button type="submit" className="set-alert-btn">
                                Set Alert
                            </button>
                        </form>
                    </>
                ) : (
                    <div className="success-message">
                        <div className="success-icon-bg">
                            <Check size={40} />
                        </div>
                        <h3>Alert Set!</h3>
                        <p>We'll email you if {product.title.substring(0, 20)}... drops below {targetPrice} DT.</p>
                    </div>
                )}
            </div>
        </div>
    );
};

export default PriceAlertModal;
