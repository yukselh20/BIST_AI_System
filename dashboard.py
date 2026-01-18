import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
import torch
import sys
import os
from datetime import datetime

# Resolve paths
sys.path.append(os.getcwd())

from core.feature_engine import fetch_and_process_data
from models.lstm_price.definitions import BISTLSTM

# --- Configuration & Custom CSS ---
st.set_page_config(layout="wide", page_title="BIST AI Terminal", page_icon="📈")

# PREMIUM UI CSS INJECTION
st.markdown("""
<style>
    /* Main Background & Font */
    .stApp {
        background-color: #0E1117;
        font-family: 'Roboto', sans-serif;
    }
    
    /* Metrics Cards (Glassmorphism) */
    div[data-testid="stMetric"] {
        background-color: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        backdrop-filter: blur(10px);
        transition: transform 0.2s;
    }
    div[data-testid="stMetric"]:hover {
        transform: scale(1.02);
        border-color: rgba(255, 255, 255, 0.3);
    }
    
    /* Headers */
    h1, h2, h3 {
        color: #E0E0E0 !important;
        font-weight: 600 !important;
    }
    
    /* Sidebar */
    section[data-testid="stSidebar"] {
        background-color: #12141C;
        border-right: 1px solid #262730;
    }
    
    /* Custom News Card */
    .news-card {
        background-color: #1E1E1E;
        padding: 15px;
        border-radius: 8px;
        margin-bottom: 15px;
        border-left: 5px solid #555;
    }
    .positive-news { border-left-color: #00FF00 !important; }
    .negative-news { border-left-color: #FF0000 !important; }
    .neutral-news { border-left-color: #888888 !important; }
    
    .news-title {
        font-size: 16px;
        font-weight: bold;
        color: #FFFFFF;
        margin-bottom: 5px;
    }
    .news-meta {
        font-size: 12px;
        color: #AAAAAA;
        margin-bottom: 10px;
    }
    .news-summary {
        font-size: 14px;
        color: #DDDDDD;
        font-style: italic;
    }
    
    /* Remove Top Padding */
    .block-container {
        padding-top: 1rem;
    }
</style>
""", unsafe_allow_html=True)

MODEL_PATH = "models/checkpoints/lstm_model.pth"
SEQUENCE_LENGTH = 60

# --- Helper Functions ---
@st.cache_resource
def load_model():
    """Loads the trained LSTM model."""
    if not os.path.exists(MODEL_PATH):
        return None
    
    device = torch.device('cpu') # Use CPU for inference on dashboard for stability
    try:
        checkpoint = torch.load(MODEL_PATH, map_location=device)
        input_size = checkpoint.get('input_size', 15)
        model = BISTLSTM(input_size=input_size).to(device)
        model.load_state_dict(checkpoint['model_state_dict'])
        model.eval()
        return model
    except Exception as e:
        st.error(f"Model yüklenirken hata: {e}")
        return None

def run_inference(model, df):
    """Runs model inference on the latest data."""
    if len(df) < SEQUENCE_LENGTH:
        return 0.5 # Neutral if not enough data
    
    # Prepare input (Last 60 bars)
    last_window = df.tail(SEQUENCE_LENGTH)
    input_np = last_window.values.astype(np.float32)
    
    input_tensor = torch.tensor(input_np).unsqueeze(0) # (1, 60, Features)
    
    with torch.no_grad():
        prob = model(input_tensor).item()
        
    return prob

def get_data(symbol):
    """Fetches and processes data from database."""
    # We need enough data for indicators (200 for EMA) + plotting
    df = fetch_and_process_data(symbol, timeframe='1min', limit=2000)
    return df

# --- UI Layout ---

# Sidebar
st.sidebar.title("🛠️ Kontrol Paneli")

# View Mode Selector
view_mode = st.sidebar.radio("Mod Seçimi", ["Genel Bakış", "Yatırım Komitesi (AI)"])
st.sidebar.markdown("---")

# Full Portfolio List matching run_bot.py
# Full Portfolio List from centralized config
from core.config_symbols import ALL_SYMBOLS as AVAILABLE_SYMBOLS

# Session State Initialization: Active Symbol
if 'active_symbol' not in st.session_state:
    st.session_state.active_symbol = AVAILABLE_SYMBOLS[0]

