import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score
import requests
from bs4 import BeautifulSoup
import feedparser
import time
from datetime import datetime, timedelta
from dateutil import parser

# Page config MUST be first
st.set_page_config(layout="wide", page_title="StockSight", page_icon="📈")

def inject_css():
    """Inject custom CSS for the dark theme and custom UI."""
    st.markdown("""
    <style>
    /* Use deep navy background */
    .stApp {
        background-color: #0D1117;
        color: white;
    }
    
    /* Ensure elements inherit font properly */
    h1, h2, h3, h4, h5, h6, p, div, span {
        font-family: sans-serif;
    }
    
    /* Accent color for links */
    a {
        color: #58A6FF !important;
        text-decoration: none;
    }
    a:hover {
        text-decoration: underline;
    }
    
    /* Card style for metric blocks and info cards */
    .metric-card {
        background-color: #161B22;
        border: 1px solid #30363D;
        border-radius: 8px;
        padding: 15px;
        margin-bottom: 15px;
    }
    
    .news-item {
        background-color: #161B22;
        border: 1px solid #30363D;
        border-radius: 8px;
        padding: 10px 15px;
        margin-bottom: 10px;
        max-height: 500px;
        overflow-y: auto;
    }
    
    .scrollable-news {
        max-height: 600px;
        overflow-y: auto;
        padding-right: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

@st.cache_data(ttl=3600)
def fetch_stock_data(ticker, start_date, end_date):
    """Fetch daily historical closing prices for a given ticker."""
    try:
        data = yf.download(ticker, start=start_date, end=end_date)
        if data.empty:
            return None
        # Handle MultiIndex columns for single ticker in some yfinance versions
        if isinstance(data.columns, pd.MultiIndex):
            data.columns = data.columns.droplevel(1)
        return data
    except Exception as e:
        return None

@st.cache_data(ttl=3600)
def fetch_company_info(ticker):
    """Fetch company metadata using yfinance."""
    try:
        tick = yf.Ticker(ticker)
        return tick.info
    except Exception as e:
        return None

def run_linear_regression(df):
    """Run linear regression on historical stock data to predict future prices."""
    df = df.copy()
    # Handle NA values
    df = df.dropna(subset=['Close'])
    if df.empty:
        return None
        
    df['DayIndex'] = range(len(df))
    
    # 80/20 split
    train_size = int(len(df) * 0.8)
    if train_size == 0:
        return None
        
    train_df = df.iloc[:train_size]
    test_df = df.iloc[train_size:]
    
    # Fit model
    model = LinearRegression()
    model.fit(train_df[['DayIndex']], train_df['Close'])
    
    # Predict on test
    if len(test_df) > 0:
        test_predictions = model.predict(test_df[['DayIndex']])
        r2 = r2_score(test_df['Close'], test_predictions)
    else:
        r2 = 0.0
        
    # Predict 90 days into future
    future_days = 90
    last_day_index = df['DayIndex'].iloc[-1]
    future_indices = list(range(last_day_index + 1, last_day_index + 1 + future_days))
    
    # Generate future dates
    last_date = df.index[-1]
    future_dates = [last_date + timedelta(days=i) for i in range(1, future_days + 1)]
    
    # Predict all (train, test, future) for plotting
    all_indices = list(df['DayIndex']) + future_indices
    all_predictions = model.predict(pd.DataFrame({'DayIndex': all_indices}))
    
    future_pred_90 = all_predictions[-1]
    
    return {
        'model': model,
        'r2': r2,
        'future_pred_90': future_pred_90,
        'all_predictions': all_predictions,
        'future_dates': future_dates,
        'total_days_used': len(df)
    }

@st.cache_data(ttl=3600)
def fetch_yahoo_news(ticker):
    """Fetch recent news from Yahoo Finance public RSS feed."""
    url = f"https://feeds.finance.yahoo.com/rss/2.0/headline?s={ticker}&region=US&lang=en-US"
    articles = []
    try:
        feed = feedparser.parse(url)
        for entry in feed.entries[:10]:
            try:
                published = parser.parse(entry.published).replace(tzinfo=None)
            except:
                published = datetime.now()
            articles.append({
                'title': entry.title,
                'source': 'Yahoo Finance',
                'link': entry.link,
                'date': published
            })
    except:
        pass
    return articles

@st.cache_data(ttl=3600)
def fetch_google_news(ticker):
    """Fetch recent news from Google News public RSS search."""
    url = f"https://news.google.com/rss/search?q={ticker}+stock&hl=en-US&gl=US&ceid=US:en"
    articles = []
    try:
        feed = feedparser.parse(url)
        for entry in feed.entries[:10]:
            try:
                published = parser.parse(entry.published).replace(tzinfo=None)
            except:
                published = datetime.now()
            articles.append({
                'title': entry.title,
                'source': entry.source.title if hasattr(entry, 'source') else 'Google News',
                'link': entry.link,
                'date': published
            })
    except:
        pass
    return articles

@st.cache_data(ttl=3600)
def fetch_finviz_news(ticker):
    """Fetch recent news from Finviz public quote page using BeautifulSoup."""
    url = f"https://finviz.com/quote.ashx?t={ticker}"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
    articles = []
    try:
        time.sleep(1.5) # respectful delay
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        news_table = soup.find(id='news-table')
        if news_table:
            rows = news_table.findAll('tr')
            for i, row in enumerate(rows):
                if i >= 10:
                    break
                a_tag = row.find('a')
                if not a_tag: continue
                title = a_tag.text
                link = a_tag['href']
                # Approximate date for Finviz to simplify parsing since it might be today or older
                articles.append({
                    'title': title,
                    'source': 'Finviz',
                    'link': link,
                    'date': datetime.now() 
                })
    except:
        pass
    return articles

def combine_and_sort_news(*article_lists):
    """Combine news lists, deduplicate by title, and sort by date descending."""
    combined = []
    seen_titles = set()
    
    for articles in article_lists:
        for article in articles:
            if article['title'] not in seen_titles:
                combined.append(article)
                seen_titles.add(article['title'])
                
    combined.sort(key=lambda x: x['date'], reverse=True)
    return combined

def render_company_info(info):
    """Render the company information section using Streamlit components."""
    if not info:
        return
        
    st.markdown("### Section 2: Company Info")
    
    name = info.get('longName', 'N/A')
    sector = info.get('sector', 'N/A')
    industry = info.get('industry', 'N/A')
    mcap = info.get('marketCap', 'N/A')
    if isinstance(mcap, (int, float)):
        mcap = f"${mcap:,.0f}"
    
    curr_price = info.get('currentPrice', 'N/A')
    high_52 = info.get('fiftyTwoWeekHigh', 'N/A')
    low_52 = info.get('fiftyTwoWeekLow', 'N/A')
    
    st.markdown(f"""
    <div class="metric-card">
        <h4>{name}</h4>
        <p><b>Sector:</b> {sector} | <b>Industry:</b> {industry}</p>
        <p><b>Market Cap:</b> {mcap}</p>
        <p><b>Current Price:</b> ${curr_price} | <b>52-Week High:</b> ${high_52} | <b>52-Week Low:</b> ${low_52}</p>
    </div>
    """, unsafe_allow_html=True)

def render_chart_and_prediction(df, regression_results):
    """Render the Plotly interactive chart and prediction metrics."""
    st.markdown("### Section 1: Price Chart & Prediction")
    
    if not regression_results:
        st.error("Not enough data to run linear regression.")
        return
        
    fig = go.Figure()
    
    # Historical data
    fig.add_trace(go.Scatter(
        x=df.index, y=df['Close'],
        mode='lines',
        name='Historical Close',
        line=dict(color='white')
    ))
    
    # Historical Prediction Fit
    N = len(df.index)
    fig.add_trace(go.Scatter(
        x=df.index, y=regression_results['all_predictions'][:N],
        mode='lines',
        name='Historical Trend (Fit)',
        line=dict(color='#8B949E', dash='dot') # Subtle grey dashed
    ))
    
    # Future Prediction Line (Glowing/Bright)
    future_x = [df.index[-1]] + regression_results['future_dates']
    future_y = [regression_results['all_predictions'][N-1]] + list(regression_results['all_predictions'][N:])
    
    # Add a thicker, brighter neon blue line for the future
    fig.add_trace(go.Scatter(
        x=future_x, y=future_y,
        mode='lines',
        name='Future Prediction (90 Days)',
        line=dict(color='#00FFFF', width=4) # Bright cyan/neon blue
    ))
    
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white'),
        xaxis=dict(showgrid=True, gridcolor='#30363D'),
        yaxis=dict(showgrid=True, gridcolor='#30363D', title='Price (USD)'),
        margin=dict(l=0, r=0, t=30, b=0),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <h5>R² Score (Test Data)</h5>
            <h2>{regression_results['r2']:.4f}</h2>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <h5>Predicted Price (90 Days)</h5>
            <h2>${regression_results['future_pred_90']:.2f}</h2>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <h5>Total Trading Days Used</h5>
            <h2>{regression_results['total_days_used']}</h2>
        </div>
        """, unsafe_allow_html=True)

