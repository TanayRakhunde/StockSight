# StockSight

## Project Overview
StockSight is a Python web application that visualizes historical stock prices, predicts future trends using linear regression, and aggregates public news. It provides an all-in-one dashboard to research companies, view their trading data, and read recent headlines.

## How It Works
The application fetches historical daily closing prices for a given stock ticker and splits the data chronologically (80% for training, 20% for testing). It then fits a Scikit-Learn `LinearRegression` model using the day index as the independent variable. The resulting model is used to plot a trend line over the historical data and extrapolate 90 days into the future. 
**Disclaimer**: This predictive model is for educational and visualization purposes only. It is a simple linear extrapolation and does **not** constitute financial advice.

## Data Sources
All data is sourced legally from public, non-paywalled sources:
- **Yahoo Finance API (`yfinance`)**: Used for historical price data and company metadata.
- **Yahoo Finance RSS**: Public RSS feed for recent headlines.
- **Google News RSS**: Public RSS feed for stock-specific news.
- **Finviz**: Publicly accessible HTML page, scraped respectfully with standard User-Agent headers and programmatic delays.

## Tech Stack
- `streamlit` (Web Interface)
- `yfinance` (Stock Data)
- `pandas` (Data Manipulation)
- `plotly` (Interactive Charts)
- `scikit-learn` (Machine Learning / Linear Regression)
- `requests` & `beautifulsoup4` (HTML Scraping)
- `feedparser` (RSS Parsing)

## How To Run
1. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Launch the Streamlit application:
   ```bash
   streamlit run app.py
   ```

## Portfolio Note
This application was built as a portfolio project for a data science student to demonstrate data fetching, machine learning, web scraping, and UI development in Python.
