# page_modules/landing_page.py
import streamlit as st

def render():
    st.markdown("""
<div style="min-height:85vh;display:flex;flex-direction:column;
align-items:center;justify-content:center;text-align:center;padding:40px 20px">
  <div style="width:88px;height:88px;
  background:linear-gradient(135deg,#7c6af7,#a78bfa);
  border-radius:24px;display:inline-flex;align-items:center;
  justify-content:center;font-size:42px;margin-bottom:20px;
  box-shadow:0 8px 32px rgba(124,106,247,.35)">🎓</div>

  <h1 style="font-family:'Playfair Display',serif;font-size:3rem;
  font-weight:700;color:#2d2150;margin-bottom:8px;line-height:1.2">
    Study Partner
  </h1>
  <p style="font-size:1.15rem;color:#7c3aed;margin-bottom:6px;font-weight:600">
    Your intelligent study companion
  </p>
  <p style="font-size:1rem;color:#9ca3af;margin-bottom:44px;
  max-width:500px;line-height:1.7">
    AI-powered study plans, adaptive scheduling, focus tools, 
    performance analytics and a personal tutor — all completely free.
  </p>

  <div style="display:flex;flex-wrap:wrap;gap:10px;
  justify-content:center;margin-bottom:48px">
""" + "".join(
        f'<span style="padding:8px 18px;background:#ede9fe;color:#7c3aed;'
        f'border-radius:20px;font-size:13px;font-weight:600;'
        f'border:1px solid #c4b5fd">{f}</span>'
        for f in [
            "✦ Instant plan generation",
            "📊 Analytics dashboard",
            "⏱ Pomodoro timer",
            "🧠 Smart quiz engine",
            "🤖 AI chat tutor",
            "📅 Study calendar",
            "⏰ Study reminders",
            "👤 Profile & notes",
        ]
    ) + """
  </div>
</div>
""", unsafe_allow_html=True)

    _, mid, _ = st.columns([2, 1, 2])
    with mid:
        if st.button("🚀  Get Started", use_container_width=True):
            st.session_state.page = "Login"
            st.rerun()
