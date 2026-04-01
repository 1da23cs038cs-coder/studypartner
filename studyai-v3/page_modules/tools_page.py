# page_modules/tools_page.py
import streamlit as st, time
from datetime import datetime, timedelta, date
import calendar as cal
from utils import storage
from utils.planner import get_quiz_question

MODES={"🍅 Pomodoro 25m":25,"☕ Short break 5m":5,"🧠 Deep work 50m":50}

def render(user):
    email=user["email"]
    plan=storage.load_active_plan(email)
    t1,t2,t3,t4=st.tabs(["⏱ Focus Timer","🧠 Self Quiz","📅 Calendar","⏰ Reminders"])

    # ── TIMER ──────────────────────────────────────────────────
    with t1:
        st.markdown("### ⏱ Focus Timer")
        cl,cr=st.columns([1,1],gap="large")
        with cl:
            mode=st.radio("Mode",list(MODES.keys()),horizontal=True)
            dur=MODES[mode]
            task=st.text_input("Current task",value=st.session_state.get("timer_task",""),
                placeholder="e.g. Chapter 3 — Linear Algebra")
            for k,v in [("t_run",False),("t_end",None),("t_dur",dur*60)]:
                if k not in st.session_state: st.session_state[k]=v
            rem=max(0,(st.session_state.t_end-datetime.now()).total_seconds()) \
                if st.session_state.t_run and st.session_state.t_end \
                else st.session_state.get("t_dur",dur*60)
            mm,ss=int(rem//60),int(rem%60)
            st.markdown(f"""
<div style="text-align:center;padding:24px;background:linear-gradient(135deg,#ede9fe,#faf8ff);
border:1.5px solid #c4b5fd;border-radius:20px;margin:10px 0;
box-shadow:0 4px 16px rgba(124,106,247,0.15)">
  <div style="font-size:58px;font-weight:300;color:#4c1d95;
  font-family:'Playfair Display',serif;letter-spacing:-2px;line-height:1">{mm:02d}:{ss:02d}</div>
  <div style="font-size:12px;color:#7c3aed;margin-top:8px;font-weight:600">{mode.split(' ',1)[1]}</div>
</div>""",unsafe_allow_html=True)
            st.progress(min(1.0,1.0-(rem/(dur*60))) if dur>0 else 0)
            b1,b2,b3=st.columns(3)
            if b1.button("▶ Start" if not st.session_state.t_run else "⏸ Pause",use_container_width=True):
                if not st.session_state.t_run:
                    st.session_state.t_run=True; st.session_state.t_dur=dur*60
                    st.session_state.t_end=datetime.now()+timedelta(seconds=rem if rem>0 else dur*60)
                else: st.session_state.t_run=False
                st.rerun()
            if b2.button("⟳ Reset",use_container_width=True,type="secondary"):
                st.session_state.t_run=False; st.session_state.t_dur=dur*60; st.session_state.t_end=None; st.rerun()
            if b3.button("✅ Log",use_container_width=True,type="secondary"):
                done_m=round((dur*60-rem)/60)
                if done_m>0: storage.save_timer(email,done_m,task or mode); st.toast(f"Logged {done_m}m session! 🎉")
                st.session_state.t_run=False; st.session_state.t_end=None
            if st.session_state.t_run and rem<=0:
                storage.save_timer(email,dur,task or mode)
                st.session_state.t_run=False; st.balloons(); st.toast(f"🎉 {dur}m session complete! Take a break.")
        with cr:
            sessions=storage.load_timers(email)
            total_m=sum(s["minutes"] for s in sessions)
            today_s=datetime.now().strftime("%Y-%m-%d")
            today_m=sum(s["minutes"] for s in sessions if s["ts"][:10]==today_s)
            st.markdown(f"""
<div style="background:#fff;border:1px solid #ddd6fe;border-radius:16px;padding:18px;
box-shadow:0 2px 8px rgba(124,106,247,0.08)">
  <div style="font-size:12px;color:#7c3aed;font-weight:700;text-transform:uppercase;
  letter-spacing:.5px;margin-bottom:12px">SESSION STATS</div>
  <div style="display:flex;gap:18px;flex-wrap:wrap">
    <div><div style="font-size:28px;font-weight:700;color:#4c1d95">{len(sessions)}</div>
    <div style="font-size:11px;color:#9ca3af">Total sessions</div></div>
    <div><div style="font-size:28px;font-weight:700;color:#4c1d95">{total_m}m</div>
    <div style="font-size:11px;color:#9ca3af">Total time</div></div>
    <div><div style="font-size:28px;font-weight:700;color:#7c6af7">{today_m}m</div>
    <div style="font-size:11px;color:#9ca3af">Today</div></div>
  </div>
</div>""",unsafe_allow_html=True)
            if sessions:
                st.markdown("<div style='margin-top:12px;font-size:12px;color:#7c3aed;font-weight:600'>RECENT SESSIONS</div>",unsafe_allow_html=True)
                for s in reversed(sessions[-5:]):
                    st.markdown(f"<div style='font-size:12px;color:#7c3aed;padding:5px 0;border-bottom:1px solid #ede9fe'>⏱ {s['minutes']}m — {s.get('task','')[:26]} <span style='color:#c4b5fd'>· {s['ts'][11:16]}</span></div>",unsafe_allow_html=True)
        if st.session_state.t_run: time.sleep(1); st.rerun()

    # ── QUIZ ───────────────────────────────────────────────────
    with t2:
        st.markdown("### 🧠 Self-Assessment Quiz")
        cq,cs=st.columns([2,1])
        with cq:
            if st.button("✦ New Question",use_container_width=True):
                topics=[]
                if plan:
                    for w in plan.get("weeks",[]):
                        for d in w.get("days",[]):
                            for s in d.get("sessions",[]):
                                if s.get("type")!="buffer": topics.append(s["topic"])
                q=get_quiz_question(plan.get("subject","") if plan else "",topics)
                st.session_state.cur_q=q; st.session_state.q_answered=False; st.session_state.q_sel=None
            if "cur_q" in st.session_state and st.session_state.cur_q:
                q=st.session_state.cur_q
                st.markdown(f"""
<div style="background:#fff;border:1.5px solid #c4b5fd;border-radius:14px;padding:18px;margin:10px 0;
box-shadow:0 2px 8px rgba(124,106,247,0.1)">
  <div style="font-size:15px;font-weight:600;color:#2d2150;line-height:1.5">{q['question']}</div>
</div>""",unsafe_allow_html=True)
                answered=st.session_state.get("q_answered",False)
                sel=st.session_state.get("q_sel",None)
                for i,opt in enumerate(q["options"]):
                    correct=answered and i==q["answer"]
                    wrong=answered and i==sel and i!=q["answer"]
                    bg="rgba(74,222,128,0.15)" if correct else "rgba(249,115,22,0.15)" if wrong else "#fff"
                    border="#4ade80" if correct else "#f97316" if wrong else "#c4b5fd"
                    color="#166534" if correct else "#9a3412" if wrong else "#2d2150"
                    st.markdown(f"""<div style="padding:11px 16px;border:1.5px solid {border};
border-radius:10px;background:{bg};color:{color};font-size:13px;
font-weight:500;margin-bottom:7px">{opt}</div>""",unsafe_allow_html=True)
                    if not answered:
                        if st.button(f"Select {i+1}",key=f"opt_{i}",use_container_width=True,type="secondary"):
                            st.session_state.q_sel=i; st.session_state.q_answered=True
                            correct_ans=(i==q["answer"]); storage.save_quiz_score(email,correct_ans)
                            if correct_ans: st.toast("✅ Correct! Well done!",icon="🌟")
                            else: st.toast("❌ Incorrect — check the explanation below",icon="📖")
                            st.rerun()
                if answered:
                    ok=sel==q["answer"]
                    st.markdown(f"""<div style="padding:12px;border-radius:10px;margin-top:8px;
font-size:13px;line-height:1.6;font-weight:500;
background:{'rgba(74,222,128,0.1)' if ok else 'rgba(249,115,22,0.1)'};
color:{'#166534' if ok else '#9a3412'};
border:1.5px solid {'#4ade80' if ok else '#f97316'}">
{'✓ Correct! ' if ok else '✗ Incorrect. '}{q['explanation']}</div>""",unsafe_allow_html=True)
            else: st.info("Click **New Question** to start.")
        with cs:
            scores=storage.load_quiz_scores(email)
            total=len(scores); correct=sum(1 for s in scores if s["correct"])
            acc=round(correct/total*100) if total else 0
            st.markdown(f"""
<div style="background:#fff;border:1px solid #ddd6fe;border-radius:14px;padding:16px;
box-shadow:0 2px 8px rgba(124,106,247,0.08)">
  <div style="font-size:12px;color:#7c3aed;font-weight:700;text-transform:uppercase;
  letter-spacing:.5px;margin-bottom:10px">QUIZ STATS</div>
  <div style="margin-bottom:8px"><div style="font-size:28px;font-weight:700;color:#4c1d95">{total}</div>
  <div style="font-size:11px;color:#9ca3af">Questions answered</div></div>
  <div style="margin-bottom:8px"><div style="font-size:28px;font-weight:700;color:#16a34a">{acc}%</div>
  <div style="font-size:11px;color:#9ca3af">Accuracy</div></div>
  <div><div style="font-size:28px;font-weight:700;color:#7c6af7">{correct}</div>
  <div style="font-size:11px;color:#9ca3af">Correct answers</div></div>
</div>""",unsafe_allow_html=True)

    # ── CALENDAR ───────────────────────────────────────────────
    with t3:
        st.markdown("### 📅 Study Calendar")
        if not plan: st.info("Create a plan to see calendar."); return
        today=date.today()
        plan_days={}; d=today
        for week in plan.get("weeks",[]):
            for day in week.get("days",[]):
                plan_days[d.isoformat()]=day["title"]
                d=(datetime.combine(d,datetime.min.time())+timedelta(days=1)).date()
        if "cal_off" not in st.session_state: st.session_state.cal_off=0
        try:
            view_m=(today.month-1+st.session_state.cal_off)%12+1
            view_y=today.year+((today.month-1+st.session_state.cal_off)//12)
            view=date(view_y,view_m,1)
        except: view=date(today.year,today.month,1)
        months=["January","February","March","April","May","June","July","August","September","October","November","December"]
        ch2,cc1,cc2=st.columns([4,1,1])
        ch2.markdown(f"**{months[view.month-1]} {view.year}**")
        if cc1.button("‹",type="secondary"): st.session_state.cal_off-=1; st.rerun()
        if cc2.button("›",type="secondary"): st.session_state.cal_off+=1; st.rerun()
        days_in_month=cal.monthrange(view.year,view.month)[1]
        first_dow=(date(view.year,view.month,1).weekday()+1)%7
        hcols=st.columns(7)
        for i,h in enumerate(["Sun","Mon","Tue","Wed","Thu","Fri","Sat"]):
            hcols[i].markdown(f"<div style='text-align:center;font-size:11px;color:#9ca3af;font-weight:600'>{h}</div>",unsafe_allow_html=True)
        cells=[""]*first_dow+list(range(1,days_in_month+1))
        while len(cells)%7!=0: cells.append("")
        for row in [cells[i:i+7] for i in range(0,len(cells),7)]:
            rcols=st.columns(7)
            for ci,dn in enumerate(row):
                if dn=="": rcols[ci].markdown("<div style='height:36px'></div>",unsafe_allow_html=True); continue
                ds=f"{view.year}-{view.month:02d}-{dn:02d}"
                has=ds in plan_days; is_today=(view.year==today.year and view.month==today.month and dn==today.day)
                bg="linear-gradient(135deg,#7c6af7,#a78bfa)" if is_today else "rgba(167,139,250,0.2)" if has else "#fff"
                color="#fff" if is_today else "#7c6af7" if has else "#9ca3af"
                border="#7c6af7" if (has or is_today) else "#ddd6fe"
                rcols[ci].markdown(f"""<div title="{plan_days.get(ds,'')}"
style="text-align:center;padding:7px 2px;border-radius:9px;background:{bg};
color:{color};font-size:12px;font-weight:{'700' if is_today else '400'};
border:1.5px solid {border}">{dn}</div>""",unsafe_allow_html=True)
        st.markdown("---"); st.markdown("**📌 Next 7 days**")
        shown=0
        for i in range(14):
            ds=(today+timedelta(days=i)).isoformat()
            if ds in plan_days:
                lbl="**Today**" if i==0 else f"In {i} day{'s' if i>1 else ''}"
                st.markdown(f"- {lbl} ({ds}): {plan_days[ds]}"); shown+=1
                if shown>=7: break

    # ── REMINDERS ─────────────────────────────────────────────
    with t4:
        st.markdown("### ⏰ Study Reminders")
        st.caption("Set daily reminders to keep your study sessions on track.")

        with st.form("reminder_form"):
            r_title=st.text_input("Reminder title",placeholder="e.g. Morning study session")
            r_col1,r_col2=st.columns(2)
            with r_col1:
                r_time=st.time_input("Reminder time",value=datetime.now().replace(hour=9,minute=0,second=0,microsecond=0).time())
            with r_col2:
                r_days=st.multiselect("Repeat on days",["Mon","Tue","Wed","Thu","Fri","Sat","Sun"],
                    default=["Mon","Tue","Wed","Thu","Fri"])
            r_msg=st.text_input("Message (optional)",placeholder="Time to study!")
            add_r=st.form_submit_button("➕ Add Reminder",use_container_width=True)

        if add_r:
            if not r_title.strip(): st.error("Enter a reminder title.")
            else:
                from datetime import datetime as dt
                today_dt=date.today()
                next_trigger=dt.combine(today_dt, r_time).isoformat()
                reminder={
                    "title": r_title.strip(),
                    "time": r_time.strftime("%H:%M"),
                    "days": r_days,
                    "message": r_msg or f"Time to study: {r_title}",
                    "active": True,
                    "next_trigger": next_trigger,
                }
                storage.save_reminder(email, reminder)
                st.toast(f"⏰ Reminder set for {r_time.strftime('%I:%M %p')}!",icon="✅")
                st.rerun()

        reminders=storage.load_reminders(email)
        if not reminders:
            st.info("No reminders set. Add one above to get notified for your study sessions.")
        else:
            st.markdown(f"**{len(reminders)} reminder(s) set**")
            for r in reminders:
                is_active=r.get("active",True)
                col_r,col_t,col_del=st.columns([4,1,1])
                col_r.markdown(f"""
<div style="padding:12px 14px;background:{'#ede9fe' if is_active else '#f5f5f5'};
border:1.5px solid {'#c4b5fd' if is_active else '#e5e7eb'};border-radius:12px">
  <div style="font-size:13px;font-weight:600;color:{'#4c1d95' if is_active else '#9ca3af'}">
    {'🔔' if is_active else '🔕'} {r.get('title','')}
  </div>
  <div style="font-size:11px;color:#9ca3af;margin-top:2px">
    ⏰ {r.get('time','--:--')} · {', '.join(r.get('days',[])) or 'No days'} · {r.get('message','')}
  </div>
</div>""",unsafe_allow_html=True)
                if col_t.button("Toggle",key=f"tog_{r['id']}",type="secondary",use_container_width=True):
                    storage.toggle_reminder(email,r["id"]); st.rerun()
                if col_del.button("🗑",key=f"del_{r['id']}",type="secondary",use_container_width=True):
                    storage.delete_reminder(email,r["id"]); st.rerun()
