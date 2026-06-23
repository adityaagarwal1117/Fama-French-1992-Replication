# Empirical Replication of the Fama-French (1992) Asset Pricing Model

**Author:** Aditya Agarwal  

## 📌 Project Overview
This repository contains a Python-based empirical replication of the foundational Fama-French (1992) paper, *"The Cross-Section of Expected Stock Returns."* Prior to 1992, the Capital Asset Pricing Model (CAPM) theorized that a stock's market beta was the primary driver of expected returns. Fama and French challenged this by proving that two distinct firm characteristics—**Size (Market Capitalization)** and **Value (Book-to-Market Ratio)**—provided a much stronger explanation for cross-sectional stock returns. 

This project builds a quantitative data pipeline to clean historical financial data, construct portfolios, and run Fama-MacBeth cross-sectional regressions to test if these anomalies persist in a modern dataset.

## 🛠️ Methodology & Technical Architecture
The pipeline is built using Python (`pandas`, `numpy`, `statsmodels`) and processes data from two major financial databases:
1. **CRSP:** For historical monthly stock prices, returns, and shares outstanding.
2. **Compustat:** For historical corporate accounting data (Book Equity).

### Key Features of the Pipeline:
* **Data Merging:** Bridged CRSP and Compustat datasets using ticker symbols.
* **Look-Ahead Bias Prevention:** Implemented the strict Fama-French "July-to-June" alignment rule. The model forces a minimum 6-month lag between the end of the fiscal year (December) and portfolio formation (July) to ensure all accounting data was publicly available before trading.
* **Portfolio Sorting:** Utilized dynamic quantile sorting to group stocks into 100 portfolios based on Size and Book-to-Market deciles.
* **Fama-MacBeth Regressions:** Executed month-by-month Ordinary Least Squares (OLS) cross-sectional regressions to calculate the risk premiums for the Size and Value factors.

## 📊 Results & Analysis
The cross-sectional regression output yielded the following coefficients and t-statistics:
* **Size (log_ME):** Coefficient: -0.0008 | t-stat: -1.48
* **Value (log_BM):** Coefficient: 0.0002 | t-stat: 0.23

**Conclusion on Factor Decay:**
Directionally, the model successfully replicated the original theory (a negative coefficient for Size and a positive coefficient for Value). However, the t-statistics fell below the 1.96 threshold for 95% confidence. 

This lack of statistical significance empirically demonstrates **Factor Decay**. In modern, highly efficient markets dominated by algorithmic trading and mega-cap tech growth stocks, the historical premiums for small-cap and value stocks have been heavily diluted. This project highlights that while the Fama-French framework remains the cornerstone of risk management, historical anomalies are often arbitraged away over time.

## 🚀 How to Run the Code
*Note: Due to strict licensing and data privacy agreements, the raw CRSP and Compustat `.csv` datasets cannot be shared publicly in this repository.*

To execute this script locally:
1. Ensure you have Python installed along with `pandas`, `numpy`, and `statsmodels`.
2. Download your own CRSP and Compustat extracts.
3. Update the `crsp_file` and `comp_file` string paths at the top of the script to point to your local `.csv` files.
4. Run the script to view the Fama-MacBeth summary statistics in your terminal.