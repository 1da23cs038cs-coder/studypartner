# page_modules/my_plans_page.py  — All plans library with history
import streamlit as st
from datetime import datetime
from utils import storage, helpers


def render(user):
    email     = user["email"]
    all_plans = storage.load_all_plans(email)   # includes _pct, _done, _total

    st.markdown("## 📚 My Plans Library")
    st.markdown(
        "<p style='color:#9ca3af;font-size:13px;margin-top:-6px'>"
        "All your study plans — switch between them, view progress, or delete old ones."
        "</p>", unsafe_allow_html=True)

    if not all_plans:
        st.markdown("""
<div style="text-align:center;padding:60px 20px;background:#fff;
border:1.5px dashed #c4b5fd;border-radius:18px">
  <div style="font-size:48px;margin-bottom:12px">📋</div>
  <div style="font-size:16px;font-weight:700;color:#4c1d95;margin-bottom:6px">
    No plans yet
  </div>
  <div style="font-size:13px;color:#9ca3af">
    Go to ✦ New Plan to create your first study plan.
  </div>
</div>
""", unsafe_allow_html=True)
        if st.button("✦ Create First Plan", use_container_width=False):
            st.session_state.page = "New Plan"; st.rerun()
        return

    active_plan = storage.load_active_plan(email)
    active_id   = active_plan.get("plan_id", "") if active_plan else ""

    # ── Summary stats row ─────────────────────────────────────────
    total_plans    = len(all_plans)
    completed_plans = sum(1 for p in all_plans if p.get("_pct", 0) == 100)
    total_sessions = sum(p.get("_total", 0) for p in all_plans)
    done_sessions  = sum(p.get("_done", 0) for p in all_plans)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("📚 Total Plans",       total_plans)
    c2.metric("✅ Completed Plans",    completed_plans)
    c3.metric("📝 Total Sessions",    total_sessions)
    c4.metric("🎯 Sessions Done",     done_sessions)
    st.markdown("---")

    # ── Filter / sort ──────────────────────────────────────────────
    fc1, fc2 = st.columns([2, 1])
    with fc1:
        search = st.text_input("🔍 Search plans",
                               placeholder="Filter by subject or title...",
                               label_visibility="collapsed")
    with fc2:
        sort_by = st.selectbox("Sort by",
                               ["Newest first", "Oldest first",
                                "Most progress", "Least progress",
                                "A–Z"],
                               label_visibility="collapsed")

    # Apply filter
    plans = all_plans.copy()
    if search.strip():
        q = search.strip().lower()
        plans = [p for p in plans if
                 q in p.get("title", "").lower() or
                 q in p.get("subject", "").lower()]

    # Apply sort
    if sort_by == "Newest first":
        plans = sorted(plans, key=lambda p: p.get("saved_at", ""), reverse=True)
    elif sort_by == "Oldest first":
        plans = sorted(plans, key=lambda p: p.get("saved_at", ""))
    elif sort_by == "Most progress":
        plans = sorted(plans, key=lambda p: p.get("_pct", 0), reverse=True)
    elif sort_by == "Least progress":
        plans = sorted(plans, key=lambda p: p.get("_pct", 0))
    elif sort_by == "A–Z":
        plans = sorted(plans, key=lambda p: p.get("title", "").lower())

    if not plans:
        st.info("No plans match your search.")
        return

    # ── Plan cards ────────────────────────────────────────────────
    for p in plans:
        pid        = p.get("plan_id", "")
        pct        = p.get("_pct", 0)
        done       = p.get("_done", 0)
        total      = p.get("_total", 0)
        is_active  = pid == active_id
        saved      = p.get("saved_at", "")[:10]
        subject    = p.get("subject", "")
        difficulty = p.get("difficulty", "").title()
        weeks      = len(p.get("weeks", []))
        hpd        = p.get("hoursPerDay", 2)

        # Status badge
        if pct == 100:
            status_bg, status_color, status_label = "#dcfce7","#16a34a","✅ Completed"
        elif pct > 0:
            status_bg, status_color, status_label = "#ede9fe","#7c3aed","📖 In Progress"
        else:
            status_bg, status_color, status_label = "#f3f4f6","#6b7280","📋 Not Started"

        active_badge = (
            '<span style="font-size:10px;padding:2px 9px;border-radius:10px;'
            'background:linear-gradient(135deg,#7c6af7,#a78bfa);color:#fff;'
            'font-weight:700;margin-left:8px">ACTIVE</span>'
            if is_active else ""
        )

        bar_color = "#4ade80" if pct == 100 else "#7c6af7" if pct > 0 else "#ddd6fe"

        st.markdown(f"""
<div style="background:#fff;border:{'2px solid #7c6af7' if is_active else '1px solid #ddd6fe'};
border-radius:16px;padding:18px 20px;margin-bottom:14px;
box-shadow:{'0 4px 20px rgba(124,106,247,.15)' if is_active else '0 2px 8px rgba(124,106,247,.06)'}">

  <div style="display:flex;align-items:flex-start;
  justify-content:space-between;flex-wrap:wrap;gap:8px;margin-bottom:12px">
    <div style="flex:1">
      <div style="font-size:16px;font-weight:700;color:#2d2150;display:flex;
      align-items:center;flex-wrap:wrap">
        {p.get('title', 'Study Plan')}{active_badge}
      </div>
      <div style="font-size:12px;color:#9ca3af;margin-top:3px">
        📚 {subject} &nbsp;·&nbsp; 🎯 {difficulty}
        &nbsp;·&nbsp; 📅 {weeks} weeks &nbsp;·&nbsp; ⏱ {hpd}h/day
        &nbsp;·&nbsp; Created {saved}
      </div>
    </div>
    <span style="font-size:11px;padding:4px 12px;border-radius:10px;
    background:{status_bg};color:{status_color};font-weight:700;
    border:1px solid {status_color}40;white-space:nowrap">
      {status_label}
    </span>
  </div>

  <div style="display:flex;align-items:center;gap:10px;margin-bottom:10px">
    <div style="flex:1;height:8px;background:#ede9fe;border-radius:4px;overflow:hidden">
      <div style="height:100%;width:{pct}%;background:{bar_color};
      border-radius:4px"></div>
    </div>
    <div style="font-size:13px;font-weight:700;color:#4c1d95;min-width:38px">
      {pct}%
    </div>
  </div>
  <div style="font-size:11px;color:#9ca3af">
    {done} of {total} sessions completed
  </div>
</div>
""", unsafe_allow_html=True)

        # Action buttons
        btn_cols = st.columns([2, 2, 2, 1])
        with btn_cols[0]:
            if not is_active:
                if st.button(f"▶ Switch to this plan",
                             key=f"switch_{pid}",
                             use_container_width=True):
                    storage.set_active_plan(email, pid)
                    st.session_state.page = "My Plan"
                    st.toast(f"Switched to: {p.get('title','')}", icon="📋")
                    st.rerun()
            else:
                if st.button("📋 View Plan",
                             key=f"view_{pid}",
                             use_container_width=True):
                    st.session_state.page = "My Plan"; st.rerun()

        with btn_cols[1]:
            if st.button("📊 Analytics",
                         key=f"analytics_{pid}",
                         use_container_width=True,
                         type="secondary"):
                storage.set_active_plan(email, pid)
                st.session_state.page = "Analytics"; st.rerun()

        with btn_cols[2]:
            if st.button("⬇ Export",
                         key=f"export_{pid}",
                         use_container_width=True,
                         type="secondary"):
                txt = _export_plan(p)
                st.download_button(
                    "💾 Download .txt",
                    txt,
                    file_name=f"{p.get('subject','plan').replace(' ','_')}.txt",
                    mime="text/plain",
                    key=f"dl_{pid}",
                    use_container_width=True,
                )

        with btn_cols[3]:
            if not is_active:
                if st.button("🗑", key=f"del_{pid}",
                             use_container_width=True,
                             type="secondary",
                             help="Delete this plan"):
                    storage.delete_plan(email, pid)
                    st.toast("Plan deleted.", icon="🗑")
                    st.rerun()


def _export_plan(plan):
    lines = [
        f"STUDY PLAN: {plan.get('title','')}",
        f"Subject: {plan.get('subject','')}",
        f"Difficulty: {plan.get('difficulty','')}",
        f"Created: {plan.get('saved_at','')[:10]}",
        f"Progress: {plan.get('_pct',0)}%",
        "",
    ]
    if plan.get("milestones"):
        lines += ["=== MILESTONES ==="] + [f"  • {m}" for m in plan["milestones"]] + [""]
    for w in plan.get("weeks", []):
        lines.append(f"\n=== WEEK {w['weekNum']}: {w.get('title','')} ===")
        if w.get("goals"):
            lines.append("Goals: " + ", ".join(w["goals"]))
        for d in w.get("days", []):
            lines.append(f"\n  Day {d['dayNum']}: {d['title']}")
            for s in d.get("sessions", []):
                lines.append(
                    f"    [{s.get('duration',45)}m] {s['topic']}"
                    f" ({s.get('type','')}) — {s.get('difficulty','')}")
    return "\n".join(lines)
