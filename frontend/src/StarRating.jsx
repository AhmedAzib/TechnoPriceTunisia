
import React from 'react';
import { Star, StarHalf } from 'lucide-react';

const StarRating = ({ rating, count, size = 16, interactive = false, onRate }) => {
    // Internal hover state for interactive mode
    const [hoverVal, setHoverVal] = React.useState(0);

    // Round to nearest 0.5 for display (if not hovering)
    // If hovering, show the hover value
    const effectiveRating = hoverVal > 0 ? hoverVal : rating;

    const roundedRating = Math.round(effectiveRating * 2) / 2;
    const fullStars = Math.floor(roundedRating);
    const hasHalfStar = roundedRating % 1 !== 0;

    const renderStars = () => {
        const stars = [];
        for (let i = 1; i <= 5; i++) {
            // Determine fill state based on hover or rating
            let isFull = i <= fullStars;
            let isHalf = (i === fullStars + 1 && hasHalfStar);
            
            // Interaction Props
            const eventProps = interactive ? {
                onMouseEnter: () => setHoverVal(i),
                onMouseLeave: () => setHoverVal(0),
                onClick: () => onRate && onRate(i)
            } : {};

            if (isFull) {
                // Full Star
                stars.push(
                    <Star 
                        key={i} 
                        size={size} 
                        fill="#fbbf24" 
                        color="#fbbf24" 
                        style={{ cursor: interactive ? 'pointer' : 'default', transition: 'transform 0.1s' }}
                        {...eventProps}
                    />
                );
            } else if (isHalf) {
                // Half Star (Only for non-hover state usually, or precise hover)
                // For simplicity in hover, we usually just do full stars. 
                // But let's keep half star logic if it comes from 'rating' prop.
                stars.push(
                    <div key={i} style={{ position: 'relative', width: size, height: size, cursor: interactive ? 'pointer' : 'default' }} {...eventProps}>
                        <Star size={size} color="#fbbf24" style={{ position: 'absolute', left: 0, opacity: 0.3 }} />
                        <StarHalf size={size} fill="#fbbf24" color="#fbbf24" style={{ position: 'absolute', left: 0 }} />
                    </div>
                );
            } else {
                // Empty Star
                stars.push(
                    <Star 
                        key={i} 
                        size={size} 
                        color="#fbbf24" 
                        style={{ opacity: 0.3, cursor: interactive ? 'pointer' : 'default' }} 
                        {...eventProps}
                    />
                );
            }
        }
        return stars;
    };

    return (
        <div 
            style={{ display: 'flex', alignItems: 'center', gap: '4px' }} 
            onMouseLeave={() => interactive && setHoverVal(0)}
        >
            <div style={{ display: 'flex' }}>
                {renderStars()}
            </div>
            {count !== undefined && (
                <span style={{ fontSize: '0.8rem', color: '#94a3b8', marginLeft: '4px' }}>
                    ({count})
                </span>
            )}
        </div>
    );
};

export default StarRating;
