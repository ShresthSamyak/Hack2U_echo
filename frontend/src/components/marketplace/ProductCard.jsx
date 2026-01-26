import React from 'react';
import { useNavigate } from 'react-router-dom';
import './ProductCard.css';

export default function ProductCard({ product, model }) {
    const navigate = useNavigate();

    const handleClick = () => {
        navigate(`/product/${model.model_id}`);
    };

    return (
        <div className="product-card" onClick={handleClick}>
            {/* Product Image */}
            <div className="product-image">
                {model.color_variants && model.color_variants.length > 0 ? (
                    <img
                        src={model.color_variants[0].image_url || '/placeholder.jpg'}
                        alt={model.model_name}
                        onError={(e) => { e.target.src = '/placeholder.jpg'; }}
                    />
                ) : (
                    <div className="image-placeholder">
                        <span>{product.category}</span>
                    </div>
                )}

                {/* AI Badge */}
                <div className="ai-badge">
                    <span>🤖</span> AI Assistant
                </div>
            </div>

            {/* Product Info */}
            <div className="product-info">
                <h3 className="product-brand">{product.brand}</h3>
                <p className="product-name">{model.model_name}</p>
                <div className="product-footer">
                    <p className="product-price">${model.price}</p>
                    {model.warranty_years && (
                        <span className="warranty-badge">
                            {model.warranty_years}y warranty
                        </span>
                    )}
                </div>
            </div>
        </div>
    );
}
