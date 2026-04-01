# page_modules/login_page.py
import streamlit as st
from utils.auth import login_user, register_user, seed_demo

def render():
    seed_demo()
    col1,col2,col3 = st.columns([1,2,1])
    with col2:
        st.markdown("""
<div style="text-align:center;padding:24px 0 20px">
  <div style="width:60px;height:60px;background:linear-gradient(135deg,#7c6af7,#a78bfa);
  border-radius:16px;display:inline-flex;align-items:center;justify-content:center;
  font-size:28px;margin-bottom:10px;box-shadow:0 4px 16px rgba(124,106,247,0.3)">🎓</div>
  <h2 style="font-family:'Playfair Display',serif;color:#2d2150;margin:0">Study Partner</h2>
  <p style="color:#9ca3af;font-size:13px;margin-top:4px">Your intelligent study companion</p>
</div>
""", unsafe_allow_html=True)

        t1,t2 = st.tabs(["🔑  Sign In","✨  Create Account"])

        with t1:
            with st.form("login_form"):
                email    = st.text_input("Email address", placeholder="you@email.com")
                password = st.text_input("Password", type="password")
                c1,c2    = st.columns([3,1])
                submit   = c1.form_submit_button("Sign in →", use_container_width=True)
                demo_btn = c2.form_submit_button("Demo", use_container_width=True)

            if demo_btn:
                ok,r = login_user("student@studyai.com","demo123")
                if ok: st.session_state.user=r; st.session_state.page="Dashboard"; st.rerun()

            if submit:
                if not email or not password: st.error("Please fill in all fields.")
                else:
                    ok,r = login_user(email,password)
                    if ok:  st.session_state.user=r; st.session_state.page="Dashboard"; st.rerun()
                    else:   st.error(r)

            st.markdown("""
<div style="margin-top:12px;padding:12px 16px;background:#ede9fe;
border:1px solid #c4b5fd;border-radius:12px;font-size:13px">
  <b style="color:#7c3aed">Demo account:</b>
  <span style="color:#4c1d95"> student@studyai.com / demo123</span>
</div>
""", unsafe_allow_html=True)

        with t2:
            with st.form("reg_form"):
                name = st.text_input("Full name", placeholder="Your full name")
                email2 = st.text_input("Email", placeholder="you@email.com")
                role = st.selectbox("I am a", ["Student","Educator","Professional","Self-learner"])
                pw1  = st.text_input("Password", type="password", placeholder="Min 6 characters")
                pw2  = st.text_input("Confirm password", type="password")
                reg  = st.form_submit_button("Create account →", use_container_width=True)

            if reg:
                if not all([name,email2,pw1,pw2]): st.error("Fill in all fields.")
                elif pw1!=pw2:   st.error("Passwords don't match.")
                elif len(pw1)<6: st.error("Password must be 6+ characters.")
                else:
                    ok,msg = register_user(name,email2,pw1,role)
                    if ok:
                        ok2,r = login_user(email2,pw1)
                        if ok2: st.session_state.user=r; st.session_state.page="Dashboard"; st.rerun()
                    else: st.error(msg)
