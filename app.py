"""
Study Partner — Free Intelligent Study Planner
Run: streamlit run app.py
"""
import streamlit as st
from components.styles import inject
from page_modules import (
    landing_page, login_page, dashboard_page, setup_page,
    plan_page, tools_page, analytics_page, chat_page, profile_page,
)
from page_modules import my_plans_page, quiz_page

st.set_page_config(
    page_title="Study Partner",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)
inject()

for k, v in {
    "user": None, "page": "Landing",
    "timer_task": "", "chat_history": [],
}.items():
    if k not in st.session_state:
        st.session_state[k] = v

if st.session_state.page == "Landing":
    landing_page.render(); st.stop()

if st.session_state.user is None:
    st.session_state.page = "Login"
    login_page.render(); st.stop()

user = st.session_state.user

# ── SIDEBAR ──────────────────────────────────────────────────────
with st.sidebar:
    import base64
    from utils.auth import get_user
    from utils import storage
    from utils.helpers import get_progress

    fresh = get_user(user["email"]) or user

    # Brand
    st.markdown("""
<div style="padding:8px 0 16px;border-bottom:2px solid #ddd6fe;margin-bottom:14px">
  <div style="display:flex;align-items:center;gap:10px">
    <div style="width:38px;height:38px;
    background:linear-gradient(135deg,#7c6af7,#a78bfa);
    border-radius:10px;display:flex;align-items:center;
    justify-content:center;font-size:19px;
    box-shadow:0 3px 10px rgba(124,106,247,.3)">🎓</div>
    <div>
      <div style="font-family:'Playfair Display',serif;font-size:16px;
      font-weight:700;color:#4c1d95">Study Partner</div>
      <div style="font-size:10px;color:#a78bfa;font-weight:600;
      letter-spacing:.5px;text-transform:uppercase">Smart Learning</div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

    # User card
    col_av, col_info = st.columns([1, 2])
    with col_av:
        if fresh.get("photo"):
            try:
                st.image(base64.b64decode(fresh["photo"]), width=46)
            except Exception:
                st.markdown(f"""<div style="width:44px;height:44px;border-radius:50%;
background:linear-gradient(135deg,#7c6af7,#a78bfa);display:flex;align-items:center;
justify-content:center;font-size:16px;font-weight:700;color:#fff">{fresh.get('avatar','SP')}</div>""",
                unsafe_allow_html=True)
        else:
            st.markdown(f"""<div style="width:44px;height:44px;border-radius:50%;
background:linear-gradient(135deg,#7c6af7,#a78bfa);display:flex;align-items:center;
justify-content:center;font-size:16px;font-weight:700;color:#fff">{fresh.get('avatar','SP')}</div>""",
            unsafe_allow_html=True)
    with col_info:
        st.markdown(f"""<div style="margin-top:4px">
<div style="font-size:13px;font-weight:700;color:#4c1d95">{fresh['name']}</div>
<div style="font-size:10px;color:#9ca3af">{fresh['role']}</div></div>""",
        unsafe_allow_html=True)

    st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)

    # Navigation
    NAV = [
        ("⊞",  "Dashboard",  "Home & overview"),
        ("✦",  "New Plan",   "Create study plan"),
        ("📋", "My Plan",    "View active schedule"),
        ("📚", "My Plans",   "All plans library"),
        ("🧠", "Quiz",       "Quizzes & question banks"),
        ("🛠", "Tools",      "Timer & calendar"),
        ("📊", "Analytics",  "Performance charts"),
        ("🤖", "AI Tutor",   "Chat assistant"),
        ("👤", "Profile",    "Account settings"),
    ]

    st.markdown("<div style='font-size:10px;color:#a78bfa;font-weight:700;"
                "text-transform:uppercase;letter-spacing:.6px;"
                "margin-bottom:5px'>Navigation</div>",
                unsafe_allow_html=True)

    for icon, label, hint in NAV:
        active = st.session_state.page == label
        if st.button(f"{icon}  {label}",
                     key=f"nav_{label}",
                     use_container_width=True,
                     help=hint,
                     type="primary" if active else "secondary"):
            st.session_state.page = label; st.rerun()

    st.markdown("<div style='height:1px;background:#ddd6fe;margin:12px 0'></div>",
                unsafe_allow_html=True)

    # Mini plan progress
    plan = storage.load_active_plan(user["email"])
    all_plans = storage.load_all_plans(user["email"])
    if plan:
        comp = storage.load_completed(user["email"])
        prog = get_progress(plan, comp)
        pct  = prog["pct"]
        st.markdown(f"""
<div style="padding:10px 12px;background:#ede9fe;border:1px solid #c4b5fd;
border-radius:12px;margin-bottom:10px">
  <div style="font-size:10px;color:#7c3aed;font-weight:700;
  text-transform:uppercase;letter-spacing:.5px;margin-bottom:2px">Active Plan</div>
  <div style="font-size:11px;color:#4c1d95;font-weight:700;margin-bottom:1px;
  white-space:nowrap;overflow:hidden;text-overflow:ellipsis">{plan.get('title','')[:22]}</div>
  <div style="font-size:10px;color:#9ca3af;margin-bottom:5px">
    {pct}% · {prog['done_days']}/{prog['total_days']} days &nbsp;|&nbsp;
    {len(all_plans)} plan(s) total
  </div>
  <div style="height:5px;background:#ddd6fe;border-radius:3px;overflow:hidden">
    <div style="height:100%;width:{pct}%;
    background:linear-gradient(90deg,#a78bfa,#7c6af7);border-radius:3px"></div>
  </div>
</div>
""", unsafe_allow_html=True)
    else:
        st.markdown("""
<div style="padding:10px 12px;background:#faf8ff;border:1px dashed #c4b5fd;
border-radius:12px;margin-bottom:10px;text-align:center">
  <div style="font-size:11px;color:#9ca3af">No active plan</div>
  <div style="font-size:10px;color:#a78bfa">Click ✦ New Plan to start</div>
</div>
""", unsafe_allow_html=True)

    if st.button("⎋  Sign out", use_container_width=True, type="secondary"):
        for k in list(st.session_state.keys()): del st.session_state[k]
        st.rerun()

# ── ROUTER ───────────────────────────────────────────────────────
p = st.session_state.page
if   p == "Dashboard":  dashboard_page.render(user)
elif p == "New Plan":   setup_page.render(user)
elif p == "My Plan":    plan_page.render(user)
elif p == "My Plans":   my_plans_page.render(user)
elif p == "Quiz":       quiz_page.render(user)
elif p == "Tools":      tools_page.render(user)
elif p == "Analytics":  analytics_page.render(user)
elif p == "AI Tutor":   chat_page.render(user)
elif p == "Profile":    profile_page.render(user)
else:                   dashboard_page.render(user)
