# page_modules/quiz_page.py  — Full quiz system: AI-generated + custom user quizzes
import streamlit as st
import random
from datetime import datetime
from utils import storage
from utils.planner import get_quiz_question, QUIZ_BANK


# ══════════════════════════════════════════════════════════════════
def render(user):
    email = user["email"]
    plan  = storage.load_active_plan(email)

    st.markdown("## 🧠 Quiz Center")
    st.markdown(
        "<p style='color:#9ca3af;font-size:13px;margin-top:-6px'>"
        "Take AI-generated quizzes based on your topics, or create and save your own quiz banks."
        "</p>", unsafe_allow_html=True)

    tab_ai, tab_custom, tab_library, tab_scores = st.tabs([
        "🤖 AI Quiz",
        "✏️ Create Quiz",
        "📚 My Quiz Library",
        "📊 Score History",
    ])

    # ── TAB 1: AI-generated quiz ──────────────────────────────────
    with tab_ai:
        _ai_quiz_tab(email, plan)

    # ── TAB 2: Create custom quiz ─────────────────────────────────
    with tab_custom:
        _create_quiz_tab(email, plan)

    # ── TAB 3: Library — take saved quizzes ───────────────────────
    with tab_library:
        _library_tab(email)

    # ── TAB 4: Score history ──────────────────────────────────────
    with tab_scores:
        _scores_tab(email)


# ══════════════════════════════════════════════════════════════════
# TAB 1 — AI Quiz
# ══════════════════════════════════════════════════════════════════

