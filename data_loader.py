"""
Module for loading and standardizing data from JSON files for the cost-effectiveness analyzer.
"""
import json
from typing import Any, Dict, List, Union
from pathlib import Path

# Type aliases for clarity
ProductData = Dict[str, Any]
SingleData = Dict[str, Any]
DosageData = Dict[str, Dict[str, Union[float, str]]]

class DataLoader:
    """Handles loading and standardization of product, single ingredient, and dosage data."""
    
    # Mapping of units to their conversion factor to milligrams
    UNIT_CONVERSIONS = {
        'mg': 1,
        'g': 1000,
        'kg': 1000000,
        'mcg': 0.001,  # micrograms
    }

    def __init__(self, data_dir: str = 'data'):
        """
        Initialize the DataLoader with the directory containing the JSON files.
        
        Args:
            data_dir: Directory containing the JSON data files
        """
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)  # Create data directory if it doesn't exist

    def load_json(self, filename: str) -> Union[List[Dict], Dict]:
        """
        Load data from a JSON file.
        
        Args:
            filename: Name of the JSON file to load
            
        Returns:
            Loaded JSON data as a dictionary or list
            
        Raises:
            FileNotFoundError: If the specified file doesn't exist
            json.JSONDecodeError: If the file contains invalid JSON
        """
        filepath = self.data_dir / filename
        try:
            with open(filepath, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"Data file not found: {filepath}")
        except json.JSONDecodeError:
            raise ValueError(f"Invalid JSON in file: {filepath}")

    def standardize_amount(self, amount: float, unit: str) -> float:
        """
        Convert an amount from the given unit to milligrams.
        
        Args:
            amount: The amount to convert
            unit: The unit to convert from ('mg', 'g', 'kg', or 'mcg')
            
        Returns:
            The amount in milligrams
            
        Raises:
            ValueError: If the unit is not supported
        """
        unit = unit.lower()
        if unit not in self.UNIT_CONVERSIONS:
            raise ValueError(f"Unsupported unit: {unit}")
        return amount * self.UNIT_CONVERSIONS[unit]

    def standardize_product(self, product: ProductData) -> ProductData:
        """
        Standardize all ingredient amounts in a product to milligrams.
        
        Args:
            product: Product data dictionary
            
        Returns:
            Product data with standardized ingredient amounts
        """
        standardized = product.copy()
        for ingredient in standardized['ingredients']:
            original_amount = ingredient['amount']
            original_unit = ingredient['unit']
            ingredient['amount_mg'] = self.standardize_amount(original_amount, original_unit)
        return standardized

    def standardize_single(self, single: SingleData) -> SingleData:
        """
        Standardize the total quantity in a single-ingredient product to milligrams.
        
        Args:
            single: Single-ingredient product data dictionary
            
        Returns:
            Single-ingredient product data with standardized quantity
        """
        standardized = single.copy()
        quantity = standardized['total_quantity']
        unit = standardized['unit']
        standardized['total_quantity_mg'] = self.standardize_amount(quantity, unit)
        return standardized

    def load_all_data(self) -> tuple[List[ProductData], List[SingleData], DosageData]:
        """
        Load and standardize all data files.
        
        Returns:
            Tuple containing:
            - List of standardized multi-ingredient products
            - List of standardized single-ingredient products
            - Dictionary of dosage information
        """
        # Load raw data
        products = self.load_json('products.json')
        singles = self.load_json('singles.json')
        dosages = self.load_json('dosages.json')
        
        # Standardize amounts to milligrams
        standardized_products = [self.standardize_product(p) for p in products]
        standardized_singles = [self.standardize_single(s) for s in singles]
        
        # Convert dosage amounts to mg
        for ingredient, info in dosages.items():
            unit = info['unit']
            for key in ['min', 'optimal', 'max']:
                if key in info:
                    info[f'{key}_mg'] = self.standardize_amount(info[key], unit)
        
        return standardized_products, standardized_singles, dosages

def create_example_files(data_dir: str = 'data'):
    """
    Create example JSON files with sample data.
    
    Args:
        data_dir: Directory where the files should be created
    """
    data_path = Path(data_dir)
    data_path.mkdir(exist_ok=True)
    
    # Example products data
    products = [
        {
            "name": "Example Pre-Workout",
            "cost": 39.99,
            "servings": 30,
            "ingredients": [
                {"name": "Caffeine Anhydrous", "amount": 200, "unit": "mg"},
                {"name": "Beta-Alanine", "amount": 3.2, "unit": "g"},
                {"name": "Creatine Monohydrate", "amount": 5, "unit": "g"}
            ]
        }
    ]
    
    # Example singles data
    singles = [
        {
            "ingredient_name": "Caffeine Anhydrous",
            "product_name": "Brand X Caffeine 200mg 100 Tabs",
            "cost": 9.99,
            "total_quantity": 20,
            "unit": "g"
        },
        {
            "ingredient_name": "Beta-Alanine",
            "product_name": "Brand Y Beta-Alanine Powder 500g",
            "cost": 19.99,
            "total_quantity": 500,
            "unit": "g"
        }
    ]
    
    # Example dosages data
    dosages = {
        "Caffeine Anhydrous": {"min": 100, "optimal": 200, "max": 400, "unit": "mg"},
        "Beta-Alanine": {"min": 1600, "optimal": 3200, "max": 6400, "unit": "mg"},
        "Creatine Monohydrate": {"min": 3000, "optimal": 5000, "max": 10000, "unit": "mg"}
    }
    
    # Write example files
    with open(data_path / 'products.json', 'w') as f:
        json.dump(products, f, indent=2)
    
    with open(data_path / 'singles.json', 'w') as f:
        json.dump(singles, f, indent=2)
    
    with open(data_path / 'dosages.json', 'w') as f:
        json.dump(dosages, f, indent=2)

if __name__ == '__main__':
    # Create example files if run directly
    create_example_files()
    
    # Test loading the example files
    loader = DataLoader()
    try:
        products, singles, dosages = loader.load_all_data()
        print("Successfully loaded and standardized all data files!")
        print(f"\nLoaded {len(products)} products")
        print(f"Loaded {len(singles)} single-ingredient products")
        print(f"Loaded {len(dosages)} ingredient dosage profiles")
    except Exception as e:
        print(f"Error loading data: {str(e)}")
