# page_modules/analytics_page.py
import streamlit as st
from utils import storage, charts, helpers
from utils.planner import get_recommendations

def render(user):
    email=user["email"]
    plan=storage.load_active_plan(email)
    comp=storage.load_completed(email)
    timers=storage.load_timers(email)
    scores=storage.load_quiz_scores(email)

    st.markdown("## 📊 Performance Analytics")
    if not plan: st.info("Create a plan to see analytics."); return

    prog=helpers.get_progress(plan,comp)
    perf=helpers.perf_metrics(prog["done_days"],prog["pct"],prog["done"],prog["total"])
    acc=round(sum(1 for s in scores if s["correct"])/len(scores)*100) if scores else 0

    c1,c2,c3,c4=st.columns(4)
    c1.metric("📈 Completion",f"{prog['pct']}%","overall")
    c2.metric("📅 Study Days",prog["done_days"],f"of {prog['total_days']}")
    c3.metric("🔥 Streak",f"{min(prog['done_days'],7)} days","in a row")
    c4.metric("🧠 Quiz Score",f"{acc}%",f"{len(scores)} answered")
    st.markdown("---")

    r1,r2=st.columns(2,gap="medium")
    with r1: st.plotly_chart(charts.topic_bars(plan,comp),  use_container_width=True,config={"displayModeBar":False})
    with r2: st.plotly_chart(charts.weekly_hours(plan,comp),use_container_width=True,config={"displayModeBar":False})

    r3,r4=st.columns(2,gap="medium")
    with r3: st.plotly_chart(charts.radar_chart(perf),       use_container_width=True,config={"displayModeBar":False})
    with r4: st.plotly_chart(charts.heatmap_chart(timers),   use_container_width=True,config={"displayModeBar":False})

    r5,r6=st.columns(2,gap="medium")
    with r5: st.plotly_chart(charts.type_donut(plan,comp),   use_container_width=True,config={"displayModeBar":False})
    with r6:
        if scores: st.plotly_chart(charts.quiz_line(scores), use_container_width=True,config={"displayModeBar":False})
    st.markdown("---")

    ri1,ri2=st.columns(2,gap="medium")
    with ri1:
        st.markdown("### 💡 Smart Insights")
        insights=[
            ("info" if prog["pct"]>=50 else "warn",
             f"You are {prog['pct']}% through your plan. {'Keep it up!' if prog['pct']>=50 else 'Try completing 2+ sessions per day.'}"),
            ("warn" if perf["Consistency"]<60 else "ok",
             f"Consistency: {perf['Consistency']}. {'Study every day — even 20 min helps.' if perf['Consistency']<60 else 'Excellent habit building!'}"),
            ("info",f"Quiz accuracy: {acc}%. {'Good recall!' if acc>=70 else 'Review weak topics and retry quizzes.'}") if scores
            else ("info","Take quizzes in the Tools tab to track retention."),
            ("info",f"Total focus logged: {round(sum(s['minutes'] for s in timers)/60,1)}h. Revision boosts retention 40%."),
        ]
        borders={"warn":"#f97316","info":"#60a5fa","ok":"#4ade80"}
        icons={"warn":"⚠️","info":"ℹ️","ok":"✅"}
        for typ,txt in insights:
            b=borders.get(typ,"#7c6af7"); ic=icons.get(typ,"💡")
            st.markdown(f"""<div style="padding:11px 14px;background:#fff;border-radius:10px;
border-left:4px solid {b};font-size:13px;color:#4c1d95;line-height:1.6;
margin-bottom:8px;box-shadow:0 2px 6px rgba(124,106,247,0.08)">{ic} {txt}</div>""",unsafe_allow_html=True)
    with ri2:
        st.markdown("### 🤖 Smart Recommendations")
        weak=helpers.weak_topics(plan,comp)
        recs=get_recommendations(plan.get("subject",""),weak,prog["pct"])
        for r in recs:
            st.markdown(f"""<div style="padding:11px 14px;background:#ede9fe;border-radius:10px;
border:1px solid #c4b5fd;font-size:13px;color:#4c1d95;line-height:1.6;
margin-bottom:8px">💡 {r}</div>""",unsafe_allow_html=True)