def _ai_quiz_tab(email, plan):
    st.markdown("### 🤖 AI-Generated Quiz")
    st.caption("Questions generated from your completed topics or any subject you choose.")

    col_q, col_s = st.columns([2, 1], gap="medium")

    with col_q:
        # Topic source selector
        source = st.radio(
            "Generate questions about:",
            ["My completed topics", "Specific topic I choose",
             "Study skills & strategies"],
            horizontal=True,
        )

        custom_topic = ""
        if source == "Specific topic I choose":
            custom_topic = st.text_input(
                "Enter topic", placeholder="e.g. Photosynthesis, World War 2, Python loops...")

        num_q = st.select_slider(
            "Number of questions",
            options=[1, 3, 5, 10],
            value=5,
        )

        if st.button("⚡ Generate Quiz Now", use_container_width=True):
            # Build topic list
            topics = []
            if source == "My completed topics" and plan:
                comp = storage.load_completed(email)
                for wi, week in enumerate(plan.get("weeks", [])):
                    for day in week.get("days", []):
                        for si, s in enumerate(day.get("sessions", [])):
                            if (comp.get(f"{wi}_{day['dayNum']}_{si}")
                                    and s.get("type") != "buffer"):
                                topics.append(s["topic"])
                if not topics:
                    # fallback: all topics from plan
                    for week in plan.get("weeks", []):
                        for day in week.get("days", []):
                            for s in day.get("sessions", []):
                                if s.get("type") != "buffer":
                                    topics.append(s["topic"])
            elif source == "Specific topic I choose" and custom_topic.strip():
                topics = [custom_topic.strip()] * 5
            else:
                # study skills
                topics = []

            subj = (custom_topic if custom_topic
                    else plan.get("subject", "general knowledge") if plan
                    else "general knowledge")

            questions = []
            with st.spinner(f"Generating {num_q} question(s)…"):
                for _ in range(num_q):
                    q = get_quiz_question(subj, topics)
                    # make each unique by shuffling topic
                    if topics: random.shuffle(topics)
                    questions.append(q)

            st.session_state["ai_quiz_questions"] = questions
            st.session_state["ai_quiz_answers"]   = [None] * len(questions)
            st.session_state["ai_quiz_submitted"]  = False
            st.rerun()

        # ── Show questions ─────────────────────────────────────────
        if "ai_quiz_questions" in st.session_state and st.session_state["ai_quiz_questions"]:
            questions  = st.session_state["ai_quiz_questions"]
            answers    = st.session_state.get("ai_quiz_answers", [None]*len(questions))
            submitted  = st.session_state.get("ai_quiz_submitted", False)

            st.markdown("---")
            st.markdown(f"**{len(questions)} question(s)** — select your answers then click Submit.")

            for qi, q in enumerate(questions):
                sel = answers[qi]
                st.markdown(f"""
<div style="background:#fff;border:1.5px solid #c4b5fd;border-radius:14px;
padding:16px 18px;margin:12px 0;
box-shadow:0 2px 8px rgba(124,106,247,.08)">
  <div style="font-size:14px;font-weight:600;color:#2d2150;margin-bottom:12px">
    Q{qi+1}. {q['question']}
  </div>
</div>
""", unsafe_allow_html=True)

                for oi, opt in enumerate(q["options"]):
                    is_correct = submitted and oi == q["answer"]
                    is_wrong   = submitted and oi == sel and oi != q["answer"]
                    is_sel     = (sel == oi)

                    bg     = ("#dcfce7" if is_correct else
                              "#fee2e2" if is_wrong else
                              "#ede9fe" if (is_sel and not submitted) else "#faf8ff")
                    border = ("#4ade80" if is_correct else
                              "#f87171" if is_wrong else
                              "#7c6af7" if (is_sel and not submitted) else "#ddd6fe")
                    color  = ("#166534" if is_correct else
                              "#991b1b" if is_wrong else
                              "#4c1d95" if is_sel else "#6b7280")

                    st.markdown(f"""
<div style="padding:10px 14px;border:1.5px solid {border};
border-radius:10px;background:{bg};color:{color};
font-size:13px;font-weight:500;margin-bottom:6px">{opt}</div>
""", unsafe_allow_html=True)

                    if not submitted:
                        if st.button(f"Select", key=f"ai_opt_{qi}_{oi}",
                                     use_container_width=True,
                                     type="secondary"):
                            st.session_state["ai_quiz_answers"][qi] = oi
                            st.rerun()

                if submitted and q.get("explanation"):
                    ok = sel == q["answer"]
                    st.markdown(f"""
<div style="padding:10px 14px;border-radius:9px;font-size:12px;line-height:1.6;
background:{'#dcfce7' if ok else '#fee2e2'};
color:{'#166534' if ok else '#991b1b'};margin-bottom:4px">
  {'✅' if ok else '❌'} {q['explanation']}
</div>
""", unsafe_allow_html=True)

            # Submit button
            if not submitted:
                answered_count = sum(1 for a in answers if a is not None)
                st.markdown(
                    f"<div style='font-size:12px;color:#9ca3af;margin-top:6px'>"
                    f"{answered_count}/{len(questions)} answered</div>",
                    unsafe_allow_html=True)
                if st.button("✅ Submit Quiz", use_container_width=True,
                             disabled=answered_count == 0):
                    st.session_state["ai_quiz_submitted"] = True
                    # save scores
                    score = 0
                    for qi, q in enumerate(questions):
                        correct = (answers[qi] == q["answer"])
                        if correct: score += 1
                        storage.save_quiz_score(
                            email, correct,
                            topic=q.get("question", "")[:40])
                    pct = round(score / len(questions) * 100)
                    st.toast(
                        f"{'🎉 ' if pct >= 70 else '📖 '}Score: {score}/{len(questions)} ({pct}%)",
                        icon="🧠")
                    st.rerun()
            else:
                score = sum(1 for qi, q in enumerate(questions)
                            if answers[qi] == q["answer"])
                pct   = round(score / len(questions) * 100)
                color = "#16a34a" if pct >= 70 else "#d97706" if pct >= 40 else "#dc2626"
                st.markdown(f"""
<div style="background:linear-gradient(135deg,#ede9fe,#faf8ff);
border:2px solid #7c6af7;border-radius:16px;padding:18px;
text-align:center;margin-top:12px">
  <div style="font-size:32px;font-weight:700;color:{color}">{pct}%</div>
  <div style="font-size:14px;font-weight:600;color:#4c1d95;margin-top:4px">
    {score} / {len(questions)} correct
  </div>
  <div style="font-size:12px;color:#9ca3af;margin-top:3px">
    {'Excellent! 🎉' if pct>=80 else 'Good job! 👍' if pct>=60 else 'Keep practising! 📖'}
  </div>
</div>
""", unsafe_allow_html=True)
                if st.button("🔄 New Quiz", use_container_width=True):
                    for k in ["ai_quiz_questions","ai_quiz_answers","ai_quiz_submitted"]:
                        st.session_state.pop(k, None)
                    st.rerun()

    with col_s:
        _quiz_stats_sidebar(email)


