import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import MarketplacePage from './pages/MarketplacePage';
import ProductDetailPage from './pages/ProductDetailPage';
import './styles/theme.css';

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<MarketplacePage />} />
        <Route path="/product/:modelId" element={<ProductDetailPage />} />
      </Routes>
    </BrowserRouter>
  );
}
