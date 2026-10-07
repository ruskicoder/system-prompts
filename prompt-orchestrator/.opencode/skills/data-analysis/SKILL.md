---
name: data-analysis
description: Analyze, transform, clean, and visualize structured datasets using Python
  REPL, pandas, numpy, and plotting libraries. Trigger with "analyze data", "process
  CSV", "EDA", "generate plots", "statistical summary", or when computing numerical
  results.
argument-hint: <dataset path or analysis goal>
---

<!-- Generated from skills/data-analysis.md by tools/generate_integrations.py. Edit the source file, not this one. -->

# Skill: Data Analysis & Processing

## Purpose
Analyze, transform, and visualize data using computational tools.

## Tools Required
- Python REPL / code execution
- Data processing libraries (numpy, pandas, scipy)
- Visualization libraries (matplotlib, plotly, seaborn)
- File I/O for various formats (CSV, JSON, Excel, Parquet)

## General Principles
- Use step-by-step computation: never rely on memorized results
- For arithmetic: calculate digit by digit before answering
- Verify results independently when possible
- Prefer Python REPL over mental calculation for anything non-trivial

## Computation Environment
When using Python for analysis:
- Available libraries: numpy, scipy, pandas, seaborn, plotly, sympy, mpmath, statsmodels
- Plotting: use plotly for interactive, matplotlib/seaborn for static
- REPL is stateful: variables persist between calls
- Timeout limits apply (typically 45-60s): break long computations into chunks

## Data Loading

### File Formats
| Format | Preferred Library | Notes |
|--------|-----------------|-------|
| CSV | pandas `read_csv` | Handle encoding, delimiter detection |
| JSON | `json` / pandas `read_json` | Nested structures need normalization |
| Excel | `openpyxl` / pandas `read_excel` | Multiple sheets, cell formatting |
| Parquet | pandas `read_parquet` | Columnar, efficient for large data |
| SQL | pandas `read_sql` | Database connection required |

### Data Cleaning
1. Check for nulls/missing values
2. Validate data types
3. Handle outliers (flag, don't silently remove)
4. Normalize formats (dates, strings, numbers)
5. Deduplicate if appropriate

## Analysis Patterns

### Exploratory Data Analysis (EDA)
- Shape, dtypes, head/tail
- Summary statistics (describe)
- Distribution plots for numeric columns
- Value counts for categorical columns
- Correlation matrix for relationships
- Missing value heatmap

### Statistical Analysis
- Descriptive statistics: mean, median, std, quartiles
- Hypothesis testing: t-test, chi-square, ANOVA
- Regression: linear, logistic
- Time series: trends, seasonality, decomposition

### Data Transformation
- Filter rows, select columns
- Group by + aggregate
- Pivot / melt
- Join / merge datasets
- Apply custom functions

## Visualization
- Line plots: time series, trends
- Bar plots: categorical comparisons
- Scatter plots: relationships between variables
- Histograms: distributions
- Heatmaps: correlation, matrices
- Box plots: distribution comparison

## Results Communication
- Present key findings prominently
- Support with visualizations when helpful
- Include uncertainty/confidence where relevant
- Don't over-interpret: let the data speak
- Flag data quality issues that affect conclusions

## Reproducibility
- Log transformation steps
- Document assumptions
- Note any data filtering/exclusion decisions
- Random seeds for reproducible sampling
- Version data processing scripts
