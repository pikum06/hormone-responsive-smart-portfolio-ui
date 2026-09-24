import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime

st.set_page_config(page_title="Hormone Terminal", layout="wide")

# Custom Terminal CSS
st.markdown("""
    <style>
    /* App background */
    .stApp { background-color: #ffffff; }
    
    /* Headers (White) */
    h1, h2, h3, .stMarkdown { color: #000000 !important; }
    
    /* Metric Boxes: Black background, White border */
    .stMetric { 
        background-color: #000000; 
        padding: 15px; 
        border-radius: 10px; 
        border: 1px solid #FFFFFF; 
    }
    
    /* Labels (White) */
    [data-testid="stMetricLabel"] { 
        color: #FFFFFF !important; 
        font-weight: bold;
    }
    
    /* Values (White and Bold) */
    [data-testid="stMetricValue"] { 
        color: #FFFFFF !important; 
        font-weight: bold !important; 
    }
    
    /* --- FIX: Delta text (e.g., 'Tracking Active') --- */
    [data-testid="stMetricDelta"] { 
        color: #FFFFFF !important; 
        font-weight: normal !important; 
    }        

    /* Alerts (Red) */
    .status-good { color: #17f502; font-weight: bold; font-size: 18px; }
    .status-warn { color: #17f502; font-weight: bold; font-size: 18px; }
    .status-danger { color: #FF0000; font-weight: bold; font-size: 18px; }
    </style>
""", unsafe_allow_html=True)

@st.cache_data(ttl=3)
def load_dashboard_data():
    try:
        backtest_df = pd.read_csv("../data/final_backtest_results.csv") 
        if not backtest_df.empty:

            # Dropping empty trailing rows that causes NaN 

            backtest_df = backtest_df.dropna(how='all')
            
            backtest_df.columns = backtest_df.columns.str.strip()
            backtest_df = backtest_df.loc[:, ~backtest_df.columns.duplicated()]
            
            if 'Date' in backtest_df.columns:
                backtest_df['Date'] = pd.to_datetime(backtest_df['Date'])
            if 'market_panic' in backtest_df.columns:
                backtest_df['market_panic'] = backtest_df['market_panic'].astype(str).str.upper() == 'TRUE'
                
            # Forcing NaN values to default numbers so math never breaks

            if 'BTC_Rolling_Vol_30d' in backtest_df.columns:
                backtest_df['BTC_Rolling_Vol_30d'] = pd.to_numeric(backtest_df['BTC_Rolling_Vol_30d'], errors='coerce').fillna(0.0)
            if 'leverage_cap' in backtest_df.columns:
                backtest_df['leverage_cap'] = pd.to_numeric(backtest_df['leverage_cap'], errors='coerce').fillna(1.0).astype(float)
        else:
            backtest_df = pd.DataFrame(columns=['Date', 'BTC_Rolling_Vol_30d', 'market_panic', 'leverage_cap'])
    except Exception:
        backtest_df = pd.DataFrame(columns=['Date', 'BTC_Rolling_Vol_30d', 'market_panic', 'leverage_cap'])

    try:
        logs_df = pd.read_csv("../data/hormone_transaction_logs.csv")
        if not logs_df.empty:

            # Drop empty rows here too just to be safe

            logs_df = logs_df.dropna(how='all') 
            logs_df.columns = logs_df.columns.str.strip()
            logs_df = logs_df.loc[:, ~logs_df.columns.duplicated()]
            if 'timestamp' in logs_df.columns:
                logs_df['timestamp'] = pd.to_datetime(logs_df['timestamp'])
    except Exception:
        logs_df = pd.DataFrame(columns=['index', 'leverage_cap', 'status', 'timestamp'])
        
    return backtest_df, logs_df

# Loading cached datasets

df_backtest, df_logs = load_dashboard_data()

# Sidebar Control Panel

st.sidebar.title("Bio-Link Control Panel")
#st.sidebar.markdown("Solana Network:`Localhost`")
st.sidebar.markdown("File Engine Sync: `Active`")
st.sidebar.divider()

panic_mode = st.sidebar.selectbox("Circuit Breaker Mode", ["Auto (Bio-Sync)", "Force Trip (PANIC = TRUE)", "Force Nominal (PANIC = FALSE)"])
base_leverage_multiplier = st.sidebar.slider("Global Max Leverage Cap (x)", 1.0, 20.0, 10.0, 1.0)

# Updating the dataframe dynamically based on the slider so the charts/tables sync up

