# page_modules/setup_page.py
import streamlit as st
from utils import storage
from utils.planner import generate_plan

GOALS=["Exam preparation","Project work","Self-improvement",
       "Career switch","Research","Certification","Interview prep"]

def render(user):
    st.markdown("## ✦ Create Your Study Plan")
    st.markdown("<p style='color:#9ca3af;font-size:13px;margin-top:-6px'>Fill in your details — plan generates instantly.</p>",unsafe_allow_html=True)

    existing = storage.load_active_plan(user["email"])
    if existing:
        st.info(f"📋 Active: **{existing.get('title','')}** — new plan will be saved separately.")

    with st.form("setup_form"):
        subject = st.text_input("📚 Subject / Topic *",
            placeholder="e.g. Python, World War 2, Calculus, French, Machine Learning...")
        c1,c2 = st.columns(2)
        with c1:
            duration = st.number_input("⏳ Duration",min_value=1,max_value=365,value=4)
            unit     = st.selectbox("Unit",["weeks","days","months"])
        with c2:
            hours = st.number_input("🕐 Daily study hours",min_value=0.5,max_value=16.0,value=2.0,step=0.5)
            diff  = st.selectbox("🎯 Difficulty",["beginner","intermediate","advanced"],
                format_func=lambda x:{"beginner":"🌱 Beginner","intermediate":"📚 Intermediate","advanced":"🚀 Advanced"}[x])

        st.markdown("**🎯 Study goals**")
        gcols=st.columns(4); goals=[]
        for i,g in enumerate(GOALS):
            with gcols[i%4]:
                if st.checkbox(g,value=(g=="Exam preparation"),key=f"g_{g}"): goals.append(g)

        days_est=duration*(7 if unit=="weeks" else 30 if unit=="months" else 1)
        st.markdown(f"""
<div style="padding:11px 16px;background:#ede9fe;border:1px solid #c4b5fd;
border-radius:10px;font-size:13px;color:#7c3aed;margin:10px 0">
  Generates <b>~{round(days_est*0.85)} study days</b> across
  <b>{round(days_est*0.85/7)+1} weeks</b> — instantly, no internet needed.
</div>""",unsafe_allow_html=True)
        submit=st.form_submit_button("⚡ Generate Plan Instantly",use_container_width=True)

    if submit:
        if not subject.strip(): st.error("Please enter a subject."); return
        with st.spinner("Building your personalized plan…"):
            try:
                plan=generate_plan(subject=subject.strip(),duration=int(duration),unit=unit,
                    hours_per_day=float(hours),difficulty=diff,goals=goals or ["general learning"])
                storage.save_plan(user["email"],plan)
                st.success(f"🎉 **{plan['title']}** generated!")
                st.balloons()
                st.info("👉 Go to **My Plan** in the sidebar to view your schedule.")
            except Exception as e: st.error(f"Error: {e}")
