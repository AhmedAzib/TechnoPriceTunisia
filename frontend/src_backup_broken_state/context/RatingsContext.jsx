
import React, { createContext, useContext, useState, useEffect } from 'react';

const RatingsContext = createContext();

export const useRatings = () => useContext(RatingsContext);

export const RatingsProvider = ({ children }) => {
    // Store user's own ratings: { [productId]: ratingValue }
    const [userRatings, setUserRatings] = useState(() => {
        const saved = localStorage.getItem('user_ratings');
        return saved ? JSON.parse(saved) : {};
    });

    useEffect(() => {
        localStorage.setItem('user_ratings', JSON.stringify(userRatings));
    }, [userRatings]);

    const submitRating = (productId, rating) => {
        setUserRatings(prev => ({
            ...prev,
            [productId]: rating
        }));
        // Show success logic or toast could be handled by UI
    };

    /**
     * Calculates the "Live" average rating including the current user's vote.
     * @param {Object} product - The product object having 'rating' (base average) and 'reviewCount' (base count)
     * @returns {Object} { average, count, userRatedValue }
     */
    const getProductRating = (product) => {
        // Safe access
        if (!product) return { average: 0, count: 0, userRatedValue: null };

        const baseAvg = product.rating || 0;
        const baseCount = product.reviewCount || 0;
        const myRating = userRatings[product.id || product.link];

        if (myRating) {
            // Formula: New Average = ((Old Avg * Old Count) + New Rating) / (Old Count + 1)
            // Note: If we wanted to allow *changing* a vote, handling would be complex if "Base" already included us.
            // But here "Base" is "Everyone else" (static file), so we just add ourselves on top.
            const totalScore = (baseAvg * baseCount) + myRating;
            const newCount = baseCount + 1;
            const newAvg = totalScore / newCount;
            
            return {
                average: newAvg,
                count: newCount,
                userRatedValue: myRating
            };
        }

        return {
            average: baseAvg,
            count: baseCount,
            userRatedValue: null
        };
    };

    return (
        <RatingsContext.Provider value={{ submitRating, getProductRating, userRatings }}>
            {children}
        </RatingsContext.Provider>
    );
};