if not df_backtest.empty and 'leverage_cap' in df_backtest.columns:
    df_backtest['executed_leverage'] = df_backtest['leverage_cap'] * base_leverage_multiplier

st.title("Hormone-Responsive Smart Portfolio")

if df_backtest.empty:
    st.warning("Waiting for data stream. Verify that final_backtest_data.csv is populated.")
else:
    # Live Data Extraction and Display Logic

    # 1. Safely extracting the last row

    latest_tick = df_backtest.iloc[-1].to_dict()
    
    raw_panic = bool(latest_tick.get('market_panic', False))
    raw_cap = float(latest_tick.get('leverage_cap', 1.0))
    current_vol = float(latest_tick.get('BTC_Rolling_Vol_30d', 0.0))
    
    # 2. Hard Overriding for Panic State based on Dropdown

    if panic_mode == "Force Trip (PANIC = TRUE)":
        display_panic = True
    elif panic_mode == "Force Nominal (PANIC = FALSE)":
        display_panic = False
    else:
        display_panic = raw_panic

    # 3. Hard Overriding for Leverage based on Panic State

    if display_panic:
        display_cap = 0.1  # Force to 0.1 if panic is true
        status_text = "CIRCUIT BREAKER TRIPPED (PANIC ACTIVE)"
        status_class = "status-danger"
        delta_action = "De-leveraging"
        cap_delta = "Restricted"
    else:
        display_cap = raw_cap  # Use raw CSV cap if calm
        status_text = "PHYSIOLOGICAL STATE: NOMINAL"
        status_class = "status-good"
        delta_action = "Stable"
        cap_delta = "Max Allowed" if display_cap == 1.0 else "Restricted"

    # 4. Math for Executed Leverage based on Slider

    # We multiply the display_cap (which is either 0.1 or 1.0) by slider value

    display_executed_lev = display_cap * base_leverage_multiplier

    # Metrics Display

    col1, col2, col3, col4 = st.columns(4)
    with col1: 
        st.metric("Market Panic", "TRUE" if display_panic else "FALSE", delta_action, delta_color="inverse")
    with col2: 
        st.metric("BTC Rolling Vol (30d)", f"{current_vol:.4f}", "Tracking Active", delta_color="off")
    with col3: 
        st.metric("Raw System Multiplier", f"{display_cap:.1f}", "System Variable", delta_color="off")
    with col4: 
        st.metric("Executed Leverage", f"{display_executed_lev:.1f}x", cap_delta)

    st.markdown(f"### Anchor Guard State: <span class='{status_class}'>{status_text}</span>", unsafe_allow_html=True)
    st.divider()

    # Dual-Axis Time Sync Chart: Volatility vs. Panic Triggers

    st.subheader("Dual-Axis Time Sync: Volatility State vs. Panic Triggers")
    
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=df_backtest['Date'], y=df_backtest['BTC_Rolling_Vol_30d'],
        name="BTC Rolling Volatility", line={'color': '#4b0082', 'width': 2}, yaxis="y1"
    ))

    fig.add_trace(go.Scatter(
        x=df_backtest['Date'], y=df_backtest['market_panic'].astype(int),
        name="Market Panic (CSV Stream)", line={'color': '#FFD700', 'width': 2, 'shape': 'hv'}, yaxis="y2"
    ))

    fig.update_layout(
        template="plotly_dark", hovermode="x unified", 
        margin={'l': 40, 'r': 40, 't': 20, 'b': 40},
        legend={'orientation': 'h', 'yanchor': 'bottom', 'y': 1.02, 'xanchor': 'right', 'x': 1},
        yaxis={'title': "Volatility Index", 'title_font': {'color': "#000000"}, 'tickfont': {'color': "#000000"}},
        yaxis2={'title': "Panic Active", 'title_font': {'color': "#000000"}, 'tickfont': {'color': "#000000"},
                'overlaying': "y", 'side': "right", 'range': [-0.1, 1.1]}
    )

    st.plotly_chart(fig, use_container_width=True)
    st.divider()

    # Displaying the last 10 rows of the backtest data and hormone transaction logs side by side
    col_left, col_right = st.columns([2, 2])
    with col_left:
        st.subheader("Final Backtest Data Stream")
        st.dataframe(df_backtest.tail(10), use_container_width=True)
    with col_right:
        st.subheader("Hormone Transaction Logs")
        if not df_logs.empty:
            
            display_cols = [c for c in ['index', 'status', 'leverage_cap', 'timestamp'] if c in df_logs.columns]
            st.dataframe(df_logs[display_cols].tail(10), use_container_width=True)
        