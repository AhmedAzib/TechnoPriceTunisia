import React from 'react';
import { useNavigate } from 'react-router-dom';
import { 
    Cpu, 
    Monitor, 
    HardDrive, 
    CircuitBoard, 
    Server, 
    Wind, 
    Box, 
    Zap,
    ArrowLeft,
    ChevronRight
} from 'lucide-react';
import './ProductsPage.css'; // Reusing styles for consistency

import pixelImage from './assets/pixel_9_pro_fixed.jpg';
import storageImage from './assets/component_storage.png';
import coolingImage from './assets/component_cooling.png';

const categories = [
    {
        id: 'cpu',
        title: 'Processors',
        description: 'Intel Core & AMD Ryzen CPUs',
        image: 'https://images.unsplash.com/photo-1591799264318-7e6ef8ddb7ea?q=80&w=1080&auto=format&fit=crop',
        icon: <Cpu size={24} />
    },
    {
        id: 'gpu',
        title: 'Graphics Cards',
        description: 'NVIDIA GeForce & AMD Radeon',
        image: 'https://images.unsplash.com/photo-1591488320449-011701bb6704?q=80&w=1080&auto=format&fit=crop',
        icon: <Monitor size={24} />
    },
    {
        id: 'motherboard',
        title: 'Motherboards',
        description: 'ATX, Micro-ATX & Mini-ITX Boards',
        image: 'https://images.unsplash.com/photo-1518770660439-4636190af475?q=80&w=1080&auto=format&fit=crop',
        icon: <CircuitBoard size={24} />
    },
    {
        id: 'ram',
        title: 'Memory (RAM)',
        description: 'DDR4 & DDR5 High Speed Memory',
        image: 'https://images.unsplash.com/photo-1562976540-1502c2145186?q=80&w=1080&auto=format&fit=crop',
        icon: <Server size={24} />
    },
    {
        id: 'storage',
        title: 'Storage',
        description: 'NVMe SSDs, SATA SSDs & HDDs',
        image: storageImage,
        icon: <HardDrive size={24} />
    },
    {
        id: 'cooling',
        title: 'Cooling',
        description: 'AIO Liquid Coolers & Air Cooling',
        image: coolingImage,
        icon: <Wind size={24} />
    },
    {
        id: 'case',
        title: 'PC Cases',
        description: 'Towers, RGB Cases & Chassis',
        image: 'https://images.unsplash.com/photo-1587202372634-32705e3bf49c?q=80&w=1080&auto=format&fit=crop',
        icon: <Box size={24} />
    },
    {
        id: 'psu',
        title: 'Power Supply',
        description: 'Modular & Certification Rated PSUs',
        image: 'https://images.unsplash.com/photo-1587202372775-e229f172b9d7?q=80&w=1080&auto=format&fit=crop',
        icon: <Zap size={24} />
    }
];

