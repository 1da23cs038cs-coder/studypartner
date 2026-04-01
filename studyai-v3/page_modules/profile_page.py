# page_modules/profile_page.py
import streamlit as st, base64
from utils.auth import update_profile, get_user
from utils import storage

def render(user):
    email = user["email"]
    # Reload fresh from disk
    fresh = get_user(email) or user
    st.markdown("## 👤 Profile Settings")

    c1,c2 = st.columns([1,2],gap="large")
    with c1:
        # Avatar / photo
        if fresh.get("photo"):
            img_data = base64.b64decode(fresh["photo"])
            st.image(img_data, width=140)
        else:
            st.markdown(f"""
<div style="width:120px;height:120px;border-radius:60px;
background:linear-gradient(135deg,#7c6af7,#a78bfa);
display:flex;align-items:center;justify-content:center;
font-size:44px;font-weight:700;color:#fff;
box-shadow:0 4px 16px rgba(124,106,247,0.3);margin-bottom:12px">
{fresh.get('avatar','??')}</div>
""", unsafe_allow_html=True)

        uploaded = st.file_uploader("📷 Change photo", type=["jpg","jpeg","png"], label_visibility="collapsed")
        if uploaded:
            ok,updated = update_profile(email, photo_bytes=uploaded.read())
            if ok:
                st.session_state.user = updated
                st.success("Photo updated!")
                st.rerun()

    with c2:
        st.markdown("#### Edit Details")
        with st.form("profile_form"):
            new_name = st.text_input("Full name", value=fresh.get("name",""))
            new_role = st.selectbox("Role", ["Student","Educator","Professional","Self-learner"],
                index=["Student","Educator","Professional","Self-learner"].index(fresh.get("role","Student")) if fresh.get("role") in ["Student","Educator","Professional","Self-learner"] else 0)
            new_bio  = st.text_area("Bio (optional)", value=fresh.get("bio",""), placeholder="Tell us about yourself...", height=80)
            save = st.form_submit_button("💾 Save changes", use_container_width=True)

        if save:
            ok,updated = update_profile(email, name=new_name.strip(), bio=new_bio, role=new_role)
            if ok:
                st.session_state.user = updated
                st.success("✅ Profile updated!")
                st.rerun()
            else: st.error(updated)

    st.markdown("---")

    # Account stats
    st.markdown("#### 📊 Account Stats")
    plan  = storage.load_active_plan(email)
    comp  = storage.load_completed(email)
    timers= storage.load_timers(email)
    plans = storage.load_all_plans(email)
    scores= storage.load_quiz_scores(email)

    a1,a2,a3,a4 = st.columns(4)
    a1.metric("Plans created",  len(plans))
    a2.metric("Total focus",    f"{round(sum(s['minutes'] for s in timers)/60,1)}h")
    a3.metric("Quizzes taken",  len(scores))
    acc = round(sum(1 for s in scores if s["correct"])/len(scores)*100) if scores else 0
    a4.metric("Quiz accuracy",  f"{acc}%")

    st.markdown(f"<div style='font-size:12px;color:#9ca3af;margin-top:8px'>Member since {fresh.get('created_at','')[:10]}</div>", unsafe_allow_html=True)

    st.markdown("---")

    # Danger zone
    st.markdown("#### ⚠️ Account Actions")
    col_s, col_d = st.columns(2)
    with col_s:
        if st.button("⎋ Sign out", use_container_width=True, type="secondary"):
            for k in list(st.session_state.keys()): del st.session_state[k]
            st.rerun()
