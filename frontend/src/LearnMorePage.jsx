import React from 'react';
import { useNavigate } from 'react-router-dom';
import { ChevronRight, Activity, Cpu, ShieldCheck, Zap, Globe, ArrowLeft } from 'lucide-react';
import './LearnMorePage.css';

const LearnMorePage = () => {
    const navigate = useNavigate();

    return (
        <div className="learn-more-container">
            {/* BACKGROUND ANIMATION */}
            <div className="learn-more-bg"></div>

            {/* NAV BACK */}
            <button className="nav-back-btn" onClick={() => navigate('/')}>
                <ArrowLeft size={20} /> Back to Home
            </button>

            {/* HERO */}
            <header className="lm-hero">
                <div className="lm-hero-content fade-in-up">
                    <h1 className="lm-title">
                        Redefining Tech <span className="highlight-text">Shopping</span>
                    </h1>
                    <p className="lm-subtitle">
                        TechnoPrice Tunisia isn't just a store. It's an intelligent platform designed to empower your buying decisions with real-time data and AI-driven insights.
                    </p>
                </div>
            </header>

            {/* MISSION GRID */}
            <section className="lm-grid-section">
                <div className="lm-card glass-card theme-blue">
                    <div className="lm-icon-box blue">
                        <Activity size={32} />
                    </div>
                    <h3>Real-Time Price Intelligence</h3>
                    <p>
                        Our algorithms scan thousands of products across the Tunisian market every hour. 
                        We don't just show you prices; we show you <strong>price history, trends, and true value</strong>.
                    </p>
                </div>

                <div className="lm-card glass-card theme-purple">
                    <div className="lm-icon-box purple">
                        <Cpu size={32} />
                    </div>
                    <h3>Performance-Per-Dinar</h3>
                    <p>
                        Stop guessing if an i5 is better than an i7 for your budget. 
                        Our "Smart Specs" engine calculates the raw performance value of every component, 
                        giving you a definitive <strong>Price/Performance score</strong>.
                    </p>
                </div>

                <div className="lm-card glass-card theme-green">
                    <div className="lm-icon-box green">
                        <ShieldCheck size={32} />
                    </div>
                    <h3>Verified Ecosystem</h3>
                    <p>
                        We aggregate products only from trusted, verified retailers. 
                        Say goodbye to scams and fake listings. Every product you see is 
                        <strong>legitimate and available</strong>.
                    </p>
                </div>

                 <div className="lm-card glass-card theme-gold">
                    <div className="lm-icon-box gold">
                        <Zap size={32} />
                    </div>
                    <h3>Instant Alerts</h3>
                    <p>
                        Set your target price and let us do the watching. 
                        We'll notify you the second a deal drops into your budget range. 
                        <strong>Speed matters</strong>.
                    </p>
                </div>
                
                 <div className="lm-card glass-card theme-cyan">
                    <div className="lm-icon-box cyan">
                        <Globe size={32} />
                    </div>
                    <h3>Centralized Catalog</h3>
                    <p>
                        Why open 20 tabs? We bring MyTek, Tunisianet, Wiki, and SpaceNet 
                        into one unified, beautiful interface. 
                        <strong>One search, everywhere</strong>.
                    </p>
                </div>
            </section>

            {/* CTA */}
            <section className="lm-cta">
                <h2>Ready to experience the future?</h2>
                <button className="cta-button primary" onClick={() => navigate('/products')}>
                    Start Browsing Now <ChevronRight size={20} />
                </button>
            </section>
        </div>
    );
};

export default LearnMorePage;
