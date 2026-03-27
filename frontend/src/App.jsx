import React from 'react';
import { BrowserRouter as Router, Routes, Route, useLocation } from 'react-router-dom';
import { CompareProvider } from './context/CompareContext';
import { WishlistProvider } from './context/WishlistContext';
import HomePage from './HomePage';
import ProductsPage from './ProductsPage';
import CatalogPage from './CatalogPage';
import ProductDetailsPage from './ProductDetailsPage';
import ComparePage from './ComparePage';
import WishlistPage from './WishlistPage';
import LoginPage from './LoginPage';
import RegisterPage from './RegisterPage';
import LearnMorePage from './LearnMorePage';
import GroupDetailsPage from './GroupDetailsPage';
import MobileGroupDetailsPage from './MobileGroupDetailsPage';
import MobilesPage from './MobilesPage';
import ComponentsPage from './ComponentsPage';
import { AuthProvider } from './AuthContext';
import Footer from './Footer';
import { RatingsProvider } from './context/RatingsContext';

import ScrollToTop from './ScrollToTop';

// Content Wrapper to use useLocation hook
const AppContent = () => {
  const location = useLocation();
  const hideGlobalFooter = location.pathname === '/products' || location.pathname === '/mobiles';

  return (
    <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column', backgroundColor: '#E8F1F5', color: '#1A2B48' }}>
        <AuthProvider>
          <WishlistProvider>
            <CompareProvider>
              <RatingsProvider>
                <Routes>
                  <Route path="/" element={<HomePage />} />
                  <Route path="/products" element={<ProductsPage />} />
                  <Route path="/catalog" element={<CatalogPage />} />
                  <Route path="/product/:id" element={<ProductDetailsPage />} />
                  <Route path="/compare" element={<ComparePage />} />
                  <Route path="/wishlist" element={<WishlistPage />} />
                  <Route path="/login" element={<LoginPage />} />
                  <Route path="/register" element={<RegisterPage />} />
                  <Route path="/about" element={<LearnMorePage />} />
                  <Route path="/group/:groupKey" element={<GroupDetailsPage />} />
                  <Route path="/mobile-group/:groupKey" element={<MobileGroupDetailsPage />} />
                  <Route path="/mobiles" element={<MobilesPage />} />
                  <Route path="/components" element={<ComponentsPage />} />
                </Routes>
                
                {/* The Footer is hidden on Products Page because it's rendered inside the layout there */}
                {!hideGlobalFooter && <Footer />} 
              </RatingsProvider>
            </CompareProvider>
          </WishlistProvider>
        </AuthProvider>
      </div>
  );
};

function App() {
  return (
    <Router>
      <ScrollToTop />
      <AppContent />
    </Router>
  );
}

export default App;