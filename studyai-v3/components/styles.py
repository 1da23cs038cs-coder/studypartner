# components/styles.py  — Pastel light theme
import streamlit as st

def inject():
    st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@500;700&family=Nunito:wght@300;400;500;600;700&display=swap');

html,body,[data-testid="stAppViewContainer"]{
  background:#faf8ff!important;color:#2d2150!important;
  font-family:'Nunito',sans-serif!important}
[data-testid="stSidebar"]{background:#f0eeff!important;border-right:1px solid #ddd6fe!important}
[data-testid="stHeader"]{background:transparent!important}
.block-container{padding:1.2rem 2rem!important;max-width:1200px!important}

h1,h2,h3{font-family:'Playfair Display',serif!important;color:#2d2150!important}
h1{font-size:1.9rem!important} h2{font-size:1.4rem!important} h3{font-size:1.1rem!important}

/* Metric cards */
[data-testid="stMetric"]{background:#ede9fe!important;border:1px solid #c4b5fd!important;
  border-radius:16px!important;padding:1rem!important}
[data-testid="stMetricValue"]{color:#4c1d95!important;font-size:1.7rem!important;font-family:'Playfair Display',serif!important}
[data-testid="stMetricLabel"]{color:#7c3aed!important;font-size:0.72rem!important;text-transform:uppercase;letter-spacing:.5px}

/* Buttons */
.stButton>button{background:linear-gradient(135deg,#7c6af7,#a78bfa)!important;
  color:#fff!important;border:none!important;border-radius:12px!important;
  font-weight:600!important;font-family:'Nunito',sans-serif!important;
  box-shadow:0 2px 8px rgba(124,106,247,0.3)!important;transition:all .2s!important}
.stButton>button:hover{transform:translateY(-1px)!important;
  box-shadow:0 4px 16px rgba(124,106,247,0.4)!important}
.stButton>button[kind="secondary"]{background:#fff!important;
  border:1.5px solid #c4b5fd!important;color:#7c6af7!important;box-shadow:none!important}
.stButton>button[kind="secondary"]:hover{background:#ede9fe!important}

/* Inputs */
.stTextInput>div>div>input,.stTextArea>div>div>textarea,
.stSelectbox>div>div,.stNumberInput>div>div>input{
  background:#fff!important;border:1.5px solid #c4b5fd!important;
  border-radius:10px!important;color:#2d2150!important;font-family:'Nunito',sans-serif!important}
.stTextInput>div>div>input:focus,.stTextArea>div>div>textarea:focus{
  border-color:#7c6af7!important;box-shadow:0 0 0 3px rgba(124,106,247,0.15)!important}

/* Tabs */
.stTabs [data-baseweb="tab-list"]{background:#ede9fe!important;
  border-bottom:1px solid #c4b5fd!important;gap:4px!important;
  padding:4px!important;border-radius:12px!important}
.stTabs [data-baseweb="tab"]{background:transparent!important;
  color:#7c3aed!important;border-radius:9px!important;border:none!important;
  font-family:'Nunito',sans-serif!important;font-size:13px!important;font-weight:600!important}
.stTabs [aria-selected="true"]{background:#7c6af7!important;color:#fff!important}

/* Expander */
.streamlit-expanderHeader{background:#ede9fe!important;
  border:1px solid #c4b5fd!important;border-radius:12px!important;color:#4c1d95!important;
  font-weight:600!important}
.streamlit-expanderContent{background:#faf8ff!important;
  border:1px solid #ddd6fe!important;border-top:none!important;border-radius:0 0 12px 12px!important}

/* Progress */
.stProgress>div>div>div>div{
  background:linear-gradient(90deg,#a78bfa,#7c6af7)!important;border-radius:6px!important}

/* Chat */
[data-testid="stChatMessage"]{background:#ede9fe!important;
  border:1px solid #c4b5fd!important;border-radius:16px!important;margin-bottom:8px!important}
[data-testid="stChatInput"]>div{background:#fff!important;
  border:1.5px solid #c4b5fd!important;border-radius:14px!important}

/* Scrollbar */
::-webkit-scrollbar{width:5px;height:5px}
::-webkit-scrollbar-track{background:transparent}
::-webkit-scrollbar-thumb{background:#c4b5fd;border-radius:3px}

/* Cards */
.study-card{background:#fff;border:1px solid #ddd6fe;border-radius:16px;
  padding:18px 20px;margin-bottom:12px;
  box-shadow:0 2px 12px rgba(124,106,247,0.08)}

/* Notification toast */
.toast-popup{position:fixed;bottom:24px;right:24px;
  background:linear-gradient(135deg,#7c6af7,#a78bfa);color:#fff;
  padding:14px 22px;border-radius:14px;font-size:14px;font-weight:600;
  z-index:9999;box-shadow:0 4px 20px rgba(124,106,247,0.4);
  animation:slideUp .3s ease;max-width:300px}
@keyframes slideUp{from{transform:translateY(16px);opacity:0}to{transform:translateY(0);opacity:1}}

/* Sidebar active nav */
.sidebar-active{background:linear-gradient(135deg,#7c6af7,#a78bfa)!important;
  color:#fff!important;border-radius:10px!important}

hr{border-color:#ddd6fe!important}
#MainMenu,footer,[data-testid="stToolbar"]{visibility:hidden}
</style>""", unsafe_allow_html=True)
