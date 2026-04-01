# page_modules/dashboard_page.py
import streamlit as st
from datetime import datetime, timedelta
from utils import storage, charts, helpers


def render(user):
    email  = user["email"]
    plan   = storage.load_active_plan(email)
    comp   = storage.load_completed(email)
    gen_at = storage.load_generated_at(email)
    timers = storage.load_timers(email)
    scores = storage.load_quiz_scores(email)
    missed = storage.load_missed(email)
    all_plans = storage.load_all_plans(email)

    prog = helpers.get_progress(plan, comp) if plan else dict(
        pct=0, done=0, total=0, done_days=0, total_days=0)
    perf = helpers.perf_metrics(
        prog["done_days"], prog["pct"], prog["done"], prog["total"])

    hour   = datetime.now().hour
    greet  = "Good morning" if hour < 12 else "Good afternoon" if hour < 18 else "Good evening"
    fname  = user["name"].split()[0]
    today  = datetime.now().strftime("%A, %B %d, %Y")

    # ── Check & show reminders ───────────────────────────────────
    _check_reminders(email)

    # ── Header banner ────────────────────────────────────────────
    st.markdown(f"""
<div style="background:linear-gradient(135deg,#ede9fe 0%,#faf8ff 60%,#e0e7ff 100%);
border:1.5px solid #c4b5fd;border-radius:18px;padding:22px 28px;
margin-bottom:24px;display:flex;align-items:center;justify-content:space-between;
flex-wrap:wrap;gap:12px;box-shadow:0 4px 20px rgba(124,106,247,.1)">
  <div>
    <div style="font-family:'Playfair Display',serif;font-size:26px;
    font-weight:700;color:#2d2150;margin-bottom:3px">
      {greet}, {fname}! 👋
    </div>
    <div style="font-size:13px;color:#7c3aed;font-weight:500">{today}</div>
    <div style="font-size:12px;color:#9ca3af;margin-top:2px">
      {f"Plan active · created {helpers.rel_time(gen_at)}" if gen_at
       else "No study plan yet — create one to get started!"}
    </div>
  </div>
  <div style="display:flex;gap:10px;flex-wrap:wrap">
    <div style="padding:10px 18px;background:linear-gradient(135deg,#7c6af7,#a78bfa);
    border-radius:12px;text-align:center;color:#fff;min-width:70px;
    box-shadow:0 3px 10px rgba(124,106,247,.3)">
      <div style="font-size:22px;font-weight:700">{prog['pct']}%</div>
      <div style="font-size:10px;opacity:.85">Progress</div>
    </div>
    <div style="padding:10px 18px;background:linear-gradient(135deg,#a78bfa,#c4b5fd);
    border-radius:12px;text-align:center;color:#fff;min-width:70px;
    box-shadow:0 3px 10px rgba(124,106,247,.2)">
      <div style="font-size:22px;font-weight:700">{prog['done_days']}</div>
      <div style="font-size:10px;opacity:.85">Days Done</div>
    </div>
    <div style="padding:10px 18px;background:linear-gradient(135deg,#86efac,#4ade80);
    border-radius:12px;text-align:center;color:#fff;min-width:70px;
    box-shadow:0 3px 10px rgba(74,222,128,.25)">
      <div style="font-size:22px;font-weight:700">{len(all_plans)}</div>
      <div style="font-size:10px;opacity:.85">Plans</div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

    # ── No plan state ────────────────────────────────────────────
    if not plan:
        col1, col2, col3 = st.columns(3)
        _empty_card(col1, "📚", "Create a Study Plan",
                    "Generate your personalized AI study plan instantly — no API key needed.",
                    "✦ New Plan", "New Plan")
        _empty_card(col2, "🧠", "Quiz Yourself",
                    "Test your knowledge with smart quiz questions on any topic.",
                    "🛠 Open Tools", "Tools")
        _empty_card(col3, "🤖", "Chat with AI Tutor",
                    "Ask anything — study tips, motivation, explanations.",
                    "🤖 Open Chat", "AI Tutor")
        return

    # ── Missed banner ────────────────────────────────────────────
    if missed:
        st.warning(
            f"⚠️ **{len(missed)} missed session(s) detected.** "
            "Go to **My Plan** to reschedule automatically.")

    # ── Stat cards ───────────────────────────────────────────────
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("📈 Progress",     f"{prog['pct']}%",
              f"{prog['done']}/{prog['total']} sessions")
    c2.metric("📅 Days Completed", prog["done_days"],
              f"of {prog['total_days']} total")
    total_focus = round(sum(s["minutes"] for s in timers) / 60, 1)
    c3.metric("⏱ Focus Hours",  f"{total_focus}h", "logged")
    quiz_acc = round(
        sum(1 for s in scores if s["correct"]) / len(scores) * 100
    ) if scores else 0
    c4.metric("🧠 Quiz Score",   f"{quiz_acc}%",  f"{len(scores)} answered")

    st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)

    # ── Progress bar ─────────────────────────────────────────────
    st.progress(prog["pct"] / 100,
                text=f"Overall completion: {prog['pct']}%  "
                     f"({prog['done']} of {prog['total']} sessions)")

    st.markdown("---")

    # ── ROW 1: Activity charts + Plan tracker ────────────────────
    col_charts, col_tracker = st.columns([3, 2], gap="medium")

    with col_charts:
        st.markdown("### 📊 Study Activity")

        tab_bar, tab_spark, tab_heat = st.tabs(
            ["📊 Daily Hours", "📈 Progress Trend", "🔥 Heatmap"])

        with tab_bar:
            st.plotly_chart(charts.activity_bar(timers),
                            use_container_width=True,
                            config={"displayModeBar": False})

        with tab_spark:
            st.plotly_chart(
                charts.progress_line(prog["pct"],
                                     len(plan.get("weeks", []))),
                use_container_width=True,
                config={"displayModeBar": False})

        with tab_heat:
            st.plotly_chart(charts.heatmap_chart(timers),
                            use_container_width=True,
                            config={"displayModeBar": False})

    with col_tracker:
        st.markdown("### 📋 Plan Tracker")

        # Plan info card
        st.markdown(f"""
<div style="background:#fff;border:1.5px solid #c4b5fd;border-radius:14px;
padding:14px 16px;margin-bottom:14px;
box-shadow:0 2px 10px rgba(124,106,247,.08)">
  <div style="font-size:15px;font-weight:700;color:#4c1d95;margin-bottom:3px">
    {plan.get('title', '')}
  </div>
  <div style="font-size:11px;color:#9ca3af">
    {plan.get('difficulty','').title()} level &nbsp;·&nbsp;
    {len(plan.get('weeks', []))} weeks &nbsp;·&nbsp;
    {plan.get('hoursPerDay', 2)}h/day
  </div>
  <div style="font-size:11px;color:#7c3aed;margin-top:4px">
    Generated: {helpers.fmt_dt(gen_at)}
  </div>
</div>
""", unsafe_allow_html=True)

        # Week progress bars
        st.markdown("""<div style="font-size:11px;color:#7c3aed;font-weight:700;
text-transform:uppercase;letter-spacing:.5px;margin-bottom:8px">
Week-by-Week Progress</div>""", unsafe_allow_html=True)

        for wi, week in enumerate(plan.get("weeks", [])[:8]):
            wp = helpers.week_progress(plan, comp, wi)
            bar_color = ("#4ade80" if wp == 100
                         else "#7c6af7" if wp > 0 else "#ddd6fe")
            st.markdown(f"""
<div style="margin-bottom:7px">
  <div style="display:flex;justify-content:space-between;
  font-size:11px;margin-bottom:3px">
    <span style="color:#4c1d95;font-weight:600">
      Wk {week['weekNum']}: {week.get('title','')[:20]}
    </span>
    <span style="color:{'#16a34a' if wp==100 else '#7c3aed'};font-weight:700">
      {wp}%{'  ✓' if wp==100 else ''}
    </span>
  </div>
  <div style="height:7px;background:#ede9fe;border-radius:4px;overflow:hidden">
    <div style="height:100%;width:{wp}%;background:{bar_color};
    border-radius:4px;transition:width .5s ease"></div>
  </div>
</div>
""", unsafe_allow_html=True)

        # Milestones
        if plan.get("milestones"):
            st.markdown("""<div style="font-size:11px;color:#7c3aed;font-weight:700;
text-transform:uppercase;letter-spacing:.5px;margin:12px 0 7px">
🏁 Milestones</div>""", unsafe_allow_html=True)
            for i, m in enumerate(plan["milestones"]):
                done_icon = "✅" if i < max(1, prog["pct"] // 33) else "⭕"
                st.markdown(
                    f"<div style='font-size:12px;color:#4c1d95;"
                    f"margin-bottom:4px'>{done_icon} {m}</div>",
                    unsafe_allow_html=True)

    st.markdown("---")

    # ── ROW 2: Performance + Activity feed ───────────────────────
    col_perf, col_feed = st.columns(2, gap="medium")

    with col_perf:
        st.markdown("### 🎯 Performance Metrics")

        tab_radar, tab_donut = st.tabs(["📡 Skills Radar", "🍩 Sessions"])

        with tab_radar:
            st.plotly_chart(charts.radar_chart(perf),
                            use_container_width=True,
                            config={"displayModeBar": False})

            # Skill breakdown
            skill_colors = {
                "Consistency": "#7c6af7",
                "Completion":  "#a78bfa",
                "Speed":       "#86efac",
                "Retention":   "#93c5fd",
                "Focus":       "#fca5a5",
            }
            for skill, val in perf.items():
                color = skill_colors.get(skill, "#c4b5fd")
                st.markdown(f"""
<div style="display:flex;align-items:center;gap:10px;margin-bottom:6px">
  <div style="width:80px;font-size:11px;color:#4c1d95;font-weight:600">{skill}</div>
  <div style="flex:1;height:8px;background:#ede9fe;border-radius:4px;overflow:hidden">
    <div style="height:100%;width:{val}%;background:{color};border-radius:4px"></div>
  </div>
  <div style="width:32px;font-size:11px;color:#7c3aed;text-align:right;font-weight:700">{val}</div>
</div>
""", unsafe_allow_html=True)

        with tab_donut:
            st.plotly_chart(charts.type_donut(plan, comp),
                            use_container_width=True,
                            config={"displayModeBar": False})
            if scores:
                st.plotly_chart(charts.quiz_line(scores),
                                use_container_width=True,
                                config={"displayModeBar": False})

    with col_feed:
        st.markdown("### 🕐 Activity Feed")

        # Plan generated callout
        if gen_at:
            st.markdown(f"""
<div style="background:linear-gradient(135deg,#ede9fe,#faf8ff);
border:1.5px solid #c4b5fd;border-radius:14px;padding:14px 16px;
margin-bottom:14px;box-shadow:0 2px 8px rgba(124,106,247,.1)">
  <div style="font-size:10px;color:#7c3aed;font-weight:700;
  text-transform:uppercase;letter-spacing:.5px;margin-bottom:5px">
    📋 Plan Generated
  </div>
  <div style="font-size:13px;font-weight:700;color:#4c1d95">
    {plan.get('title', '')}
  </div>
  <div style="font-size:12px;color:#7c3aed;margin-top:2px">
    {helpers.fmt_dt(gen_at)}
  </div>
  <div style="display:flex;gap:6px;flex-wrap:wrap;margin-top:8px">
    {''.join(
        f'<span style="font-size:11px;padding:3px 10px;border-radius:10px;'
        f'background:#fff;color:#7c3aed;border:1px solid #c4b5fd">{t}</span>'
        for t in [
            f"{len(plan.get('weeks',[]))} weeks",
            f"{plan.get('hoursPerDay',2)}h/day",
            plan.get('difficulty','').title(),
            plan.get('subject','')[:18],
        ]
    )}
  </div>
</div>
""", unsafe_allow_html=True)

        # Recent events
        events = []
        if gen_at:
            events.append(("✦", "Plan created", plan.get("title","")[:30],
                           helpers.rel_time(gen_at), "#7c6af7"))
        events.append(("🔑", "Signed in",
                        helpers.fmt_dt(user.get("login_at", "")),
                        helpers.rel_time(user.get("login_at", "")), "#60a5fa"))
        if prog["done"] > 0:
            events.append(("✅", f"{prog['done']} sessions completed",
                           f"{prog['done_days']} full study days",
                           "ongoing", "#4ade80"))
        if timers:
            last = timers[-1]
            events.append(("⏱", f"Focus: {last.get('task','Study')[:26]}",
                           f"{last['minutes']} min logged",
                           helpers.rel_time(last["ts"]), "#a78bfa"))
        if scores:
            lq = scores[-1]
            events.append(("📝", "Quiz answered",
                           "✓ Correct" if lq["correct"] else "✗ Incorrect",
                           helpers.rel_time(lq["ts"]),
                           "#4ade80" if lq["correct"] else "#f97316"))
        # Upcoming session
        if plan.get("weeks") and plan["weeks"][0].get("days"):
            next_day = next(
                (d for w in plan["weeks"] for d in w.get("days", [])
                 if not all(comp.get(f"{plan['weeks'].index(w)}_{d['dayNum']}_{si}")
                            for si in range(len(d.get("sessions",[])))) ),
                None)
            if next_day:
                events.append(("📅", f"Next: {next_day['title'][:30]}",
                               f"{len(next_day.get('sessions',[]))} sessions · "
                               f"{sum(s.get('duration',45) for s in next_day.get('sessions',[]))}m",
                               "upcoming", "#fbbf24"))

        for icon, title, sub, t, color in events[:7]:
            st.markdown(f"""
<div style="display:flex;align-items:flex-start;gap:10px;padding:9px 0;
border-bottom:1px solid #f0eeff">
  <div style="width:32px;height:32px;border-radius:9px;
  background:{color}22;display:flex;align-items:center;
  justify-content:center;font-size:15px;flex-shrink:0">{icon}</div>
  <div style="flex:1">
    <div style="font-size:13px;font-weight:600;color:#2d2150">{title}</div>
    <div style="font-size:11px;color:#9ca3af;margin-top:1px">{sub}</div>
  </div>
  <div style="font-size:11px;color:#c4b5fd;white-space:nowrap;margin-top:2px">{t}</div>
</div>
""", unsafe_allow_html=True)

        # Smart tip
        pct = prog["pct"]
        tip = ("Build consistency — study even 20 min every day."
               if perf["Consistency"] < 60
               else "Half-way there! Keep completing daily sessions."
               if pct < 50
               else "Excellent pace! Review completed topics regularly.")
        st.markdown(f"""
<div style="margin-top:14px;padding:12px 14px;
background:linear-gradient(135deg,#ede9fe,#faf8ff);
border-left:4px solid #7c6af7;border-radius:0 12px 12px 0;
font-size:13px;color:#4c1d95;line-height:1.6;font-weight:500">
  💡 {tip}
</div>
""", unsafe_allow_html=True)

    st.markdown("---")

    # ── ROW 3: Quick actions ─────────────────────────────────────
    st.markdown("### ⚡ Quick Actions")
    qa1, qa2, qa3, qa4 = st.columns(4)

    with qa1:
        st.markdown(_action_card("📋", "View My Plan",
                                 "See today's sessions"), unsafe_allow_html=True)
        if st.button("Open Plan →", use_container_width=True, key="qa_plan",
                     type="secondary"):
            st.session_state.page = "My Plan"; st.rerun()
    with qa2:
        st.markdown(_action_card("⏱", "Start Timer",
                                 "Focus with Pomodoro"), unsafe_allow_html=True)
        if st.button("Open Timer →", use_container_width=True, key="qa_timer",
                     type="secondary"):
            st.session_state.page = "Tools"; st.rerun()
    with qa3:
        st.markdown(_action_card("🧠", "Take a Quiz",
                                 "Test your knowledge"), unsafe_allow_html=True)
        if st.button("Open Quiz →", use_container_width=True, key="qa_quiz",
                     type="secondary"):
            st.session_state.page = "Tools"; st.rerun()
    with qa4:
        st.markdown(_action_card("📊", "View Analytics",
                                 "Track performance"), unsafe_allow_html=True)
        if st.button("Open Analytics →", use_container_width=True,
                     key="qa_analytics", type="secondary"):
            st.session_state.page = "Analytics"; st.rerun()


# ── Helpers ──────────────────────────────────────────────────────

def _action_card(icon, title, sub):
    return f"""
<div style="background:#fff;border:1.5px solid #ddd6fe;border-radius:14px;
padding:14px;margin-bottom:8px;text-align:center;
box-shadow:0 2px 8px rgba(124,106,247,.07)">
  <div style="font-size:24px;margin-bottom:6px">{icon}</div>
  <div style="font-size:13px;font-weight:700;color:#4c1d95">{title}</div>
  <div style="font-size:11px;color:#9ca3af;margin-top:2px">{sub}</div>
</div>"""

def _empty_card(col, icon, title, desc, btn_label, page_target):
    with col:
        st.markdown(f"""
<div style="background:#fff;border:1.5px solid #c4b5fd;border-radius:16px;
padding:24px 18px;text-align:center;margin-bottom:10px;
box-shadow:0 4px 16px rgba(124,106,247,.1)">
  <div style="font-size:36px;margin-bottom:10px">{icon}</div>
  <div style="font-size:15px;font-weight:700;color:#4c1d95;margin-bottom:6px">{title}</div>
  <div style="font-size:12px;color:#9ca3af;line-height:1.6">{desc}</div>
</div>
""", unsafe_allow_html=True)
        if st.button(btn_label, use_container_width=True,
                     key=f"empty_{page_target}"):
            st.session_state.page = page_target
            st.rerun()

def _check_reminders(email):
    from utils import storage
    reminders = storage.load_reminders(email)
    now = datetime.now()
    for r in reminders:
        if not r.get("active", True):
            continue
        try:
            t    = datetime.fromisoformat(r.get("next_trigger", "9999"))
            diff = abs((now - t).total_seconds())
            if diff <= 90:
                st.toast(
                    f"⏰ Reminder: {r.get('title', 'Time to study!')}",
                    icon="📚")
        except Exception:
            pass
