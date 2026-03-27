import React, { createContext, useState, useContext, useEffect } from 'react';

const WishlistContext = createContext();

export const WishlistProvider = ({ children }) => {
  // Initialize from LocalStorage
  const [wishlist, setWishlist] = useState(() => {
    const saved = localStorage.getItem('my-wishlist');
    return saved ? JSON.parse(saved) : [];
  });

  // Sync to LocalStorage whenever wishlist changes
  useEffect(() => {
    localStorage.setItem('my-wishlist', JSON.stringify(wishlist));
  }, [wishlist]);

  const toggleWishlist = (product) => {
    const exists = wishlist.find(p => p.id === product.id);
    if (exists) {
      setWishlist(wishlist.filter(p => p.id !== product.id));
    } else {
      setWishlist([...wishlist, product]);
    }
  };

  const isInWishlist = (id) => !!wishlist.find(p => p.id === id);

  return (
    <WishlistContext.Provider value={{ wishlist, toggleWishlist, isInWishlist }}>
      {children}
    </WishlistContext.Provider>
  );
};

export const useWishlist = () => useContext(WishlistContext);
