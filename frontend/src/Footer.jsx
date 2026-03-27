
import React from 'react';
import { Link } from 'react-router-dom';
import { Facebook, Instagram, Twitter, Mail, MapPin, Phone, Github } from 'lucide-react';
import './Footer.css';

const Footer = () => {
  return (
    <footer className="site-footer">
      <div className="footer-content">
        <div className="footer-col">
          <h3>TechnoPriceTunisia</h3>
          <p>
            The future of tech retail. High-performance gaming systems, 
            professional workstations, and next-gen peripherals.
          </p>
          <div className="socials">
            <a href="#" aria-label="Facebook"><Facebook size={18} /></a>
            <a href="#" aria-label="Instagram"><Instagram size={18} /></a>
            <a href="#" aria-label="Twitter"><Twitter size={18} /></a>
            <a href="#" aria-label="Github"><Github size={18} /></a>
          </div>
        </div>

        <div className="footer-col">
          <h3>Quick Links</h3>
          <Link to="/">Home</Link>
          <Link to="/products">Browse Inventory</Link>
          <Link to="/wishlist">My Wishlist</Link>
          <Link to="/compare">Compare Models</Link>
          <Link to="/about">Learn More</Link>
        </div>

        <div className="footer-col">
          <h3>Contact Us</h3>
          <a href="mailto:support@antigravity.tn"><Mail size={16} /> support@antigravity.tn</a>
          <a href="tel:+21671000000"><Phone size={16} /> +216 71 000 000</a>
          <p><MapPin size={16} /> 123 Tech Avenue, Tunis</p>
        </div>
      </div>
      <div className="footer-bottom">
        &copy; {new Date().getFullYear()} TechnoPriceTunisia. All rights reserved. 
        Designed for the Future.
      </div>
    </footer>
  );
};

export default Footer;
