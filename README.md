# StockSight 📈

> A full-stack data science web application that provides real-time stock price visualization, machine learning-based trend prediction, and public news aggregation. 

## Project Overview

StockSight was built to demonstrate end-to-end data engineering, machine learning, and frontend development capabilities. The application seamlessly integrates financial data APIs, custom web scraping pipelines, and a predictive machine learning model into a unified, responsive user interface. 

It serves as a comprehensive dashboard for equity research, allowing users to instantly pull historical data, view predictive trends, and read the latest headlines from multiple aggregated sources.

## 🏗️ Architecture & Features

### 🖥️ Frontend (User Interface & Visualization)
- **Responsive Dashboard:** Built entirely in Python using **Streamlit**, featuring a custom-styled dark theme UI injected via CSS.
- **Interactive Data Visualization:** Leverages **Plotly Graph Objects** to render interactive, zoomable, and hover-enabled historical price charts overlaid with prediction trendlines.
- **Dynamic Metric Cards:** Real-time calculation and display of model performance metrics (R² Score) and dynamic financial indicators (Market Cap, 52-Week High/Low).
- **Asynchronous Feel:** Utilizes Streamlit's session state and caching to provide a snappy, SPA-like (Single Page Application) experience without full page reloads.

### ⚙️ Backend (Data Pipelines & Aggregation)
- **Financial Data Integration:** Integrates with the **yfinance** API to pull raw historical OHLCV (Open, High, Low, Close, Volume) data and real-time company metadata.
- **Multi-Source News Scraping:** Employs **BeautifulSoup4** and **Requests** to scrape HTML tables from public financial platforms (e.g., Finviz) while respecting server load with programmatic delays and standard User-Agents.
- **RSS Feed Parsing:** Implements **feedparser** to continuously fetch, parse, and normalize live XML RSS feeds from Google News and Yahoo Finance.
- **Data Normalization:** A custom deduplication and sorting algorithm consolidates asynchronous news feeds into a single, clean timeline.
- **Caching Layer:** Heavy network calls and data manipulations are decorated with `@st.cache_data` with Time-To-Live (TTL) expiration, drastically reducing API rate limits and improving application latency.

### 🧠 Machine Learning Pipeline
- **Data Preprocessing:** Utilizes **Pandas** for handling missing values, indexing time series data, and performing an 80/20 chronological Train/Test split.
- **Predictive Modeling:** Implements a **Scikit-Learn** `LinearRegression` model trained on historical trading days to identify macro-trends.
- **Forecasting:** Extrapolates the trained model to forecast price trends 90 days into the future, rendering the projection directly onto the frontend chart.

## 🛠️ Tech Stack

| Category | Technologies |
|----------|--------------|
| **Frontend** | Streamlit, Plotly, HTML/CSS |
| **Backend** | Python, Pandas, BeautifulSoup4, Requests, feedparser, yfinance |
| **Machine Learning** | Scikit-Learn |
| **Version Control** | Git, GitHub |

## 🚀 Installation & Usage

1. **Clone the repository:**
   ```bash
   git clone https://github.com/TanayRakhunde/StockSight.git
   cd StockSight
   ```

2. **Install dependencies:**
   Ensure you have Python 3.8+ installed, then run:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application:**
   ```bash
   streamlit run app.py
   ```
   *The application will automatically open in your default web browser.*

## ⚠️ Disclaimer
**This application was built for educational and portfolio purposes only.** The linear regression model provides a simplified mathematical extrapolation of historical trends and does **not** constitute financial advice. All scraped data is sourced from fully public, non-paywalled endpoints using respectful scraping practices.
