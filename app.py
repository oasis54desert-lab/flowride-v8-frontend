import os, requests, pandas as pd, streamlit as st
APP_VERSION="V8.0-FLOWRIDE-CUSTOMER"
API_URL=os.getenv("FLOWRIDE_API_URL","").rstrip("/"); API_KEY=os.getenv("FLOWRIDE_API_KEY","")
try: API_URL=st.secrets.get("FLOWRIDE_API_URL",API_URL).rstrip("/"); API_KEY=st.secrets.get("FLOWRIDE_API_KEY",API_KEY)
except Exception: pass
st.set_page_config(page_title="Indian Stock Scanner FLOWRIDE",page_icon="🇮🇳",layout="centered")
st.markdown("<style>div.stButton>button{width:100%;border-radius:10px;font-weight:600} .flow{padding:14px;border-radius:12px;text-align:center;font-size:25px;font-weight:700;background:#eef5ff} .small{font-size:12px;color:#777}</style>",unsafe_allow_html=True)
st.title("🇮🇳 Indian Stock Scanner")
st.caption("FLOWRIDE • Find the trend. Ride the flow. Exit when it breaks.")
if not API_URL or not API_KEY:
 st.error("Backend configuration is missing. Set FLOWRIDE_API_URL and FLOWRIDE_API_KEY in Streamlit Secrets."); st.stop()
def call(path,params=None,timeout=90):
 r=requests.get(API_URL+path,params=params,headers={"X-API-Key":API_KEY},timeout=timeout)
 if r.status_code>=400: raise RuntimeError(r.text)
 return r.json()
try:
 h=requests.get(API_URL+"/health",timeout=20).json()
 st.info(f"Universe: **{h.get('total',0):,}** securities • NSE **{h.get('nse',0):,}** • BSE **{h.get('bse',0):,}**")
except Exception: st.warning("Backend is waking up or unavailable. Try again in a moment.")
st.subheader("🔎 Search Stock")
q=st.text_input("Search NSE/BSE symbol, company name or scrip code",placeholder="RELIANCE, TCS, PRICOL, 500325...")
ex=st.selectbox("Exchange",["ALL","NSE","BSE"])
if st.button("🔍 SEARCH",type="primary") and q.strip():
 try: st.session_state.results=call("/search",{"q":q.strip(),"exchange":ex})["results"]
 except Exception as e: st.error(f"Search failed: {e}")
results=st.session_state.get("results",[])
if results:
 labels=[f"{r['symbol']} — {r['name']} ({r['exchange']})" for r in results]
 idx=st.selectbox("Select stock",range(len(labels)),format_func=lambda i:labels[i]); sel=results[idx]
 if st.button("📊 ANALYZE SELECTED STOCK",type="primary"):
  try: st.session_state.analysis=call("/analyze",{"exchange":sel["exchange"],"symbol":sel["symbol"]})
  except Exception as e: st.error(f"Analysis failed: {e}")
a=st.session_state.get("analysis")
if a:
 st.divider(); st.subheader(f"📊 {a['name']} | {a['symbol']} ({a['exchange']})")
 st.markdown(f"<div class='flow'>{'🟢' if a['flowride']=='BUY' else '🔴' if a['flowride']=='EXIT' else '🔵'} {a['flowride']}<br><span style='font-size:15px'>Flow Score {a['flow_score']:.0f}/100</span></div>",unsafe_allow_html=True)
 c=st.columns(4); c[0].metric("Close",f"₹{a['close']:,.2f}"); c[1].metric("Score",f"{a['score']:.0f}/100"); c[2].metric("Signal",a['signal']); c[3].metric("RSI",f"{a['rsi']:.1f}" if a['rsi'] is not None else "—")
 c=st.columns(3); c[0].metric("Stop Loss",f"₹{a['stop_loss']:,.2f}"); c[1].metric("Target 1",f"₹{a['target1']:,.2f}"); c[2].metric("Target 2",f"₹{a['target2']:,.2f}")
 st.caption(f"Latest data: {a['latest_date']} • Data is historical/delayed, not exchange real-time.")
 if a['reasons']: st.write("**Positive factors:** "+" • ".join(a['reasons']))
st.divider(); st.subheader("🚀 Ranked Universe Scanner")
scan_ex=st.selectbox("Exchange for scan",["NSE","BSE"]); limit=st.number_input("Stocks to scan",min_value=10,max_value=1000,value=100,step=10)
if st.button("🔄 RUN EOD SCAN",type="primary"):
 try:
  with st.spinner(f"Scanning {limit} {scan_ex} securities…"): data=call("/scan",{"exchange":scan_ex,"limit":int(limit)},timeout=180)
  out=pd.DataFrame(data["results"]); st.success(f"Usable: {data['usable']} • Failed/unavailable: {data['failed']}")
  if not out.empty:
   st.dataframe(out[["symbol","name","exchange","close","score","signal","flowride","flow_score","rsi","atr_pct","stop_loss","target1"]].round(2),use_container_width=True,hide_index=True)
 except Exception as e: st.error(f"Scan failed: {e}")
st.caption("FLOWRIDE is a rules-based technical market-analysis system. It is not personalized investment advice.")
