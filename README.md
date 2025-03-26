# Cost-Effectiveness Analyzer

A Python program for evaluating the cost-effectiveness of multi-ingredient consumer products, with a focus on nutritional supplements like pre-workout formulas. The analyzer goes beyond simple cost-per-serving metrics by considering both ingredient dosages and their market values.

## Key Features

- **Ingredient Dosage Analysis**: Evaluates ingredient effectiveness based on scientifically recognized dosage ranges
- **Value Inference**: Calculates ingredient costs using market data from single-ingredient products
- **Flexible Analysis**: Analyze entire products or focus on specific ingredients of interest
- **Standardized Units**: Automatically handles unit conversions (mg, g, kg, mcg)
- **Clear Reporting**: Detailed analysis reports showing cost-effectiveness scores and value contributions

## How It Works

1. **Data Loading**: The system loads product data, single-ingredient market prices, and dosage information from JSON files.

2. **Value Calculation**:
   - Infers raw ingredient costs using weighted averages from single-ingredient products
   - Calculates dosage effectiveness scores (0-1) based on min/optimal/max ranges
   - Combines costs and effectiveness to determine value contributions

3. **Cost-Effectiveness Score**:
   - Sums the value contributions of ingredients
   - Divides by the actual cost per serving
   - Higher scores indicate better value for money

## Installation

1. Clone this repository:
   ```bash
   git clone <repository-url>
   cd cost-efficiency-python
   ```

2. No additional dependencies required - uses Python standard library only.

## Usage

1. Prepare your data files in the `data` directory:
   - `products.json`: Multi-ingredient products to analyze
   - `singles.json`: Single-ingredient products for cost inference
   - `dosages.json`: Effective dosage ranges for ingredients

2. Run the analyzer:
   ```bash
   python main.py
   ```

3. Follow the interactive prompts to:
   - Select a product to analyze
   - Optionally filter specific ingredients
   - View the detailed cost-effectiveness report

## Data File Formats

### products.json
```json
[
  {
    "name": "Example Pre-Workout",
    "cost": 39.99,
    "servings": 30,
    "ingredients": [
      {"name": "Caffeine Anhydrous", "amount": 200, "unit": "mg"},
      {"name": "Beta-Alanine", "amount": 3.2, "unit": "g"}
    ]
  }
]
```

### singles.json
```json
[
  {
    "ingredient_name": "Caffeine Anhydrous",
    "product_name": "Brand X Caffeine 200mg 100 Tabs",
    "cost": 9.99,
    "total_quantity": 20,
    "unit": "g"
  }
]
```

### dosages.json
```json
{
  "Caffeine Anhydrous": {
    "min": 100,
    "optimal": 200,
    "max": 400,
    "unit": "mg"
  }
}
```

## Example Output

```
Product Evaluation Report: Example Pre-Workout
==================================================
Cost per serving: $1.33
Total theoretical value: $0.23
Cost-effectiveness score: 0.17
(Analyzed 2 of 3 ingredients)

Ingredient Analysis:
--------------------------------------------------
Caffeine Anhydrous:
  Amount: 200mg
  Dosage Score: 1.00
  Reason: Between minimum and optimal dose
  Cost/mg: $0.000500
  Value Contribution: $0.10
```

## Architecture

The system consists of three main modules:

1. `data_loader.py`: Handles JSON file loading and unit standardization
2. `ingredient_analyzer.py`: Calculates inferred costs and dosage effectiveness scores
3. `product_evaluator.py`: Combines analyses to generate final evaluations
4. `main.py`: Provides the command-line interface

## Limitations

- Relies on available single-ingredient product data for cost inference
- Assumes linear relationships in dosage effectiveness between min/optimal/max points
- Does not account for ingredient synergies or timing of consumption

## Future Improvements

- Support for supplement timing/scheduling analysis
- Integration with online price APIs
- Ingredient synergy scoring
- Web interface for easier data input
- Export results to CSV/Excel
- Market price trend analysis

## Contributing

Contributions are welcome! Please feel free to submit issues and pull requests.

## License

This project is open source and available under the MIT License.