# Callback to update state from Selectbox
def on_symbol_change():
    st.session_state.active_symbol = st.session_state.sb_symbol_select

# Callback to update state from Buttons
def set_active_symbol(sym):
    st.session_state.active_symbol = sym
    st.session_state.sb_symbol_select = sym

# Find current index for selectbox
try:
    current_index = AVAILABLE_SYMBOLS.index(st.session_state.active_symbol)
except:
    current_index = 0
    st.session_state.active_symbol = AVAILABLE_SYMBOLS[0]
    st.session_state.sb_symbol_select = AVAILABLE_SYMBOLS[0]

# Selectbox with on_change
symbol_select = st.sidebar.selectbox(
    "Hisse Seçin", 
    AVAILABLE_SYMBOLS, 
    # index=current_index,  <-- REMOVED to avoid warning
    key='sb_symbol_select',
    on_change=on_symbol_change
)

st.sidebar.markdown("---")
st.sidebar.subheader("Sistem Durumu")
st.sidebar.success("🟢 Sistem Çevrimiçi")
st.sidebar.write(f"Güncelleme: `{datetime.now().strftime('%H:%M:%S')}`")

if st.sidebar.button("⚠️ Önbelleği Temizle"):
    st.cache_resource.clear()
    st.rerun()

if st.sidebar.button("🔄 Manuel Yenile"):
    st.rerun()

# --- SIDEBAR MARKET SCANNER ---
st.sidebar.markdown("---")
st.sidebar.subheader("📡 Canlı Piyasa Gözcüsü")
st.sidebar.caption("Yapay Zeka (LSTM) tarafından hesaplanan anlık yükseliş ihtimalleri:")

# Create a container for the scanner
scanner_container = st.sidebar.container()

# Helper to scan market
@st.cache_data(ttl=60) # Cache for 60 seconds to avoid heavy load
def scan_whole_market():
    results = []
    scan_model = load_model()
    if not scan_model: return []

    for sym in AVAILABLE_SYMBOLS:
        try:
            # Fetch sufficient data for indicators (EMA200) + Sequence (60)
            # Increased limit to 2000 to ensure we cover enough history even with gaps
            d = fetch_and_process_data(sym, timeframe='1min', limit=2000) 
            if not d.empty and len(d) >= SEQUENCE_LENGTH:
                prob = run_inference(scan_model, d)
                results.append({'symbol': sym, 'prob': prob})
        except Exception as e:
            print(f"Scanner Error for {sym}: {e}")
            pass
    
    # Sort by Probability Descending
    return sorted(results, key=lambda x: x['prob'], reverse=True)

# Run Scan
with st.sidebar:
    with st.spinner("Piyasa taranıyor..."):
        market_snapshot = scan_whole_market()

if market_snapshot:
    for item in market_snapshot:
        sym = item['symbol']
        prob_pct = item['prob'] * 100
        
        # Color coding
        icon = "🔻"
        btn_type = "secondary"
        if prob_pct > 60: 
            icon = "🚀"
            btn_type = "primary" # Use primary color for high potential
        elif prob_pct > 50:
            icon = "➖"
            btn_type = "secondary"
            
        # Interactive Button with Callback
        btn_label = f"{sym} | {prob_pct:.1f}% {icon}"
        st.sidebar.button(
            btn_label, 
            key=f"btn_{sym}", 
            use_container_width=True, 
            type=btn_type,
            on_click=set_active_symbol,
            args=(sym,)
        )
            
else:
    st.sidebar.warning("Veri bekleniyor...")


# Main Header
col_header_1, col_header_2 = st.columns([3, 1])
with col_header_1:
    st.title(f"📊 {symbol_select} - AI Terminal")
with col_header_2:
    st.markdown(" ") # Spacer

