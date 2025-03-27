"""
Main entry point for the cost-effectiveness analyzer.
"""
import argparse
from typing import List, Optional

from data_loader import DataLoader
from ingredient_analyzer import IngredientAnalyzer
from product_evaluator import ProductEvaluator

def list_products(products: List[dict]) -> None:
    """Display a numbered list of available products."""
    print("\nAvailable Products:")
    print("-" * 50)
    for i, product in enumerate(products, 1):
        print(f"{i}. {product['name']}")

def list_ingredients(product: dict) -> None:
    """Display a numbered list of ingredients in a product."""
    print(f"\nIngredients in {product['name']}:")
    print("-" * 50)
    for i, ingredient in enumerate(product['ingredients'], 1):
        print(f"{i}. {ingredient['name']} ({ingredient['amount']}{ingredient['unit']})")

def get_product_choice(products: List[dict]) -> dict:
    """Get user's product selection."""
    while True:
        try:
            choice = int(input("\nEnter product number to analyze (0 to exit): "))
            if choice == 0:
                exit(0)
            if 1 <= choice <= len(products):
                return products[choice - 1]
            print(f"Please enter a number between 1 and {len(products)}")
        except ValueError:
            print("Please enter a valid number")

def get_ingredient_filter(product: dict) -> Optional[List[str]]:
    """Get optional ingredient filter from user."""
    while True:
        filter_choice = input("\nAnalyze specific ingredients? (y/n): ").lower()
        if filter_choice not in ('y', 'n'):
            print("Please enter 'y' or 'n'")
            continue
            
        if filter_choice == 'n':
            return None
            
        # Show ingredients and get selection
        list_ingredients(product)
        print("\nEnter ingredient numbers separated by commas (e.g., '1,3'), or press Enter for all:")
        selection = input().strip()
        
        if not selection:
            return None
            
        try:
            indices = [int(i.strip()) - 1 for i in selection.split(',')]
            if all(0 <= i < len(product['ingredients']) for i in indices):
                return [product['ingredients'][i]['name'] for i in indices]
            print("Invalid ingredient number(s)")
        except ValueError:
            print("Invalid input format")

def main():
    """Main execution function."""
    parser = argparse.ArgumentParser(description="Cost-Effectiveness Analyzer")
    parser.add_argument('--hide-ingredients', action='store_true',
                      help='Hide detailed ingredient analysis in output')
    args = parser.parse_args()
    
    print("Cost-Effectiveness Analyzer")
    print("=" * 50)
    
    # Initialize components
    evaluator = ProductEvaluator()
    
    try:
        # Load data
        print("Loading data...")
        products, inferred_costs, dosages = evaluator.load_data()
        
        while True:
            # Display available products
            list_products(products)
            
            # Get product selection
            product = get_product_choice(products)
            
            # Get optional ingredient filter
            ingredient_filter = get_ingredient_filter(product)
            
            # Perform evaluation
            print("\nAnalyzing product...")
            evaluation = evaluator.evaluate_product(
                product,
                inferred_costs,
                dosages,
                ingredient_filter
            )
            
            # Display results
            print("\n" + evaluator.format_evaluation_report(evaluation, show_ingredients=not args.hide_ingredients))
            
            # Ask to continue
            if input("\nAnalyze another product? (y/n): ").lower() != 'y':
                break
                
        print("\nThank you for using the Cost-Effectiveness Analyzer!")
        
    except FileNotFoundError as e:
        print(f"\nError: Required data file not found: {e}")
        print("Please ensure all required JSON files are present in the data directory.")
    except Exception as e:
        print(f"\nAn error occurred: {e}")

if __name__ == '__main__':
    main()
