from product_evaluator import ProductEvaluator

def test_analysis():
    """Test the analysis of Gorilla Mode (2 Scoops)"""
    evaluator = ProductEvaluator()
    products, inferred_costs, dosages = evaluator.load_data()
    
    # Get Gorilla Mode (2 Scoops) - it's the third product (index 2)
    product = products[2]
    
    # Analyze without ingredient filter
    evaluation = evaluator.evaluate_product(product, inferred_costs, dosages)
    report = evaluator.format_evaluation_report(evaluation)
    
    # Write output to file
    with open('analysis_output.txt', 'w') as f:
        f.write(report)

if __name__ == '__main__':
    test_analysis()
