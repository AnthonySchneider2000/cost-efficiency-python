# Cost-Effectiveness Analyzer TODO

This TODO list tracks completed work and planned enhancements for the Cost-Effectiveness Analyzer project. It serves as a living document to guide development priorities and track progress.

## Git History
- 2025-03-27: chore: update .gitignore to include additional file patterns for build artifacts and documentation (63be8e0)
- 2025-03-27: feat: add CSV export functionality for product evaluation results (34cc72e)
- 2025-03-27: docs: update TODO list to reflect completed enhancements in output reporting (5c530ca)
- 2025-03-27: docs: update README and TODO with design decisions and project priorities (d6e84c5)
- 2025-03-27: feat: enhance product evaluation output and add output control options (2e412ff)
- 2025-03-27: feat: add new product entries for Total War supplements (69fb9b8)
- 2025-03-26: init (8ff0127)


## Immediate Priority
- [X] Enhance Output Reporting
  - [X] List ingredients skipped due to missing cost data
  - [X] List ingredients skipped due to missing dosage data
- [X] Add CSV/Excel Export
  - [X] Design export format structure
  - [X] Implement export functionality in product_evaluator.py (34cc72e)
  - [X] Add export option to main.py interface (34cc72e)

## Refinements & Improvements
- [X] Refine Dosage Scoring Logic (2025-03-27)
  - [X] Adjust scoring at min/max boundaries
  - [X] Improve clarity and context of dosage reason strings

## Code Quality & Testing
- [ ] Implement Data Validation
  - [ ] Add JSON schema validation for data files
  - [ ] Add input validation for user commands
- [ ] Expand Test Coverage
  - [ ] Add tests for edge cases in data loading
  - [ ] Add tests for export functionality
- [ ] Create Configuration System
  - [ ] Move file paths to config file
  - [ ] Add command-line argument support

## Future Enhancements
- [ ] Build Web Interface
  - [ ] Research and select web framework
  - [ ] Design UI mockups
  - [ ] Plan API structure
- [ ] Implement Price Integration
  - [ ] Research available price APIs
  - [ ] Design price update system
  - [ ] Implement automatic price fetching
- [ ] Advanced Analysis Features
  - [ ] Ingredient synergy scoring
  - [ ] Market price trend analysis
  - [ ] Supplement timing analysis

## Maintenance
- [ ] Regular Data Updates
  - [ ] Update product entries
  - [ ] Refresh single ingredient prices
  - [ ] Review and update dosage data

## Completed Work
- [X] Phase 1: Planning & Setup
  - [X] Define Data Structures
  - [X] Source Dosage Knowledge
  - [X] Outline Core Modules
  - [X] Create Checklist
- [X] Phase 2: Implementation
  - [X] Implement Data Loading (data_loader.py)
  - [X] Implement Inferred Cost Calculation (ingredient_analyzer.py)
  - [X] Implement Dosage Effectiveness (ingredient_analyzer.py)
  - [X] Implement Value Contribution & Evaluation (product_evaluator.py)
  - [X] Implement User Interface (main.py)
- [X] Phase 3: Documentation & Initial Release
  - [X] Add Docstrings & Comments
  - [X] Create README.md
  - [X] Add output control options
  - [X] Final Review
