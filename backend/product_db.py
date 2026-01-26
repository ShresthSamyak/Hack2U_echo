import json
from pathlib import Path
from typing import List, Dict, Optional

class ProductDatabase:
    """Product knowledge management system"""
    
    def __init__(self, data_path: str = "data/products.json"):
        self.data_path = Path(__file__).parent / data_path
        self.products = self._load_products()
    
    def _load_products(self) -> Dict:
        """Load product catalog from JSON file"""
        with open(self.data_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def get_all_categories(self) -> List[str]:
        """Get all product categories"""
        return list(self.products.keys())
    
    def get_category_products(self, category: str) -> List[Dict]:
        """Get all products in a category"""
        return self.products.get(category, [])
    
    def search_by_features(self, category: str, features: List[str]) -> List[Dict]:
        """Search products by features"""
        category_products = self.get_category_products(category)
        results = []
        
        for product in category_products:
            for model in product.get('models', []):
                model_features = [f.lower() for f in model.get('features', [])]
                if any(feat.lower() in model_features for feat in features):
                    results.append({**product, 'matched_model': model})
        
        return results
    
    def get_product_by_id(self, product_id: str) -> Optional[Dict]:
        """Get product by ID"""
        for category in self.products.values():
            for product in category:
                if product['product_id'] == product_id:
                    return product
        return None
    
    def get_model_by_id(self, model_id: str) -> Optional[tuple[Dict, Dict]]:
        """Get model by ID, returns (product, model)"""
        for category in self.products.values():
            for product in category:
                for model in product.get('models', []):
                    if model['model_id'] == model_id:
                        return (product, model)
        return None
    
    def get_color_variants(self, product_id: str) -> List[Dict]:
        """Get all color variants of a product"""
        product = self.get_product_by_id(product_id)
        if product:
            return product.get('models', [])
        return []
    
    def get_by_price_range(self, category: str, min_price: float, max_price: float) -> List[Dict]:
        """Get products within price range"""
        category_products = self.get_category_products(category)
        results = []
        
        for product in category_products:
            for model in product.get('models', []):
                if min_price <= model.get('price', 0) <= max_price:
                    results.append({**product, 'matched_model': model})
        
        return results
    
    def get_error_code_info(self, model_id: str, error_code: str) -> Optional[Dict]:
        """Get error code explanation for a specific model"""
        result = self.get_model_by_id(model_id)
        if not result:
            return None
        
        product, model = result
        common_issues = model.get('common_issues', [])
        
        for issue in common_issues:
            if issue.get('error', '').upper() == error_code.upper():
                return issue
        
        return None
    
    def get_installation_info(self, model_id: str) -> Optional[str]:
        """Get installation instructions for a model"""
        result = self.get_model_by_id(model_id)
        if result:
            _, model = result
            return model.get('installation')
        return None
    
    def get_maintenance_info(self, model_id: str) -> Optional[str]:
        """Get maintenance schedule for a model"""
        result = self.get_model_by_id(model_id)
        if result:
            _, model = result
            return model.get('maintenance')
        return None
    
    def get_warranty_info(self, model_id: str) -> Optional[int]:
        """Get warranty years for a model"""
        result = self.get_model_by_id(model_id)
        if result:
            _, model = result
            return model.get('warranty_years')
        return None

# Global instance
product_db = ProductDatabase()
