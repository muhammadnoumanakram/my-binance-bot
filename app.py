import streamlit as st
import re
import requests
import pandas as pd
import mplfinance as mpf
import io

# --- Binance Data Function ---
def get_binance_futures_data(symbol, interval='15m', limit=100):
    url = "https://fapi.binance.com/fapi/v1/klines"
    if not symbol.endswith('USDT'):
        symbol = symbol + 'USDT'
    
    params = {"symbol": symbol, "interval": interval, "limit": limit}
    response = requests.get(url, params=params)
    
    if response.status_code == 200:
        data = response.json()
        df = pd.DataFrame(data, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume', 'close_time', 'qav', 'num_trades', 'taker_base_vol', 'taker_quote_vol', 'ignore'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        df.set_index('timestamp', inplace=True)
        for col in ['open', 'high', 'low', 'close', 'volume']:
            df[col] = df[col].astype(float)
        return df, symbol
    else:
        return None, None

# --- Web App UI Setup ---
st.set_page_config(page_title="Nouman's Signal Bot", page_icon="📈")

# ---> BEAUTIFUL NAME HEADING <---
st.markdown("<h1 style='text-align: center; color: #f3ba2f; text-shadow: 2px 2px 4px #000000;'>Muhammad Nouman Akram ✨</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; font-size: 18px; color: #a6a6a6; font-style: italic;'>Premium Binance Chart & Signal Bot</p>", unsafe_allow_html=True)

st.divider()

st.write("Apni post neechay paste karein aur chart generate karein.")

# Text Box for Input
post_text = st.text_area("Post Text:", height=150)

# Button to trigger action
if st.button("Detect Coin, Arrow & Generate Chart"):
    if not post_text:
        st.warning("Please post paste karein!")
    else:
        post_text = post_text.upper()
        
        # Coin Name Extraction
        matches = re.findall(r'\b[A-Z]{2,6}\b', post_text)
        coin_symbol = None
        for match in matches:
            if match not in ['LONG', 'SHORT', 'USDT', 'BUY', 'SELL', 'TP', 'SL', 'ENTRY']:
                coin_symbol = match
                break
                
        if not coin_symbol:
            st.error("Coin nahi mila post mein!")
        else:
            is_long = "LONG" in post_text
            is_short = "SHORT" in post_text

            with st.spinner(f"Fetching data for {coin_symbol}..."):
                df, real_symbol = get_binance_futures_data(coin_symbol)
            
            if df is not None:
                # Chart banana
                fig, axlist = mpf.plot(
                    df, 
                    type='candle', 
                    style='charles', 
                    title=f"{real_symbol} Setup", 
                    returnfig=True,
                    figsize=(8, 5)
                )
                
                main_ax = axlist[0]
                
                # ---> ARROW KI FIX POSITION <---
                if is_long:
                    main_ax.annotate("", xy=(0.95, 0.8), xytext=(0.95, 0.2), 
                                     xycoords='axes fraction', textcoords='axes fraction',
                                     arrowprops=dict(facecolor='green', edgecolor='green', width=12, headwidth=25, headlength=25))
                    main_ax.text(0.95, 0.85, "LONG", color='green', fontsize=14, fontweight='bold', ha='center', transform=main_ax.transAxes)
                
                elif is_short:
                    main_ax.annotate("", xy=(0.95, 0.2), xytext=(0.95, 0.8), 
                                     xycoords='axes fraction', textcoords='axes fraction',
                                     arrowprops=dict(facecolor='red', edgecolor='red', width=12, headwidth=25, headlength=25))
                    main_ax.text(0.95, 0.15, "SHORT", color='red', fontsize=14, fontweight='bold', ha='center', transform=main_ax.transAxes)

                # Image ko memory (buffer) mein save karna
                buf = io.BytesIO()
                fig.savefig(buf, format="png", bbox_inches='tight')
                buf.seek(0)
                
                # Image Mobile screen par show karna
                st.success("Chart Tayyar Hai! Image par long-press kar ke Copy ya Save kar lein.")
                st.image(buf, use_container_width=True)
                
            else:
                st.error(f"API Error: {coin_symbol} ka data nahi mila.")