const ComponentsPage = () => {
    const navigate = useNavigate();

    return (
        <div className="products-layout-final" style={{
            display: 'flex',
            flexDirection: 'column',
            minHeight: '100vh',
            backgroundColor: '#02040a',
            backgroundImage: `radial-gradient(circle at 15% 50%, rgba(56, 189, 248, 0.08) 0%, transparent 25%), 
                              radial-gradient(circle at 85% 30%, rgba(168, 85, 247, 0.08) 0%, transparent 25%)`,
            color: '#e2e8f0',
            fontFamily: "'Inter', sans-serif"
        }}>
            
            {/* Header / Nav */}
            <div style={{ padding: '20px 40px', display: 'flex', justifyContent: 'space-between', alignItems: 'center', background: 'rgba(2, 6, 23, 0.8)', backdropFilter: 'blur(10px)', borderBottom: '1px solid rgba(255,255,255,0.05)', position: 'sticky', top: 0, zIndex: 50 }}>
                <button 
                    onClick={() => navigate('/')} 
                    style={{ background: 'none', border: 'none', color: 'white', display: 'flex', alignItems: 'center', gap: '8px', cursor: 'pointer', fontSize: '1rem', fontWeight: 'bold' }}
                >
                    <ArrowLeft size={20} /> Back Home
                </button>
                <h1 style={{ fontSize: '1.2rem', margin: 0, background: 'linear-gradient(to right, #38bdf8, #818cf8)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent', letterSpacing: '1px' }}>
                    PC BUILDER ZONE
                </h1>
            </div>

            <main style={{ padding: '40px', flex: 1, maxWidth: '1400px', margin: '0 auto', width: '100%' }}>
                
                {/* Hero / Title */}
                <div style={{ textAlign: 'center', marginBottom: '50px' }}>
                    <h2 style={{ fontSize: '3rem', fontWeight: '800', marginBottom: '15px', color: 'white', textShadow: '0 0 30px rgba(56, 189, 248, 0.3)' }}>
                        Premium Components
                    </h2>
                    <p style={{ color: '#94a3b8', fontSize: '1.2rem', maxWidth: '600px', margin: '0 auto' }}>
                        Discover top-tier hardware for your next dream build. From processors to cooling, we have it all.
                    </p>
                </div>

                {/* Grid */}
                <div style={{ 
                    display: 'grid', 
                    gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))', 
                    gap: '30px' 
                }}>
                    {categories.map((cat) => (
                        <div 
                            key={cat.id} 
                            style={{ 
                                position: 'relative',
                                height: '320px',
                                borderRadius: '24px',
                                overflow: 'hidden',
                                cursor: 'pointer',
                                border: '1px solid rgba(255,255,255,0.1)',
                                transition: 'all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275)',
                                group: 'card'
                            }}
                            className="component-card"
                            onClick={() => navigate(`/products?category=${cat.id}`)}
                            onMouseEnter={(e) => {
                                e.currentTarget.style.transform = 'translateY(-10px)';
                                e.currentTarget.style.boxShadow = '0 20px 40px -10px rgba(0,0,0,0.5)';
                                e.currentTarget.style.borderColor = 'rgba(56, 189, 248, 0.5)';
                                e.currentTarget.querySelector('.bg-img').style.transform = 'scale(1.1)';
                                e.currentTarget.querySelector('.content-overlay').style.background = 'linear-gradient(to top, rgba(2,6,23,0.95), rgba(2,6,23,0.3))';
                            }}
                            onMouseLeave={(e) => {
                                e.currentTarget.style.transform = 'translateY(0)';
                                e.currentTarget.style.boxShadow = 'none';
                                e.currentTarget.style.borderColor = 'rgba(255,255,255,0.1)';
                                e.currentTarget.querySelector('.bg-img').style.transform = 'scale(1)';
                                e.currentTarget.querySelector('.content-overlay').style.background = 'linear-gradient(to top, rgba(2,6,23,0.9), transparent)';
                            }}
                        >
                            {/* Background Image */}
                            <img 
                                className="bg-img"
                                src={cat.image} 
                                alt={cat.title} 
                                style={{
                                    width: '100%',
                                    height: '100%',
                                    objectFit: 'cover',
                                    transition: 'transform 0.6s ease',
                                }}
                            />
                            
                            {/* Gradient Overlay */}
                            <div className="content-overlay" style={{
                                position: 'absolute',
                                inset: 0,
                                background: 'linear-gradient(to top, rgba(2,6,23,0.9), transparent)',
                                display: 'flex',
                                flexDirection: 'column',
                                justifyContent: 'flex-end',
                                padding: '25px',
                                transition: 'background 0.3s ease'
                            }}>
                                <div style={{ 
                                    marginBottom: '10px', 
                                    background: 'rgba(56, 189, 248, 0.2)', 
                                    width: 'fit-content', 
                                    padding: '8px', 
                                    borderRadius: '12px',
                                    color: '#38bdf8',
                                    backdropFilter: 'blur(4px)'
                                }}>
                                    {cat.icon}
                                </div>
                                <h3 style={{ fontSize: '1.5rem', fontWeight: 'bold', margin: '0 0 5px', color: 'white' }}>
                                    {cat.title}
                                </h3>
                                <p style={{ color: '#cbd5e1', fontSize: '0.95rem', margin: 0, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                                    {cat.description}
                                    <span style={{ 
                                        background: 'rgba(255,255,255,0.1)', 
                                        borderRadius: '50%', 
                                        padding: '4px',
                                        display: 'flex'
                                    }}>
                                        <ChevronRight size={16} />
                                    </span>
                                </p>
                            </div>
                        </div>
                    ))}
                </div>
            </main>
        </div>
    );
};

export default ComponentsPage;
