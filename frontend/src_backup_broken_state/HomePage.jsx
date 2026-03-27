import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Smartphone, Watch, ChevronRight, Zap, Mail, MessageCircle } from 'lucide-react';
import './HomePage.css';
import pixelImage from './assets/pixel_9_pro_fixed.jpg';

const heroImages = [
    "https://images.unsplash.com/photo-1518770660439-4636190af475?q=100&w=2500&auto=format&fit=crop",
    "https://images.unsplash.com/photo-1551288049-bebda4e38f71?q=100&w=2500&auto=format&fit=crop",
    "https://images.unsplash.com/photo-1460925895917-afdab827c52f?q=100&w=2500&auto=format&fit=crop",
    "https://images.unsplash.com/photo-1451187580459-43490279c0fa?q=100&w=2500&auto=format&fit=crop"
];

const HomePage = () => {
    const navigate = useNavigate();
    const [currentImage, setCurrentImage] = useState(0);

    useEffect(() => {
        const interval = setInterval(() => {
            setCurrentImage((prev) => (prev + 1) % heroImages.length);
        }, 4000);
        return () => clearInterval(interval);
    }, []);

    return (
        <div className="home-container">
            {/* SIDE WIDGETS */}
            <div className="side-widget left">
                <div className="widget-content">
                    <Mail size={18} /> <span className="vertical-text">SUBSCRIBE</span>
                </div>
            </div>
            <div className="side-widget right">
                <div className="widget-content">
                    <MessageCircle size={18} /> <span className="vertical-text">CONTACT</span>
                </div>
            </div>

            {/* HERO SECTION */}
            <section className="hero">
                {heroImages.map((img, index) => (
                    <div
                        key={index}
                        className={`hero-bg ${index === currentImage ? 'active' : ''}`}
                        style={{ backgroundImage: `url(${img})` }}
                    />
                ))}

                <div className="hero-overlay"></div>
                
                <div className="hero-content fade-in-up">
                    <div className="badge-container">
                        <span className="premium-badge">
                            <Zap size={18} fill="currentColor" className="pulsing-icon" /> 
                            The Future of Pricing
                        </span>
                    </div>

                    <h1 className="brand-title">
                        <span className="gold-text">TechnoPrice</span>
                        <span className="spacer"> </span>
                        <span className="liquid-text">Tunisia</span>
                    </h1>

                    <p className="hero-subtitle">
                        <span className="subtitle-deals">Compare prices, find the best deals, and shop smarter.</span>
                        <br/>
                        <span className="subtitle-tech">Experience the next generation of tech shopping.</span>
                    </p>

                    <div className="cta-group">
                        <button className="cta-button primary" onClick={() => navigate('/products')}>
                            Browse Computers <ChevronRight size={20} />
                        </button>
                        <button className="cta-button secondary" onClick={() => navigate('/about')}>
                            Learn More
                        </button>
                    </div>
                </div>
            </section>

            {/* ECOSYSTEM SECTION (VIDEO BACKGROUND) */}
            <section className="categories-section">
                
                {/* VIDEO CONTAINER */}
                <div className="video-container">
                    <video className="tech-video" autoPlay loop muted playsInline>
                        <source src="/tech-bg.mp4" type="video/mp4" />
                    </video>
                    <div className="video-overlay"></div>
                </div>

                <div className="section-header fade-in-scroll">
                    <div className="title-wrapper">
                        <h2 className="ecosystem-title">Explore The Ecosystem</h2>
                    </div>
                    <div className="laser-beam"></div>
                </div>

                <div className="grid-container">
                    <div className="category-card featured-card" onClick={() => navigate('/products')}>
                        <div className="card-bg-glow"></div>
                        <div className="card-image-container">
                            <img
                                src="https://images.unsplash.com/photo-1661961110218-35af7210f803?q=100&w=2500&auto=format&fit=crop"
                                alt="Futuristic Laptop"
                                className="card-img"
                            />
                        </div>
                        <div className="card-info">
                            <div className="card-header">
                                <h3>Computers</h3>
                                <span className="live-indicator">● Live</span>
                            </div>
                            <p>High-performance Laptops, Desktops & Workstations.</p>
                            <div className="link-wrapper">
                                <span className="link-text">Enter Section</span>
                                <div className="arrow-circle"><ChevronRight size={18} /></div>
                            </div>
                        </div>
                    </div>

                    <div className="category-card featured-card" onClick={() => navigate('/mobiles')}>
                        <div className="card-bg-glow"></div>
                        <div className="card-image-container">
                            <img
                                src={pixelImage}
                                alt="Google Pixel 9 Pro"
                                className="card-img"
                                style={{ objectFit: 'cover' }}
                            />
                        </div>
                        <div className="card-info">
                            <div className="card-header">
                                <h3>Mobiles</h3>
                                <span className="live-indicator">● New</span>
                            </div>
                            <p>Featuring the all-new Pixel 9 Pro.</p>
                            <div className="link-wrapper">
                                <span className="link-text">Explore Mobiles</span>
                                <div className="arrow-circle"><ChevronRight size={18} /></div>
                            </div>
                        </div>
                    </div>

                    <div className="category-card featured-card" onClick={() => navigate('/components')}>
                        <div className="card-bg-glow"></div>
                        <div className="card-image-container">
                            <img
                                src="https://images.unsplash.com/photo-1591799264318-7e6ef8ddb7ea?q=80&w=1080"
                                alt="Gaming Components"
                                className="card-img"
                                style={{ objectFit: 'cover' }}
                            />
                        </div>
                        <div className="card-info">
                            <div className="card-header">
                                <h3>Components</h3>
                                <span className="live-indicator">● New</span>
                            </div>
                            <p>Build your dream machine with parts.</p>
                            <div className="link-wrapper">
                                <span className="link-text">Browse Parts</span>
                                <div className="arrow-circle"><ChevronRight size={18} /></div>
                            </div>
                        </div>
                    </div>
                </div>
            </section>
        </div>
    );
};

export default HomePage;
