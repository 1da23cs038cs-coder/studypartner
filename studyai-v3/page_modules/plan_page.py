# page_modules/plan_page.py
import streamlit as st
from utils import storage, helpers
from utils.planner import STUDY_TIPS
import random

def render(user):
    email = user["email"]
    all_plans = storage.load_all_plans(email)

    if not all_plans:
        st.info("📋 No plans yet. Go to **New Plan** to create one.")
        return

    # ── Plan selector ────────────────────────────────────────────
    if len(all_plans) > 1:
        plan_labels = [f"{p.get('title','')} ({p.get('saved_at','')[:10]})" for p in all_plans]
        active_plan = storage.load_active_plan(email)
        default_idx = next((i for i,p in enumerate(all_plans) if p.get("plan_id")==active_plan.get("plan_id","")),len(all_plans)-1)
        sel_idx = st.selectbox("📋 Select plan", range(len(all_plans)), format_func=lambda i:plan_labels[i], index=default_idx)
        if all_plans[sel_idx].get("plan_id") != active_plan.get("plan_id",""):
            if st.button("Switch to this plan"):
                storage.set_active_plan(email, all_plans[sel_idx]["plan_id"]); st.rerun()

    plan = storage.load_active_plan(email)
    if not plan: st.info("No active plan."); return

    comp   = storage.load_completed(email)
    missed = storage.load_missed(email)
    prog   = helpers.get_progress(plan,comp)
    pid    = plan.get("plan_id","default")

    # Header
    ch,cb = st.columns([3,1])
    with ch:
        st.markdown(f"## 📋 {plan.get('title','Study Plan')}")
        st.markdown(f"<p style='color:#9ca3af;font-size:13px;margin-top:-6px'>{plan.get('description','')}</p>",unsafe_allow_html=True)
    with cb:
        txt=_export(plan)
        st.download_button("⬇ Download",txt,file_name="study-plan.txt",mime="text/plain",use_container_width=True)

    c1,c2,c3,c4=st.columns(4)
    c1.metric("Progress",f"{prog['pct']}%"); c2.metric("Days",f"{prog['done_days']}/{prog['total_days']}")
    c3.metric("Sessions",f"{prog['done']}/{prog['total']}"); c4.metric("Hours",f"{round(prog['done_days']*plan.get('hoursPerDay',2))}h")
    st.progress(prog["pct"]/100)

    if missed:
        cw,cr=st.columns([4,1])
        cw.warning(f"⚠️ **{len(missed)} missed day(s).** Reschedule to catch up.")
        if cr.button("Reschedule"): storage.reschedule(email); st.success("Rescheduled!"); st.rerun()

    if plan.get("milestones"):
        with st.expander("🏁 Milestones",expanded=False):
            for m in plan["milestones"]: st.markdown(f"- {m}")

    st.markdown("---")

    weeks=plan.get("weeks",[])
    wlabels=[f"Week {w['weekNum']}: {w.get('title','')} ({helpers.week_progress(plan,comp,i)}%)" for i,w in enumerate(weeks)]
    sel=st.selectbox("Select week",range(len(weeks)),format_func=lambda i:wlabels[i])
    week=weeks[sel]

    if week.get("goals"):
        with st.expander(f"🎯 Week {week['weekNum']} Goals",expanded=True):
            for g in week["goals"]: st.markdown(f"- {g}")

    for di,day in enumerate(week.get("days",[])):
        pfx=f"{sel}_{day['dayNum']}"
        all_done=bool(day["sessions"]) and all(comp.get(f"{pfx}_{si}") for si in range(len(day["sessions"])))
        is_missed=pfx in missed
        is_buf=day.get("isBuffer",False)
        total_m=sum(s.get("duration",45) for s in day.get("sessions",[]))
        badge="🔄 Buffer" if is_buf else "✅ Done" if all_done else "⚠️ Missed" if is_missed else "📌 Pending"

        # Popup toast when all sessions marked done
        prev_done = st.session_state.get(f"prev_done_{pfx}", False)
        if all_done and not prev_done:
            st.toast(f"🎉 Day {day['dayNum']} complete! Great work!", icon="🌟")
        st.session_state[f"prev_done_{pfx}"] = all_done

        with st.expander(f"**Day {day['dayNum']}** — {day['title']}  ·  {badge}  ·  {total_m}m",expanded=(di==0 and sel==0)):
            for si,s in enumerate(day.get("sessions",[])):
                key=f"{pfx}_{si}"; done=comp.get(key,False)
                ca,cb2,cc=st.columns([0.5,8,1.5])
                with ca:
                    nv=st.checkbox("",value=done,key=f"ck_{key}",label_visibility="collapsed")
                    if nv!=done: storage.toggle_session(email,key); st.rerun()
                with cb2:
                    strike="~~" if done else ""
                    st.markdown(
                        f"{strike}{helpers.type_icon(s.get('type','lecture'))} **{s['topic']}** {helpers.diff_icon(s.get('difficulty','easy'))}{strike}\n\n"
                        f"<span style='font-size:11px;color:#9ca3af'>{s.get('type','').title()} · {s.get('notes','')}</span>",
                        unsafe_allow_html=True)
                with cc:
                    st.markdown(f"<span style='font-size:12px;color:#9ca3af'>{s.get('duration',45)}m</span>",unsafe_allow_html=True)

            # Notes section
            st.markdown("<div style='margin-top:10px;font-size:12px;color:#7c3aed;font-weight:600'>📝 Day Notes</div>",unsafe_allow_html=True)
            note_key=f"note_{pfx}"
            existing_note=storage.load_note(email,pid,pfx)
            note_val=st.text_area("Add your notes, key points, questions...",
                value=existing_note,key=note_key,height=80,label_visibility="collapsed",
                placeholder=f"Notes for {day['title']}... key concepts, questions, links")
            if note_val!=existing_note:
                storage.save_note(email,pid,pfx,note_val)

            # Random tip
            tip=random.choice(STUDY_TIPS)
            st.markdown(f"<div style='font-size:11px;color:#a78bfa;padding:6px 10px;background:#ede9fe;border-radius:8px;margin-top:8px'>💡 Tip: {tip}</div>",unsafe_allow_html=True)

            b1,b2,b3=st.columns(3)
            if b1.button("✅ All done",key=f"ad_{pfx}",use_container_width=True):
                storage.mark_day(email,sel,day["dayNum"],len(day["sessions"]),True); st.rerun()
            if not is_missed:
                if b2.button("⚠️ Missed",key=f"ms_{pfx}",use_container_width=True):
                    storage.mark_day(email,sel,day["dayNum"],len(day["sessions"]),False); st.rerun()
            if b3.button("▶ Timer",key=f"tm_{pfx}",use_container_width=True):
                st.session_state.timer_task=day["title"]; st.session_state.page="Tools"; st.rerun()

def _export(plan):
    lines=[f"STUDY PLAN: {plan.get('title','')}\nGenerated: {plan.get('generatedAt','')}\n"]
    if plan.get("milestones"):
        lines+=["=== MILESTONES ==="]+[f"  • {m}" for m in plan["milestones"]]+[""]
    for w in plan.get("weeks",[]):
        lines.append(f"\n=== WEEK {w['weekNum']}: {w.get('title','')} ===")
        if w.get("goals"): lines.append("Goals: "+", ".join(w["goals"]))
        for d in w.get("days",[]):
            lines.append(f"\n  Day {d['dayNum']}: {d['title']}")
            for s in d.get("sessions",[]):
                lines.append(f"    [{s.get('duration',45)}m] {s['topic']} ({s.get('type','')}) — {s.get('difficulty','')}")
                if s.get("notes"): lines.append(f"    Tip: {s['notes']}")
    return "\n".join(lines)