def render_news_section(news_items):
    """Render the aggregated public news feed."""
    st.markdown("### Section 3: Public News Scraper")
    st.caption("Public news aggregated from Yahoo Finance RSS, Google News RSS, and Finviz public pages. No private or paywalled data is accessed.")
    
    if not news_items:
        st.write("No news found.")
        return
        
    st.markdown('<div class="scrollable-news">', unsafe_allow_html=True)
    for item in news_items:
        date_str = item['date'].strftime('%b %d, %Y %I:%M %p')
        st.markdown(f"""
        <div class="news-item">
            <a href="{item['link']}" target="_blank" style="font-size: 1.1em; font-weight: bold;">{item['title']}</a>
            <div style="font-size: 0.9em; color: #8B949E; margin-top: 5px;">
                {item['source']} • {date_str}
            </div>
        </div>
        """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

def render_raw_data_table(df):
    """Render the raw OHLCV data table sorted by date descending."""
    st.markdown("### Section 4: Raw Data Table")
    df_sorted = df.sort_index(ascending=False)
    st.dataframe(df_sorted[['Open', 'High', 'Low', 'Close', 'Volume']], use_container_width=True)

def main():
    """Main application layout and execution flow."""
    inject_css()
    
    st.title("StockSight")
    st.write("A stock price visualizer, linear regression predictor, and public news aggregator.")
    
    with st.form("input_form"):
        col1, col2 = st.columns([1, 2])
        with col1:
            ticker = st.text_input("Enter Stock Ticker (e.g. AAPL)", value="AAPL")
        with col2:
            default_start = datetime.today() - timedelta(days=2*365)
            date_range = st.date_input("Select Date Range", value=(default_start, datetime.today()))
            
        submit = st.form_submit_button("Analyze")
        
    if submit:
        ticker = ticker.strip().upper()
        if not ticker:
            st.error("Please enter a valid ticker.")
            return
            
        if len(date_range) != 2:
            st.error("Please select a complete start and end date range.")
            return
            
        start_date, end_date = date_range
        
        with st.spinner(f"Fetching data for {ticker}..."):
            df = fetch_stock_data(ticker, start_date, end_date)
            
            if df is None or df.empty:
                st.error(f"Could not fetch data for {ticker}. The ticker may be delisted, incorrect, or there is no data for the selected dates.")
                return
                
            info = fetch_company_info(ticker)
            
            yahoo_news = fetch_yahoo_news(ticker)
            google_news = fetch_google_news(ticker)
            finviz_news = fetch_finviz_news(ticker)
            
            combined_news = combine_and_sort_news(yahoo_news, google_news, finviz_news)
            
            regression_results = run_linear_regression(df)
            
            # Render Sections
            st.markdown("---")
            if info:
                render_company_info(info)
                st.markdown("---")
            render_chart_and_prediction(df, regression_results)
            st.markdown("---")
            render_news_section(combined_news)
            st.markdown("---")
            render_raw_data_table(df)

if __name__ == "__main__":
    main()
