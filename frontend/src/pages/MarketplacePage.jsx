import React, { useState, useEffect } from 'react';
import { api } from '../services/api';
import ProductCard from '../components/marketplace/ProductCard';
import '../styles/marketplace.css';

export default function MarketplacePage() {
    const [products, setProducts] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [activeCategory, setActiveCategory] = useState('all');

    // Fetch products on mount
    useEffect(() => {
        fetchProducts();
    }, []);

    const fetchProducts = async () => {
        try {
            setLoading(true);
            const data = await api.getProducts();
            // Backend returns {categories, all_products}, we need just all_products
            setProducts(data.all_products || data);
        } catch (err) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    // Get all products as flat array
    const getAllProductsArray = () => {
        if (!products) return [];

        const allProducts = [];
        Object.entries(products).forEach(([category, categoryProducts]) => {
            if (Array.isArray(categoryProducts)) {
                categoryProducts.forEach(product => {
                    // Add each model as a separate item
                    product.models?.forEach(model => {
                        allProducts.push({
                            category,
                            product,
                            model
                        });
                    });
                });
            }
        });
        return allProducts;
    };

    // Filter products by category
    const getFilteredProducts = () => {
        const allProducts = getAllProductsArray();
        if (activeCategory === 'all') return allProducts;
        return allProducts.filter(item => item.category === activeCategory);
    };

    const categories = [
        { id: 'all', label: 'All Products' },
        { id: 'washing_machines', label: 'Washing Machines' },
        { id: 'refrigerators', label: 'Refrigerators' },
        { id: 'headphones', label: 'Headphones' },
    ];

    const filteredProducts = getFilteredProducts();

    return (
        <div className="marketplace-page">
            <div className="container">
                <header className="marketplace-header">
                    <h1>Product Intelligence Agent</h1>
                    <p className="subtitle">Browse products with AI assistance</p>
                </header>

                {/* Category Filter */}
                <div className="category-filter">
                    {categories.map(cat => (
                        <button
                            key={cat.id}
                            className={`category-btn ${activeCategory === cat.id ? 'active' : ''}`}
                            onClick={() => setActiveCategory(cat.id)}
                        >
                            {cat.label}
                        </button>
                    ))}
                </div>

                {/* Product Grid */}
                {loading && (
                    <div className="loading-placeholder">
                        <div className="spinner"></div>
                        <p>Loading products...</p>
                    </div>
                )}

                {error && (
                    <div className="error-placeholder">
                        <p>❌ Error loading products: {error}</p>
                        <button onClick={fetchProducts} className="btn btn-primary">
                            Try Again
                        </button>
                    </div>
                )}

                {!loading && !error && (
                    <div className="product-grid">
                        {filteredProducts.length === 0 ? (
                            <div className="empty-placeholder">
                                <p>No products found in this category.</p>
                            </div>
                        ) : (
                            filteredProducts.map((item, index) => (
                                <ProductCard
                                    key={`${item.model.model_id}-${index}`}
                                    product={item.product}
                                    model={item.model}
                                />
                            ))
                        )}
                    </div>
                )}
            </div>
        </div>
    );
}
