
import React, { useState, useMemo, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import { Search, ChevronRight, Laptop, Filter, Grid, List as ListIcon, X, ArrowUpRight } from 'lucide-react';
import Navbar from './components/Navbar';
import { normalizeProductData, generateVariantKey, sortSizes } from './utils/productUtils';
import { MASTER_DATA } from './data/masterData';
import './ProductsPage.css'; // Reuse existing styles for now or create Catalog.css

const CatalogPage = () => {
    const [products, setProducts] = useState([]);
    const [searchParams, setSearchParams] = useSearchParams();
    const [searchQuery, setSearchQuery] = useState('');
    const [selectedGroup, setSelectedGroup] = useState(null);

    // Initial Load & Normalization
    useEffect(() => {
        const normalized = normalizeProductData(MASTER_DATA);
        setProducts(normalized);
    }, []);

    // Grouping Logic
    const groups = useMemo(() => {
        const grouped = {};
        
        products.forEach(p => {
            const key = generateVariantKey(p);
            if (!grouped[key]) {
                grouped[key] = {
                    key: key,
                    baseProduct: p,
                    variants: [],
                    brands: new Set(),
                    priceMin: p.price,
                    priceMax: p.price,
                    specsSet: {
                        cpu: new Set(),
                        ram: new Set(),
                        gpu: new Set()
                    }
                };
            }
            
            const g = grouped[key];
            g.variants.push(p);
            g.brands.add(p.brand);
            g.priceMin = Math.min(g.priceMin, p.price);
            g.priceMax = Math.max(g.priceMax, p.price);
            
            // Collect specs for summary
            if(p.specs.cpu) g.specsSet.cpu.add(p.specs.cpu);
            if(p.specs.ram) g.specsSet.ram.add(p.specs.ram);
            if(p.specs.gpu) g.specsSet.gpu.add(p.specs.gpu);
        });

        // Convert to array and filter by search
        let groupList = Object.values(grouped);
        
        if (searchQuery) {
            const q = searchQuery.toLowerCase();
            groupList = groupList.filter(g => 
                g.key.toLowerCase().includes(q) || 
                g.baseProduct.brand.toLowerCase().includes(q)
            );
        }

        return groupList;
    }, [products, searchQuery]);

    // Handle Active Group from URL
    useEffect(() => {
        const groupKey = searchParams.get('group');
        if (groupKey && products.length > 0) {
            // Find group roughly matching
            // Note: URL encoding might mismatch exact key spacing, so simplistic check
            const found = groups.find(g => g.key === groupKey);
            if (found) setSelectedGroup(found);
        }
    }, [searchParams, groups, products]);

    const openGroup = (g) => {
        setSelectedGroup(g);
        setSearchParams({ group: g.key });
    };

    const closeGroup = () => {
        setSelectedGroup(null);
        setSearchParams({});
    };

    return (
        <div className="product-page" style={{ background: '#E8F1F5', minHeight: '100vh', color: '#1A2B48' }}>
            <Navbar />
            
            {/* HERRO HEADER */}
            <div style={{ padding: '40px 5%', background: 'linear-gradient(to bottom, #f1f5f9, #E8F1F5)', borderBottom: '1px solid #e2e8f0' }}>
                <h1 style={{ fontSize: '2.5rem', fontWeight: '800', marginBottom: '10px', background: 'linear-gradient(90deg, #1A2B48, #64748b)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
                    Series Catalog
                </h1>
                <p style={{ color: '#64748b', fontSize: '1.1rem', maxWidth: '600px' }}>
                    Explore complete laptop lineups. Compare configurations and find the perfect match for your needs.
                </p>

                 {/* SEARCH BAR */}
                 <div style={{ marginTop: '30px', position: 'relative', maxWidth: '500px' }}>
                    <Search className="search-icon" size={20} style={{ position: 'absolute', left: '15px', top: '50%', transform: 'translateY(-50%)', color: '#64748b' }} />
                    <input 
                        type="text" 
                        placeholder="Search for a series (e.g. Legion 5, Victus 15)..." 
                        value={searchQuery}
                        onChange={(e) => setSearchQuery(e.target.value)}
                        style={{
                            width: '100%',
                            padding: '12px 15px 12px 45px',
                            background: 'white',
                            border: '1px solid #e2e8f0',
                            borderRadius: '12px',
                            color: '#1A2B48',
                            fontSize: '1rem',
                            outline: 'none'
                        }}
                    />
                </div>
            </div>

            {/* CATALOG GRID */}
            <div className="catalog-grid" style={{ 
                display: 'grid', 
                gridTemplateColumns: 'repeat(auto-fill, minmax(350px, 1fr))', 
                gap: '20px', 
                padding: '40px 5%' 
            }}>
                {groups.map(group => (
                    <div key={group.key} className="series-card" onClick={() => openGroup(group)} style={{
                        background: 'white',
                        border: '1px solid #e2e8f0',
                        borderRadius: '16px',
                        overflow: 'hidden',
                        cursor: 'pointer',
                        transition: 'transform 0.2s, background 0.2s',
                        position: 'relative'
                    }}>
                        {/* HEADER IMAGE */}
                        <div style={{ height: '200px', overflow: 'hidden', padding: '20px', background: 'white', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                            <img src={group.baseProduct.image} alt={group.key} style={{ maxHeight: '100%', objectFit: 'contain' }} />
                        </div>
                        
                        {/* CONTENT */}
                        <div style={{ padding: '20px' }}>
                            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start', marginBottom: '10px' }}>
                                <span style={{ fontSize: '0.75rem', fontWeight: 'bold', color: '#64748b', textTransform: 'uppercase' }}>
                                    {[...group.brands].join(', ')}
                                </span>
                                <span style={{ background: '#5F8D8B', color: 'white', fontSize: '0.7rem', fontWeight: '800', padding: '2px 8px', borderRadius: '4px' }}>
                                    {group.variants.length} CONFIGS
                                </span>
                            </div>
                            
                            <h3 style={{ fontSize: '1.2rem', fontWeight: '700', marginBottom: '15px', lineHeight: '1.4' }}>
                                {group.key}
                            </h3>

                            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px', marginBottom: '20px' }}>
                                {[...group.specsSet.cpu].slice(0, 3).map(cpu => (
                                    <span key={cpu} style={{ fontSize: '0.75rem', background: '#f1f5f9', padding: '4px 8px', borderRadius: '4px' }}>
                                        {cpu}
                                    </span>
                                ))}
                                {group.specsSet.cpu.size > 3 && <span style={{ fontSize: '0.75rem', color: '#64748b' }}>+More</span>}
                            </div>

                            <div style={{ borderTop: '1px solid #e2e8f0', paddingTop: '15px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                                <div>
                                    <div style={{ fontSize: '0.8rem', color: '#94a3b8' }}>Starting from</div>
                                    <div style={{ fontSize: '1.2rem', fontWeight: 'bold', color: '#10b981' }}>
                                        {group.priceMin} TND
                                    </div>
                                </div>
                                <button style={{ 
                                    background: 'transparent',
                                    border: '1px solid #e2e8f0',
                                    color: '#1A2B48',
                                    width: '36px',
                                    height: '36px',
                                    borderRadius: '50%',
                                    display: 'flex', 
                                    alignItems: 'center', 
                                    justifyContent: 'center' 
                                }}>
                                    <ChevronRight size={18} />
                                </button>
                            </div>
                        </div>
                    </div>
                ))}
            </div>

            {/* DETAILS MODAL */}
            {selectedGroup && (
                <div className="catalog-modal-overlay" onClick={closeGroup} style={{
                    position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.85)', backdropFilter: 'blur(10px)', zIndex: 9999,
                    display: 'flex', alignItems: 'center', justifyContent: 'center'
                }}>
                    <div className="catalog-modal-content" onClick={e => e.stopPropagation()} style={{
                        background: 'white', width: '90%', maxWidth: '800px', maxHeight: '90vh', overflowY: 'auto',
                        borderRadius: '24px', border: '1px solid #e2e8f0', boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.15)'
                    }}>
                        {/* HEADER */}
                        <div style={{ padding: '30px', borderBottom: '1px solid #e2e8f0', display: 'flex', justifyContent: 'space-between', alignItems: 'start' }}>
                            <div>
                                <h2 style={{ fontSize: '1.8rem', fontWeight: 'bold', marginBottom: '5px' }}>{selectedGroup.key}</h2>
                                <p style={{ color: '#94a3b8' }}>{selectedGroup.variants.length} configurations available across multiple stores.</p>
                            </div>
                            <button onClick={closeGroup} style={{ background: '#f1f5f9', border: 'none', borderRadius: '50%', width: '40px', height: '40px', color: '#1A2B48', cursor: 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                                <X size={20} />
                            </button>
                        </div>

                        {/* LIST */}
                        <div style={{ padding: '20px' }}>
                            {selectedGroup.variants
                                .sort((a,b) => a.price - b.price)
                                .map((v, idx) => (
                                <div key={idx} style={{ 
                                    display: 'flex', 
                                    alignItems: 'center', 
                                    background: '#f1f5f9',
                                    padding: '20px',
                                    borderRadius: '12px',
                                    marginBottom: '10px',
                                    border: '1px solid #e2e8f0',
                                    transition: 'background 0.2s',
                                    gap: '20px'
                                }}>
                                    {/* THUMB */}
                                    <div style={{ width: '60px', height: '60px', background: 'white', borderRadius: '8px', padding: '5px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                                        <img src={v.image} alt="" style={{ maxWidth: '100%', maxHeight: '100%' }} />
                                    </div>

                                    {/* SPECS */}
                                    <div style={{ flex: 1 }}>
                                        <div style={{ display: 'flex', gap: '10px', marginBottom: '5px' }}>
                                            <span style={{ fontWeight: 'bold' }}>{v.specs.ram || "RAM?"}</span>
                                            <span style={{ color: '#64748b' }}>/</span>
                                            <span style={{ fontWeight: 'bold' }}>{v.specs.storage || "Storage?"}</span>
                                        </div>
                                        <div style={{ fontSize: '0.9rem', color: '#94a3b8' }}>
                                            {v.specs.cpu} • {v.specs.gpu} • {v.specs.screen}
                                        </div>
                                        <div style={{ marginTop: '5px', fontSize: '0.8rem', color: '#64748b', display: 'flex', alignItems: 'center', gap: '6px' }}>
                                            <span style={{ 
                                                width: '8px', height: '8px', borderRadius: '50%', 
                                                background: v.specs.os === 'Windows' ? '#3b82f6' : '#64748b' 
                                            }} />
                                            {v.specs.os}
                                        </div>
                                    </div>

                                    {/* PRICE & STORE */}
                                    <div style={{ textAlign: 'right' }}>
                                        <div style={{ fontSize: '1.25rem', fontWeight: 'bold', color: '#10b981', marginBottom: '5px' }}>
                                            {v.price} TND
                                        </div>
                                        <div style={{ fontSize: '0.85rem', color: '#94a3b8', marginBottom: '8px' }}>
                                            via {v.source}
                                        </div>
                                        <a href={v.link} target="_blank" rel="noopener noreferrer" style={{
                                            display: 'inline-flex', alignItems: 'center', gap: '5px',
                                            background: '#5F8D8B', color: 'white', textDecoration: 'none',
                                            padding: '8px 16px', borderRadius: '6px', fontWeight: 'bold', fontSize: '0.9rem'
                                        }}>
                                            View Offer <ArrowUpRight size={14} />
                                        </a>
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

export default CatalogPage;