# ══════════════════════════════════════════════════════════════════
# TAB 2 — Create Custom Quiz
# ══════════════════════════════════════════════════════════════════

def _create_quiz_tab(email, plan):
    st.markdown("### ✏️ Create Your Own Quiz")
    st.caption("Build a question bank from your notes — save it and take it any time.")

    # Quiz title & subject
    qc1, qc2 = st.columns(2)
    with qc1:
        quiz_title = st.text_input("Quiz title *",
                                   placeholder="e.g. Chapter 3 — Forces & Motion",
                                   key="cq_title")
    with qc2:
        quiz_subject = st.text_input("Subject / Topic",
                                     placeholder="e.g. Physics",
                                     key="cq_subject")

    # Question builder
    st.markdown("#### ➕ Add Questions")
    st.caption("Add as many questions as you like, then click Save Quiz.")

    if "cq_questions" not in st.session_state:
        st.session_state["cq_questions"] = []

    # Add question form
    with st.expander("➕ Add a new question", expanded=True):
        q_text = st.text_area("Question *", key="cq_q",
                              placeholder="Type your question here...",
                              height=80)
        o1, o2 = st.columns(2)
        with o1:
            opt_a = st.text_input("Option A *", key="cq_a", placeholder="First option")
            opt_c = st.text_input("Option C",   key="cq_c", placeholder="Third option")
        with o2:
            opt_b = st.text_input("Option B *", key="cq_b", placeholder="Second option")
            opt_d = st.text_input("Option D",   key="cq_d", placeholder="Fourth option")

        opts_filled = [o for o in [opt_a, opt_b, opt_c, opt_d] if o.strip()]
        correct_opt = st.selectbox(
            "Correct answer *",
            options=opts_filled if opts_filled else ["—"],
            key="cq_correct",
        )
        explanation = st.text_input("Explanation (optional)",
                                    key="cq_exp",
                                    placeholder="Why is this correct?")

        if st.button("➕ Add Question", use_container_width=True):
            if not q_text.strip():
                st.error("Please enter the question text.")
            elif len(opts_filled) < 2:
                st.error("Please add at least 2 options.")
            elif correct_opt == "—" or correct_opt not in opts_filled:
                st.error("Please select the correct answer.")
            else:
                options = [o.strip() for o in opts_filled]
                answer_idx = options.index(correct_opt.strip())
                st.session_state["cq_questions"].append({
                    "question":    q_text.strip(),
                    "options":     options,
                    "answer":      answer_idx,
                    "explanation": explanation.strip(),
                })
                # clear fields via rerun
                for k in ["cq_q","cq_a","cq_b","cq_c","cq_d","cq_exp"]:
                    st.session_state.pop(k, None)
                st.toast(f"Question {len(st.session_state['cq_questions'])} added!", icon="✅")
                st.rerun()

    # Show current questions
    qs = st.session_state.get("cq_questions", [])
    if qs:
        st.markdown(f"**{len(qs)} question(s) ready:**")
        for i, q in enumerate(qs):
            with st.expander(f"Q{i+1}: {q['question'][:60]}...", expanded=False):
                for j, opt in enumerate(q["options"]):
                    icon = "✅" if j == q["answer"] else "○"
                    st.markdown(f"{icon} {opt}")
                if q.get("explanation"):
                    st.caption(f"Explanation: {q['explanation']}")
                if st.button(f"🗑 Remove Q{i+1}",
                             key=f"rm_q_{i}", type="secondary"):
                    st.session_state["cq_questions"].pop(i)
                    st.rerun()

        # Save quiz
        st.markdown("---")
        if st.button("💾 Save Quiz to Library", use_container_width=True,
                     type="primary"):
            if not quiz_title.strip():
                st.error("Please enter a quiz title.")
            else:
                quiz = {
                    "title":    quiz_title.strip(),
                    "subject":  quiz_subject.strip(),
                    "questions": qs,
                }
                storage.save_custom_quiz(email, quiz)
                st.session_state.pop("cq_questions", None)
                st.toast(f"Quiz '{quiz_title}' saved to library!", icon="📚")
                st.rerun()

        if st.button("🗑 Clear all questions", use_container_width=True,
                     type="secondary"):
            st.session_state.pop("cq_questions", None)
            st.rerun()
    else:
        st.info("No questions added yet. Use the form above to add questions.")


