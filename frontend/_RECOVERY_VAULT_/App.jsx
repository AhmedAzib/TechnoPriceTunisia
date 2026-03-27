import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { CompareProvider } from './context/CompareContext';
import { WishlistProvider } from './context/WishlistContext';
import HomePage from './HomePage';
import ProductsPage from './ProductsPage';
import ProductDetailsPage from './ProductDetailsPage';
import ComparePage from './ComparePage';
import WishlistPage from './WishlistPage';
import LoginPage from './LoginPage';
import RegisterPage from './RegisterPage';
import { AuthProvider } from './AuthContext';
import Footer from './Footer';

function App() {
  return (
    <Router>
      <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
        <AuthProvider>
          <WishlistProvider>
            <CompareProvider>
              <Routes>
                <Route path="/" element={<HomePage />} />
                <Route path="/products" element={<ProductsPage />} />
                <Route path="/product/:id" element={<ProductDetailsPage />} />
                <Route path="/compare" element={<ComparePage />} />
                <Route path="/wishlist" element={<WishlistPage />} />
                <Route path="/login" element={<LoginPage />} />
                <Route path="/register" element={<RegisterPage />} />
              </Routes>
              
              {/* The Footer MUST be here, outside Routes but inside the Flex container */}
              <Footer /> 
            </CompareProvider>
          </WishlistProvider>
        </AuthProvider>
      </div>
    </Router>
  );
}

export default App;