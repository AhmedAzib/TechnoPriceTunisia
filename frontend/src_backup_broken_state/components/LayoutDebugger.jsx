import React, { useEffect, useState } from 'react';

const LayoutDebugger = () => {
    const [traitors, setTraitors] = useState([]);
    const [docWidth, setDocWidth] = useState(0);
    const [audit, setAudit] = useState({});

    useEffect(() => {
        console.log("!!! LAYOUT DEBUGGER MOUNTED !!!"); 
        const checkLayout = () => {
            const width = document.documentElement.offsetWidth;
            setDocWidth(width);
            
            // --- 1. TRAITOR CHECK (Horizontal Overflow) ---
            const foundTraitors = [];
            const allElements = document.querySelectorAll('*');
            allElements.forEach(el => {
                if (el.id === 'layout-debugger-overlay' || el.tagName === 'SCRIPT' || el.tagName === 'STYLE') return;
                
                // Only flag if significantly larger (buffer of 1px)
                if (el.offsetWidth > width + 1) {
                    el.style.outline = '5px solid red';
                    foundTraitors.push({
                        name: el.tagName.toLowerCase() + (el.className ? '.'+el.className.split(' ')[0] : ''),
                        width: el.offsetWidth,
                        diff: el.offsetWidth - width
                    });
                }
            });
            setTraitors(foundTraitors);

            // --- 2. CSS AUDIT (Structural Integrity) ---
            // This detects if the Mobile Override is actually working
            const layout = document.querySelector('.products-layout');
            const sidebar = document.querySelector('.sidebar');
            const nav = document.querySelector('.mobile-filter-strip');

            const newAudit = {
                layoutMode: layout ? window.getComputedStyle(layout).display : 'N/A', // Should be 'block' on mobile
                layoutCols: layout ? window.getComputedStyle(layout).gridTemplateColumns : 'N/A', // Should be 'none'
                sidebarDisplay: sidebar ? window.getComputedStyle(sidebar).display : 'N/A', // Should be 'none'
                navPos: nav ? window.getComputedStyle(nav).position : 'N/A', // Should be 'fixed'
                navBottom: nav ? window.getComputedStyle(nav).bottom : 'N/A' // Should be '0px'
            };
            setAudit(newAudit);
        };

        checkLayout();
        window.addEventListener('resize', checkLayout);
        const interval = setInterval(checkLayout, 1000); 

        return () => {
             window.removeEventListener('resize', checkLayout);
             clearInterval(interval);
        };
    }, []);

    const isSafe = traitors.length === 0;

    return (
        <div id="layout-debugger-overlay" style={{
            position: 'fixed', top: 0, left: 0,
            width: isSafe ? 'auto' : '100%',
            height: isSafe ? 'auto' : '60vh',
            maxHeight: '60vh', overflowY: 'auto',
            background: 'rgba(0, 0, 0, 0.9)', 
            color: 'white', zIndex: 2147483647,
            padding: '10px', fontFamily: 'monospace', fontSize: '13px',
            border: isSafe ? '2px solid #00ff00' : '2px solid red',
            borderBottomRightRadius: '8px'
        }}>
            <div style={{borderBottom:'1px solid #555', paddingBottom:'5px', marginBottom:'5px'}}>
               <strong>🕵️ CSS AUDIT</strong>
            </div>
            
            {/* AUDIT REPORT */}
            <div style={{display:'grid', gridTemplateColumns:'max-content 1fr', gap:'5px 15px', marginBottom:'10px', fontSize:'11px', color:'#ccc'}}>
                <div>Layout Mode:</div> <div style={{color: audit.layoutMode === 'block' ? '#00ff00' : 'red', fontWeight:'bold'}}>{audit.layoutMode}</div>
                <div>Sidebar:</div> <div style={{color: audit.sidebarDisplay === 'none' ? '#00ff00' : 'red', fontWeight:'bold'}}>{audit.sidebarDisplay}</div>
                <div>Nav Pos:</div> <div style={{color: audit.navPos === 'fixed' ? '#00ff00' : 'red', fontWeight:'bold'}}>{audit.navPos}</div>
            </div>

            {isSafe ? (
                 <div style={{color:'#00ff00', fontWeight:'bold', fontSize:'14px'}}>✅ WIDTH SAFE ({docWidth}px)</div>
            ) : (
                <>
                    <div style={{color:'red', fontWeight:'bold', fontSize:'14px'}}>⚠️ WIDTH OVERFLOW</div>
                    <ul style={{margin: 0, paddingLeft: '20px', color:'red'}}>
                        {traitors.map((t, i) => (
                            <li key={i}>{t.name}: {t.width}px</li>
                        ))}
                    </ul>
                </>
            )}
            
            <div style={{marginTop:'10px', fontSize:'10px', color:'#888'}}>
                v2.0 Logic Analyzer
            </div>
        </div>
    );
};

export default LayoutDebugger;