# ══════════════════════════════════════════════════════════════════
# TAB 3 — Library: take saved quizzes
# ══════════════════════════════════════════════════════════════════

def _library_tab(email):
    st.markdown("### 📚 My Quiz Library")

    quizzes = storage.load_custom_quizzes(email)

    if not quizzes:
        st.info("No custom quizzes yet. Go to **✏️ Create Quiz** to build your first one.")
        return

    # Active quiz session
    active_qid = st.session_state.get("taking_quiz_id")
    if active_qid:
        quiz = next((q for q in quizzes if q.get("quiz_id") == active_qid), None)
        if quiz:
            _take_quiz(email, quiz)
            return

    st.markdown(f"**{len(quizzes)} quiz(zes) saved**")

    for quiz in quizzes:
        qid      = quiz.get("quiz_id", "")
        n_q      = len(quiz.get("questions", []))
        attempts = quiz.get("attempts", 0)
        best     = quiz.get("best_score", 0)
        last_at  = quiz.get("last_attempted", "")

        st.markdown(f"""
<div style="background:#fff;border:1.5px solid #ddd6fe;border-radius:14px;
padding:16px 18px;margin-bottom:12px;
box-shadow:0 2px 8px rgba(124,106,247,.06)">
  <div style="display:flex;align-items:flex-start;
  justify-content:space-between;flex-wrap:wrap;gap:8px">
    <div>
      <div style="font-size:15px;font-weight:700;color:#2d2150">
        📝 {quiz.get('title','')}
      </div>
      <div style="font-size:12px;color:#9ca3af;margin-top:3px">
        {quiz.get('subject','')} &nbsp;·&nbsp;
        {n_q} question(s) &nbsp;·&nbsp;
        {attempts} attempt(s) &nbsp;·&nbsp;
        Best: {best}%
        {f' &nbsp;·&nbsp; Last: {last_at[:10]}' if last_at else ''}
      </div>
    </div>
    <div style="padding:6px 14px;background:#ede9fe;border-radius:20px;
    font-size:13px;font-weight:700;color:#7c3aed">
      Best {best}%
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

        b1, b2, b3 = st.columns([2, 2, 1])
        with b1:
            if st.button(f"▶ Take Quiz",
                         key=f"take_{qid}",
                         use_container_width=True):
                st.session_state["taking_quiz_id"]      = qid
                st.session_state["lib_quiz_answers"]     = [None] * n_q
                st.session_state["lib_quiz_submitted"]   = False
                st.rerun()
        with b2:
            if st.button(f"👁 Preview",
                         key=f"prev_{qid}",
                         use_container_width=True,
                         type="secondary"):
                with st.expander("Preview", expanded=True):
                    for i, q in enumerate(quiz.get("questions", [])):
                        st.markdown(f"**Q{i+1}.** {q['question']}")
                        for j, opt in enumerate(q["options"]):
                            st.markdown(
                                f"{'✅' if j==q['answer'] else '○'} {opt}")
                        if q.get("explanation"):
                            st.caption(q["explanation"])
                        st.markdown("---")
        with b3:
            if st.button("🗑", key=f"del_cq_{qid}",
                         type="secondary",
                         use_container_width=True,
                         help="Delete quiz"):
                storage.delete_custom_quiz(email, qid)
                st.toast("Quiz deleted.")
                st.rerun()


def _take_quiz(email, quiz):
    """Interactive quiz-taking UI for a saved custom quiz."""
    questions  = quiz.get("questions", [])
    answers    = st.session_state.get("lib_quiz_answers", [None]*len(questions))
    submitted  = st.session_state.get("lib_quiz_submitted", False)

    st.markdown(f"### 📝 {quiz.get('title','Quiz')}")
    st.caption(f"{len(questions)} questions · {quiz.get('subject','')}")

    if st.button("← Back to Library", type="secondary"):
        st.session_state.pop("taking_quiz_id", None)
        st.session_state.pop("lib_quiz_answers", None)
        st.session_state.pop("lib_quiz_submitted", None)
        st.rerun()

    st.markdown("---")

    for qi, q in enumerate(questions):
        sel = answers[qi]
        st.markdown(f"""
<div style="background:#fff;border:1.5px solid #c4b5fd;border-radius:14px;
padding:16px 18px;margin:10px 0;
box-shadow:0 2px 6px rgba(124,106,247,.07)">
  <div style="font-size:14px;font-weight:700;color:#2d2150;margin-bottom:10px">
    Q{qi+1}. {q['question']}
  </div>
</div>
""", unsafe_allow_html=True)

        for oi, opt in enumerate(q["options"]):
            is_correct = submitted and oi == q["answer"]
            is_wrong   = submitted and oi == sel and oi != q["answer"]
            is_sel     = (sel == oi)
            bg     = ("#dcfce7" if is_correct else "#fee2e2" if is_wrong else
                      "#ede9fe" if (is_sel and not submitted) else "#faf8ff")
            border = ("#4ade80" if is_correct else "#f87171" if is_wrong else
                      "#7c6af7" if (is_sel and not submitted) else "#ddd6fe")
            color  = ("#166534" if is_correct else "#991b1b" if is_wrong else
                      "#4c1d95" if is_sel else "#6b7280")

            st.markdown(f"""
<div style="padding:10px 14px;border:1.5px solid {border};
border-radius:10px;background:{bg};color:{color};
font-size:13px;font-weight:500;margin-bottom:6px">{opt}</div>
""", unsafe_allow_html=True)

            if not submitted:
                if st.button(f"Select", key=f"lib_opt_{qi}_{oi}",
                             use_container_width=True, type="secondary"):
                    st.session_state["lib_quiz_answers"][qi] = oi
                    st.rerun()

        if submitted and q.get("explanation"):
            ok = sel == q["answer"]
            st.markdown(f"""
<div style="padding:9px 14px;border-radius:8px;font-size:12px;
background:{'#dcfce7' if ok else '#fee2e2'};
color:{'#166534' if ok else '#991b1b'};margin-bottom:4px">
  {'✅' if ok else '❌'} {q['explanation']}
</div>
""", unsafe_allow_html=True)

    if not submitted:
        answered = sum(1 for a in answers if a is not None)
        st.caption(f"{answered}/{len(questions)} answered")
        if st.button("✅ Submit", use_container_width=True,
                     disabled=answered == 0):
            st.session_state["lib_quiz_submitted"] = True
            score = sum(1 for qi, q in enumerate(questions)
                        if answers[qi] == q["answer"])
            pct   = round(score / len(questions) * 100)
            storage.update_quiz_attempt(
                email, quiz["quiz_id"], pct)
            for qi, q in enumerate(questions):
                storage.save_quiz_score(
                    email,
                    answers[qi] == q["answer"],
                    quiz_id=quiz["quiz_id"],
                    topic=quiz.get("subject",""))
            st.toast(f"Score: {score}/{len(questions)} ({pct}%)", icon="🧠")
            st.rerun()
    else:
        score = sum(1 for qi, q in enumerate(questions)
                    if answers[qi] == q["answer"])
        pct   = round(score / len(questions) * 100)
        color = "#16a34a" if pct >= 70 else "#d97706" if pct >= 40 else "#dc2626"
        st.markdown(f"""
<div style="background:linear-gradient(135deg,#ede9fe,#faf8ff);
border:2px solid #7c6af7;border-radius:16px;padding:20px;text-align:center;margin-top:12px">
  <div style="font-size:36px;font-weight:700;color:{color}">{pct}%</div>
  <div style="font-size:14px;font-weight:600;color:#4c1d95;margin-top:6px">
    {score} / {len(questions)} correct
  </div>
  <div style="font-size:12px;color:#9ca3af;margin-top:4px">
    {'Excellent! 🎉' if pct>=80 else 'Good job! 👍' if pct>=60 else 'Keep practising! 📖'}
  </div>
</div>
""", unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔄 Retake", use_container_width=True):
                st.session_state["lib_quiz_answers"]   = [None]*len(questions)
                st.session_state["lib_quiz_submitted"] = False
                st.rerun()
        with col2:
            if st.button("← Library", use_container_width=True, type="secondary"):
                for k in ["taking_quiz_id","lib_quiz_answers","lib_quiz_submitted"]:
                    st.session_state.pop(k, None)
                st.rerun()


# ══════════════════════════════════════════════════════════════════
# TAB 4 — Score history
# ══════════════════════════════════════════════════════════════════

def _scores_tab(email):
    st.markdown("### 📊 Score History")
    scores = storage.load_quiz_scores(email)

    if not scores:
        st.info("No quiz scores yet. Take a quiz to see your history here.")
        return

    total   = len(scores)
    correct = sum(1 for s in scores if s["correct"])
    acc     = round(correct / total * 100) if total else 0
    recent  = scores[-10:]
    streak  = 0
    for s in reversed(scores):
        if s["correct"]: streak += 1
        else: break

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("📝 Total Questions", total)
    c2.metric("✅ Correct",          correct)
    c3.metric("🎯 Accuracy",        f"{acc}%")
    c4.metric("🔥 Current Streak",   streak)

    st.markdown("---")
    st.markdown("**Recent 10 answers:**")
    for i, s in enumerate(reversed(recent)):
        icon = "✅" if s["correct"] else "❌"
        topic_label = f" — {s['topic'][:40]}" if s.get("topic") else ""
        ts = s.get("ts","")[:16].replace("T"," ")
        st.markdown(
            f"<div style='font-size:13px;padding:6px 0;"
            f"border-bottom:1px solid #f0eeff;color:#4c1d95'>"
            f"{icon} {ts}{topic_label}</div>",
            unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════
# SHARED sidebar stats
# ══════════════════════════════════════════════════════════════════

def _quiz_stats_sidebar(email):
    scores    = storage.load_quiz_scores(email)
    custom_qs = storage.load_custom_quizzes(email)
    total     = len(scores)
    correct   = sum(1 for s in scores if s["correct"])
    acc       = round(correct / total * 100) if total else 0

    st.markdown(f"""
<div style="background:#fff;border:1.5px solid #ddd6fe;border-radius:14px;
padding:16px;box-shadow:0 2px 8px rgba(124,106,247,.07)">
  <div style="font-size:11px;color:#7c3aed;font-weight:700;
  text-transform:uppercase;letter-spacing:.5px;margin-bottom:12px">
    QUIZ STATS
  </div>
  <div style="margin-bottom:10px">
    <div style="font-size:26px;font-weight:700;color:#4c1d95">{total}</div>
    <div style="font-size:11px;color:#9ca3af">Questions answered</div>
  </div>
  <div style="margin-bottom:10px">
    <div style="font-size:26px;font-weight:700;
    color:{'#16a34a' if acc>=70 else '#d97706' if acc>=40 else '#dc2626'}">{acc}%</div>
    <div style="font-size:11px;color:#9ca3af">Accuracy</div>
  </div>
  <div style="margin-bottom:10px">
    <div style="font-size:26px;font-weight:700;color:#7c6af7">{correct}</div>
    <div style="font-size:11px;color:#9ca3af">Correct answers</div>
  </div>
  <div>
    <div style="font-size:26px;font-weight:700;color:#a78bfa">{len(custom_qs)}</div>
    <div style="font-size:11px;color:#9ca3af">Custom quizzes saved</div>
  </div>
</div>
""", unsafe_allow_html=True)

    # Progress bar for accuracy
    if total > 0:
        st.markdown("<div style='margin-top:10px;font-size:11px;color:#7c3aed;font-weight:600'>ACCURACY TREND</div>",
                    unsafe_allow_html=True)
        st.progress(acc / 100)