# --- TAB 1: OVERVIEW ---
if view_mode == "Genel Bakış":
    # Main Logic
    model = load_model()
    with st.spinner('Veriler Güncelleniyor...'):
        df = get_data(symbol_select)

    if df.empty:
        st.warning(f"⚠️ Veritabanında {symbol_select} verisi bulunamadı. Lütfen veri toplayıcısını kontrol edin.")
    elif len(df) < 200:
        st.warning(f"⚠️ Yetersiz veri ({len(df)}/200). İndikatörler için daha fazla veri gerekiyor.")
    else:
        # 1. Metrics Section
        last_price = df['close'].iloc[-1]
        prev_price = df['close'].iloc[-2]
        change = last_price - prev_price
        change_pct = (change / prev_price) * 100
        
        prediction_prob = 0.5
        if model:
            prediction_prob = run_inference(model, df)
        
        # Decision Logic
        threshold = 0.52
        decision = "BEKLE"
        delta_color = "off"
        
        if prediction_prob > threshold:
            decision = "AL (BUY)"
            delta_color = "normal" # Green in streamline
        elif prediction_prob < (1.0 - threshold):
            decision = "SAT (SELL)"
            delta_color = "inverse" # Red in streamline

        # GLASSMORPHISM CARDS ROW
        m1, m2, m3 = st.columns(3)
        
        with m1:
            st.metric("Son Fiyat", f"{last_price:.2f} TL", f"{change_pct:.2f}%", delta_color="normal")
            
        with m2:
            st.metric("AI Sinyali", decision, f"Güven: {abs(prediction_prob - 0.5) * 200:.1f}%", delta_color=delta_color)

        with m3:
            # Custom Gauge using Plotly (Compact)
            fig_gauge = go.Figure(go.Indicator(
                mode = "gauge+number",
                value = prediction_prob * 100,
                title = {'text': "Yükseliş İhtimali", 'font': {'size': 14}},
                gauge = {
                    'axis': {'range': [0, 100]},
                    'bar': {'color': "#00CC96" if prediction_prob > 0.5 else "#EF553B"},
                    'bgcolor': "rgba(0,0,0,0)",
                    'borderwidth': 0,
                    'bordercolor': "gray",
                    'steps' : [
                        {'range': [0, 40], 'color': "rgba(239, 85, 59, 0.3)"},
                        {'range': [40, 60], 'color': "rgba(128, 128, 128, 0.3)"},
                        {'range': [60, 100], 'color': "rgba(0, 204, 150, 0.3)"}
                    ],
                    'threshold' : {'line': {'color': "white", 'width': 2}, 'thickness': 0.75, 'value': prediction_prob*100}
                }
            ))
            fig_gauge.update_layout(height=140, margin=dict(l=10,r=10,t=30,b=10), paper_bgcolor='rgba(0,0,0,0)', font={'color': "white"})
            st.plotly_chart(fig_gauge, use_container_width=True)
            
        st.markdown("---")

        # 2. Charts Section (Neon Style)
        st.subheader("📈 Teknik Görünüm")
        
        # Filter last 150 bars
        plot_data = df.tail(150)
        
        fig = make_subplots(rows=2, cols=1, shared_xaxes=True, 
                            vertical_spacing=0.03, row_heights=[0.7, 0.3])

        # Candlestick
        fig.add_trace(go.Candlestick(
            x=plot_data.index,
            open=plot_data['open'], high=plot_data['high'],
            low=plot_data['low'], close=plot_data['close'],
            name='Fiyat',
            increasing_line_color='#00CC96', decreasing_line_color='#EF553B'
        ), row=1, col=1)

        # Overlays (Neon Lines)
        if 'SMA_50' in plot_data.columns:
            fig.add_trace(go.Scatter(x=plot_data.index, y=plot_data['SMA_50'], line=dict(color='#FFA15A', width=1.5), name='SMA 50'), row=1, col=1)
        if 'EMA_200' in plot_data.columns:
            fig.add_trace(go.Scatter(x=plot_data.index, y=plot_data['EMA_200'], line=dict(color='#19D3F3', width=1.5), name='EMA 200'), row=1, col=1)
            
        # Bollinger Bands (Subtle)
        if 'BBU_20_2.0' in plot_data.columns and 'BBL_20_2.0' in plot_data.columns:
            fig.add_trace(go.Scatter(x=plot_data.index, y=plot_data['BBU_20_2.0'], line=dict(color='rgba(255,255,255,0.1)', width=0), showlegend=False), row=1, col=1)
            fig.add_trace(go.Scatter(x=plot_data.index, y=plot_data['BBL_20_2.0'], line=dict(color='rgba(255,255,255,0.1)', width=0), fill='tonexty', fillcolor='rgba(255,255,255,0.05)', name='Bollinger'), row=1, col=1)

        # RSI (Purple Neon)
        if 'RSI_14' in plot_data.columns:
            fig.add_trace(go.Scatter(x=plot_data.index, y=plot_data['RSI_14'], line=dict(color='#AB63FA', width=2), name='RSI 14'), row=2, col=1)
            # RSI Zones
            fig.add_hline(y=70, line_dash="dot", line_color="#FF6692", row=2, col=1)
            fig.add_hline(y=30, line_dash="dot", line_color="#00CC96", row=2, col=1)

        fig.update_layout(
            height=600, 
            xaxis_rangeslider_visible=False, 
            template="plotly_dark",
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            margin=dict(l=0,r=0,t=0,b=0),
            legend=dict(orientation="h", y=1, x=0, bgcolor='rgba(0,0,0,0.5)')
        )
        st.plotly_chart(fig, use_container_width=True)

        # 3. Premium News Section
        st.markdown("---")
        st.subheader("📰 AI Haber Analizi")
        
        with st.spinner(f"{symbol_select} Haberleri Taranıyor..."):
            try:
                from core.news_agent import NewsAgent
                
                @st.cache_resource
                def get_news_agent():
                    return NewsAgent()

                agent = get_news_agent()
                news_items = agent.fetch_news(symbol_select, limit=6) # 6 items for grid
                
                if news_items:
                    # Create Grid (2 Columns)
                    news_cols = st.columns(2)
                    
                    for i, item in enumerate(news_items):
                        sentiment_score = agent.analyze_sentiment(item['title'])
                        
                        # Sentiment Styling
                        s_label = "NÖTR"
                        css_class = "neutral-news"
                        
                        if sentiment_score > 0.2: 
                            s_label = f"POZİTİF (+{sentiment_score:.2f})"
                            css_class = "positive-news"
                        elif sentiment_score < -0.2: 
                            s_label = f"NEGATİF ({sentiment_score:.2f})"
                            css_class = "negative-news"
                        
                        summary = item.get('summary', '')
                        if not summary: summary = "Özet hazırlanamadı."
                        
                        # Card HTML
                        card_html = f"""
                        <div class="news-card {css_class}">
                            <div class="news-title"><a href="{item['link']}" target="_blank" style="text-decoration:none; color:white;">{item['title']}</a></div>
                            <div class="news-meta">📅 {item['published']} | {s_label}</div>
                            <div class="news-summary">{summary[:180]}...</div>
                        </div>
                        """
                        
                        # Place in grid (Alternating columns)
                        with news_cols[i % 2]:
                            st.markdown(card_html, unsafe_allow_html=True)
                            
                else:
                    st.info("Bu hisseyle ilgili güncel haber bulunamadı.")
                    
            except Exception as e:
                st.error(f"Haber modülü hatası: {e}")

        # 4. Data Table (Collapsible)
        with st.expander("🔍 Tüm Verileri Görüntüle"):
            st.dataframe(df.tail(20).sort_index(ascending=False), use_container_width=True)

