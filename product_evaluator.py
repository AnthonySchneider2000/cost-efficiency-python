"""
Module for evaluating product cost-effectiveness in the cost-effectiveness analyzer.
"""
import csv
import os
from typing import Dict, List, Optional, NamedTuple
from dataclasses import dataclass

from data_loader import DataLoader
from ingredient_analyzer import IngredientAnalyzer, DosageScore

@dataclass
class IngredientEvaluation:
    """Evaluation results for a single ingredient."""
    name: str
    amount_mg: float
    dosage_score: DosageScore
    value_contribution: float
    cost_per_mg: float

@dataclass
class SkippedIngredient:
    """Information about a skipped ingredient."""
    name: str
    reason: str  # 'missing_cost' or 'missing_dosage'

@dataclass
class ProductEvaluation:
    """Complete evaluation results for a product."""
    name: str
    cost_per_serving: float
    total_value: float
    cost_effectiveness_score: float
    ingredients: List[IngredientEvaluation]
    analyzed_ingredients: int
    total_ingredients: int
    skipped_ingredients: List[SkippedIngredient]

class ProductEvaluator:
    """Evaluates product cost-effectiveness based on ingredients."""

    def __init__(self):
        """Initialize the evaluator with required components."""
        self.data_loader = DataLoader()
        self.ingredient_analyzer = IngredientAnalyzer()

    def load_data(self) -> tuple[List[Dict], Dict[str, float], Dict]:
        """
        Load and prepare all required data.
        
        Returns:
            Tuple containing:
            - List of standardized products
            - Dictionary of inferred ingredient costs
            - Dictionary of dosage information
        """
        products, singles, dosages = self.data_loader.load_all_data()
        inferred_costs = self.ingredient_analyzer.calculate_inferred_costs(singles)
        return products, inferred_costs, dosages

    def evaluate_product(
        self,
        product: Dict,
        inferred_costs: Dict,
        dosage_data: Dict,
        ingredient_filter: Optional[List[str]] = None
    ) -> ProductEvaluation:
        """
        Evaluate a product's cost-effectiveness.
        
        Args:
            product: Product data dictionary
            inferred_costs: Dictionary of inferred costs per ingredient
            dosage_data: Dictionary of dosage information
            ingredient_filter: Optional list of ingredients to analyze
            
        Returns:
            ProductEvaluation containing the analysis results
        """
        evaluated_ingredients = []
        skipped_ingredients = []
        total_value = 0.0
        analyzed_count = 0
        
        # Calculate cost per serving
        cost_per_serving = product['cost'] / product['servings']
        
        # Evaluate each ingredient
        for ingredient in product['ingredients']:
            name = ingredient['name']
            
            # Check if ingredient has cost data
            if name not in inferred_costs:
                skipped_ingredients.append(SkippedIngredient(name=name, reason='missing_cost'))
                continue
                
            # Check if ingredient has dosage data
            if name not in dosage_data:
                skipped_ingredients.append(SkippedIngredient(name=name, reason='missing_dosage'))
                continue
            
            result = self.ingredient_analyzer.analyze_ingredient(
                ingredient,
                inferred_costs,
                dosage_data,
                ingredient_filter
            )
            
            if result is not None:
                dosage_score, value_contribution = result
                analyzed_count += 1
                total_value += value_contribution
                
                evaluated_ingredients.append(IngredientEvaluation(
                    name=name,
                    amount_mg=ingredient['amount_mg'],
                    dosage_score=dosage_score,
                    value_contribution=value_contribution,
                    cost_per_mg=inferred_costs[name].cost_per_mg
                ))
        
        # Calculate cost-effectiveness score
        # This is the ratio of the total theoretical value to actual cost
        cost_effectiveness_score = total_value / cost_per_serving if cost_per_serving > 0 else 0
        
        return ProductEvaluation(
            name=product['name'],
            cost_per_serving=cost_per_serving,
            total_value=total_value,
            cost_effectiveness_score=cost_effectiveness_score,
            ingredients=evaluated_ingredients,
            analyzed_ingredients=analyzed_count,
            total_ingredients=len(product['ingredients']),
            skipped_ingredients=skipped_ingredients
        )

    def format_evaluation_report(self, evaluation: ProductEvaluation, show_ingredients: bool = True) -> str:
        """
        Format the evaluation results into a readable report.
        
        Args:
            evaluation: ProductEvaluation results
            show_ingredients: Whether to include detailed ingredient analysis in output
            
        Returns:
            Formatted string containing the evaluation report
        """
        lines = [
            f"Product Evaluation Report: {evaluation.name}",
            "=" * 50,
            f"Cost per serving: ${evaluation.cost_per_serving:.2f}",
            f"Total theoretical value: ${evaluation.total_value:.2f}",
            f"Cost-effectiveness score: {evaluation.cost_effectiveness_score:.2f}",
            f"(Analyzed {evaluation.analyzed_ingredients} of {evaluation.total_ingredients} ingredients)",
            "",
        ]

        if show_ingredients and evaluation.ingredients:
            lines.extend([
                "Ingredient Analysis:",
                "-" * 50,
                ""
            ])
            
            # Add analyzed ingredients
            for ingredient in evaluation.ingredients:
                lines.extend([
                    f"\n{ingredient.name}:",
                    f"  Amount: {ingredient.amount_mg}mg",
                    f"  Dosage Score: {ingredient.dosage_score.score:.2f}",
                    f"  Reason: {ingredient.dosage_score.reason}",
                    f"  Cost/mg: ${ingredient.cost_per_mg:.6f}",
                    f"  Value Contribution: ${ingredient.value_contribution:.2f}",
                    ""
                ])
            
        # Add skipped ingredients if any
        if evaluation.skipped_ingredients:
            lines.extend([
                "Skipped Ingredients:",
                "-" * 50,
                ""
            ])
            
            missing_cost = [i.name for i in evaluation.skipped_ingredients if i.reason == 'missing_cost']
            missing_dosage = [i.name for i in evaluation.skipped_ingredients if i.reason == 'missing_dosage']
            
            if missing_cost:
                lines.append("Missing cost data:")
                for name in missing_cost:
                    lines.append(f"  - {name}")
                lines.append("")
                
            if missing_dosage:
                lines.append("Missing dosage data:")
                for name in missing_dosage:
                    lines.append(f"  - {name}")
                lines.append("")
        
        return "\n".join(lines)

    def export_to_csv(self, evaluation_pairs: List[tuple[Dict, ProductEvaluation]], filepath: str):
        """
        Exports the evaluation results to a CSV file.

        Args:
            evaluation_pairs (List[tuple[Dict, ProductEvaluation]]): A list of tuples,
                where each tuple contains the original product dictionary and its
                corresponding ProductEvaluation object.
            filepath (str): The path to the output CSV file.
        """
        if not evaluation_pairs:
            print("No evaluation results to export.")
            return

        # Ensure the directory exists
        output_dir = os.path.dirname(filepath)
        # Handle case where filepath is just a filename (no directory part)
        if output_dir and not os.path.exists(output_dir):
             os.makedirs(output_dir, exist_ok=True)

        # Define header based on the desired output structure
        header = [
            'Product Name',
            'Product Total Cost (£)', # Added currency symbol for clarity
            'Product Servings',
            'Product Cost Per Serving (£)', # Added currency symbol
            'Ingredient Name',
            'Amount Per Serving (mg)', # Added unit
            'Unit', # Keep 'Unit' column, populate with 'mg'
            'Single Ingredient Cost Per mg (£)', # Clarified unit and currency
            'Ingredient Cost in Product (£)', # Added currency symbol
            'Dosage Score (Efficiency Rating)', # Renamed for clarity
            'Dosage Match Reason', # Renamed for clarity
            'Overall Product Score (Value/Cost)', # Renamed for clarity
            'Skipped Ingredients' # Renamed, extracted from SkippedIngredient objects
        ]

        try:
            with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(header)

                for product_dict, evaluation in evaluation_pairs:
                    # Extract product-level details
                    product_name = evaluation.name
                    product_cost = product_dict.get('cost', 'N/A') # Get from original dict
                    product_servings = product_dict.get('servings', 'N/A') # Get from original dict
                    product_cost_per_serving = evaluation.cost_per_serving
                    overall_efficiency = evaluation.cost_effectiveness_score # Use cost_effectiveness_score
                    # Extract names of skipped ingredients
                    skipped_ingredients_str = ', '.join([si.name for si in evaluation.skipped_ingredients])

                    evaluated_ingredients_list = evaluation.ingredients

                    if not evaluated_ingredients_list:
                         # Write a row for the product even if no ingredients were evaluated
                         writer.writerow([
                            product_name,
                            product_cost,
                            product_servings,
                            f"{product_cost_per_serving:.2f}" if isinstance(product_cost_per_serving, (int, float)) else 'N/A',
                            'N/A', # Ingredient Name
                            'N/A', # Amount Per Serving
                            'N/A', # Unit
                            'N/A', # Single Ingredient Cost Per Unit
                            'N/A', # Ingredient Cost in Product
                            'N/A', # Dosage Score (Efficiency Rating)
                            'N/A', # Dosage Match Reason
                            f"{overall_efficiency:.2f}" if isinstance(overall_efficiency, (int, float)) else 'N/A',
                            skipped_ingredients_str
                        ])
                    else:
                        # Write a row for each evaluated ingredient
                        for ing_eval in evaluated_ingredients_list:
                            cost_per_mg = ing_eval.cost_per_mg
                            amount_mg = ing_eval.amount_mg
                            # Calculate cost in product, handle potential errors
                            cost_in_product = (amount_mg * cost_per_mg) if amount_mg is not None and cost_per_mg is not None else 'N/A'

                            writer.writerow([
                                product_name,
                                product_cost,
                                product_servings,
                                f"{product_cost_per_serving:.2f}" if isinstance(product_cost_per_serving, (int, float)) else 'N/A',
                                ing_eval.name,
                                amount_mg if amount_mg is not None else 'N/A',
                                'mg', # Unit is always mg based on IngredientEvaluation
                                f"{cost_per_mg:.6f}" if isinstance(cost_per_mg, (int, float)) else 'N/A', # Single Ingredient Cost Per mg
                                f"{cost_in_product:.4f}" if isinstance(cost_in_product, (int, float)) else 'N/A', # Ingredient Cost in Product
                                f"{ing_eval.dosage_score.score:.2f}" if ing_eval.dosage_score else 'N/A', # Dosage Score
                                ing_eval.dosage_score.reason if ing_eval.dosage_score else 'N/A', # Dosage Match Reason
                                f"{overall_efficiency:.2f}" if isinstance(overall_efficiency, (int, float)) else 'N/A', # Overall Product Score
                                skipped_ingredients_str # Skipped ingredients (same for all rows of a product)
                            ])
            print(f"Successfully exported results to {filepath}")

        except IOError as e:
            print(f"Error writing to CSV file {filepath}: {e}")
        except Exception as e:
            print(f"An unexpected error occurred during CSV export: {e}")


if __name__ == '__main__':
    # Test the evaluator with our example data
    evaluator = ProductEvaluator()
    products, inferred_costs, dosages = evaluator.load_data()
    
    # Evaluate the first product
    if products:
        evaluation = evaluator.evaluate_product(products[0], inferred_costs, dosages)
        print(evaluator.format_evaluation_report(evaluation))
        
        print("\n" + "=" * 50)
        print("Testing with ingredient filter:")
        # Test with ingredient filter (just caffeine)
        filtered_eval = evaluator.evaluate_product(
            products[0],
            inferred_costs,
            dosages,
            ingredient_filter=["Caffeine Anhydrous"]
        )
        print(evaluator.format_evaluation_report(filtered_eval))
