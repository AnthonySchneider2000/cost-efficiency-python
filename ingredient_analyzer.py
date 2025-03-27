"""
Module for analyzing ingredient costs and effectiveness in the cost-effectiveness analyzer.
"""
from typing import Dict, List, Optional
from dataclasses import dataclass
from collections import defaultdict

@dataclass
class IngredientCost:
    """Container for ingredient cost analysis results."""
    name: str
    cost_per_mg: float
    sample_size: int  # Number of single-ingredient products used in calculation

@dataclass
class DosageScore:
    """Container for dosage effectiveness analysis results."""
    name: str
    score: float  # 0-1 score
    amount_mg: float
    min_mg: float
    optimal_mg: float
    max_mg: float
    reason: str  # Explanation of the score

class IngredientAnalyzer:
    """Analyzes ingredient costs and dosage effectiveness."""

    def calculate_inferred_costs(self, singles_data: List[Dict]) -> Dict[str, IngredientCost]:
        """
        Calculate the inferred cost per mg for each ingredient based on single-ingredient products.
        Uses a weighted average based on product quantities.
        
        Args:
            singles_data: List of standardized single-ingredient product data
            
        Returns:
            Dictionary mapping ingredient names to their IngredientCost
        """
        # Group products by ingredient
        ingredient_groups = defaultdict(list)
        for product in singles_data:
            ingredient_groups[product['ingredient_name']].append(product)
        
        # Calculate weighted average cost for each ingredient
        inferred_costs = {}
        for ingredient_name, products in ingredient_groups.items():
            total_weighted_cost = 0
            total_quantity = 0
            
            for product in products:
                quantity_mg = product['total_quantity_mg']
                cost_per_mg = product['cost'] / quantity_mg
                total_weighted_cost += cost_per_mg * quantity_mg
                total_quantity += quantity_mg
            
            average_cost_per_mg = total_weighted_cost / total_quantity if total_quantity > 0 else 0
            
            inferred_costs[ingredient_name] = IngredientCost(
                name=ingredient_name,
                cost_per_mg=average_cost_per_mg,
                sample_size=len(products)
            )
        
        return inferred_costs

    def calculate_dosage_score(
        self,
        amount_mg: float,
        dosage_info: Dict,
        ingredient_name: str
    ) -> DosageScore:
        """
        Calculate a 0-1 score for ingredient dosage effectiveness.
        
        Scoring logic:
        - 0 for amounts below minimum effective dose
        - Linear increase from min to optimal
        - 1.0 at optimal dose
        - Linear decrease from optimal to max (if amount > optimal)
        - 0 for amounts above maximum safe dose
        
        Args:
            amount_mg: Amount of ingredient in milligrams
            dosage_info: Dictionary containing min, optimal, and max values in mg
            ingredient_name: Name of the ingredient
            
        Returns:
            DosageScore containing the score and explanation
        """
        min_mg = dosage_info['min_mg']
        optimal_mg = dosage_info['optimal_mg']
        max_mg = dosage_info['max_mg']
        
        # Define a small positive score for boundary conditions
        boundary_score = 0.25

        if amount_mg < min_mg:
            score = 0.0
            reason = f"Below minimum effective dose ({min_mg}mg)"
        elif amount_mg == min_mg:
            score = boundary_score
            reason = f"At minimum effective dose ({min_mg}mg)"
        elif amount_mg > max_mg:
            score = 0.0
            reason = f"Exceeds maximum safe dose ({max_mg}mg)"
        elif amount_mg == max_mg:
            score = boundary_score
            reason = f"At maximum safe dose ({max_mg}mg)"
        elif amount_mg == optimal_mg:
            score = 1.0
            reason = f"At optimal dose ({optimal_mg}mg)"
        elif amount_mg < optimal_mg: # Between min (exclusive) and optimal (exclusive)
            # Linear increase from boundary_score at min_mg to 1.0 at optimal_mg
            score = boundary_score + (1.0 - boundary_score) * (amount_mg - min_mg) / (optimal_mg - min_mg)
            reason = f"Between minimum ({min_mg}mg) and optimal ({optimal_mg}mg)"
        else: # Between optimal (exclusive) and max (exclusive)
            # Linear decrease from 1.0 at optimal_mg to boundary_score at max_mg
            score = 1.0 - (1.0 - boundary_score) * (amount_mg - optimal_mg) / (max_mg - optimal_mg)
            reason = f"Between optimal ({optimal_mg}mg) and maximum ({max_mg}mg)"
        
        return DosageScore(
            name=ingredient_name,
            score=score,
            amount_mg=amount_mg,
            min_mg=min_mg,
            optimal_mg=optimal_mg,
            max_mg=max_mg,
            reason=reason
        )

    def analyze_ingredient(
        self,
        ingredient: Dict,
        inferred_costs: Dict[str, IngredientCost],
        dosage_info: Dict,
        ingredient_filter: Optional[List[str]] = None
    ) -> Optional[tuple[DosageScore, float]]:
        """
        Analyze a single ingredient's effectiveness and value contribution.
        
        Args:
            ingredient: Ingredient data containing name and amount
            inferred_costs: Dictionary of inferred costs per ingredient
            dosage_info: Dictionary of dosage information per ingredient
            ingredient_filter: Optional list of ingredient names to analyze
            
        Returns:
            Tuple of (DosageScore, value_contribution) if ingredient should be analyzed,
            None if ingredient should be skipped (not in filter)
        """
        name = ingredient['name']
        
        # Skip if not in filter (if filter is provided)
        if ingredient_filter and name not in ingredient_filter:
            return None
            
        # Skip if missing cost or dosage data
        if name not in inferred_costs or name not in dosage_info:
            return None
        
        # Calculate dosage score
        dosage_score = self.calculate_dosage_score(
            ingredient['amount_mg'],
            dosage_info[name],
            name
        )
        
        # Calculate value contribution
        cost_info = inferred_costs[name]
        value_contribution = ingredient['amount_mg'] * cost_info.cost_per_mg * dosage_score.score
        
        return dosage_score, value_contribution


if __name__ == '__main__':
    # Test the analyzer with our example data
    from data_loader import DataLoader
    
    loader = DataLoader()
    products, singles, dosages = loader.load_all_data()
    
    analyzer = IngredientAnalyzer()
    
    # Calculate inferred costs
    inferred_costs = analyzer.calculate_inferred_costs(singles)
    
    print("\nInferred Costs:")
    for name, cost_info in inferred_costs.items():
        print(f"{name}: ${cost_info.cost_per_mg:.6f}/mg (from {cost_info.sample_size} products)")
    
    # Test dosage scoring for each ingredient in the first product
    print("\nDosage Scores for Example Product:")
    for ingredient in products[0]['ingredients']:
        if ingredient['name'] in dosages:
            score = analyzer.calculate_dosage_score(
                ingredient['amount_mg'],
                dosages[ingredient['name']],
                ingredient['name']
            )
            print(f"\n{score.name}:")
            print(f"Amount: {score.amount_mg}mg")
            print(f"Score: {score.score:.2f}")
            print(f"Reason: {score.reason}")