# --- TAB 2: COMMITTEE VIEW ---
elif view_mode == "Yatırım Komitesi (AI)":
    st.title(f"🏛️ Yatırım Komitesi: {symbol_select}")
    st.caption("Ajan Tabanlı Karar Destek Sistemi (Multi-Agent System powered by LangGraph)")
    
    col_k1, col_k2 = st.columns([1, 2])
    
    with col_k1:
        st.info("Yatırım Komitesi, farklı uzmanlıklara sahip AI ajanlarını bir araya getirerek ortak bir karar verir.")
        if st.button("🔔 Komiteyi Topla", type="primary", use_container_width=True):
            with st.spinner("Ajanlar toplanıyor... Veriler analiz ediliyor..."):
                # Run Simulation
                try:
                    from run_committee import run_committee_simulation
                    result = run_committee_simulation(symbol_select)
                    st.session_state.committee_result = result
                except Exception as e:
                    st.error(f"Komite hatası: {e}")
                    
    with col_k2:
        if 'committee_result' in st.session_state:
            from agents.ui_components import render_committee_decision
            render_committee_decision(st.session_state.committee_result)
        else:
            st.markdown("""
            <div style="text-align: center; padding: 50px; opacity: 0.5;">
                <h1>🧠</h1>
                <p>Henüz bir toplantı yapılmadı.</p>
                <p>Sol taraftaki butona basarak ajanları çağırabilirsiniz.</p>
            </div>
            """, unsafe_allow_html=True)
