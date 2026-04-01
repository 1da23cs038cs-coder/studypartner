# utils/storage.py  — Fixed: all plans + sessions preserved, custom quiz support
import json
from datetime import datetime
from pathlib import Path

_BASE    = Path(__file__).parent.parent / "data"
DATA_DIR = _BASE / "plans"

def _file(email):
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    safe = email.replace("@","_at_").replace(".","_")
    return DATA_DIR / f"{safe}.json"

def _load(email):
    f = _file(email)
    if not f.exists(): return {}
    try:    return json.loads(f.read_text(encoding="utf-8"))
    except: return {}

def _save(email, data):
    _file(email).write_text(
        json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

# ══════════════════════════════════════════════════════════════════
# PLANS  — multiple plans stored, fully isolated per plan_id
# ══════════════════════════════════════════════════════════════════

def save_plan(email, plan):
    d = _load(email)

    # ── Step 1: flush current active-plan's progress into its slot ──
    aid_old = d.get("active_plan_id", "")
    if aid_old:
        d[f"cs_{aid_old}"] = d.get("completed_sessions", {})
        d[f"md_{aid_old}"] = d.get("missed_days", [])

    # ── Step 2: register new plan ────────────────────────────────────
    plans = d.get("plans", [])
    plan["saved_at"] = datetime.now().isoformat()
    plan["plan_id"]  = f"plan_{len(plans)+1}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    plans.append(plan)

    pid = plan["plan_id"]
    d["plans"]             = plans
    d["active_plan_id"]    = pid
    d["plan_generated_at"] = plan["saved_at"]

    # ── Step 3: fresh empty progress for this new plan ───────────────
    d[f"cs_{pid}"] = {}
    d[f"md_{pid}"] = []
    d["completed_sessions"] = {}
    d["missed_days"]        = []

    _save(email, d)

def load_all_plans(email):
    """Return list of all plans with their individual progress stats."""
    d     = _load(email)
    plans = d.get("plans", [])
    result = []
    for p in plans:
        pid = p.get("plan_id", "")
        cs  = d.get(f"cs_{pid}", {})
        # calculate completion %
        total = done = 0
        for wi, week in enumerate(p.get("weeks", [])):
            for day in week.get("days", []):
                if day.get("isBuffer"): continue
                for si in range(len(day.get("sessions", []))):
                    total += 1
                    if cs.get(f"{wi}_{day['dayNum']}_{si}"): done += 1
        pct = round(done / total * 100) if total else 0
        result.append({**p, "_pct": pct, "_done": done, "_total": total})
    return result

def load_active_plan(email):
    d   = _load(email)
    aid = d.get("active_plan_id")
    if not aid:
        plans = d.get("plans", [])
        return plans[-1] if plans else None
    for p in d.get("plans", []):
        if p.get("plan_id") == aid:
            return p
    plans = d.get("plans", [])
    return plans[-1] if plans else None

def set_active_plan(email, plan_id):
    """Switch to a different plan — saves current progress first."""
    d = _load(email)

    # flush current plan's sessions
    aid_old = d.get("active_plan_id", "")
    if aid_old:
        d[f"cs_{aid_old}"] = d.get("completed_sessions", {})
        d[f"md_{aid_old}"] = d.get("missed_days", [])

    # load target plan's sessions
    d["active_plan_id"]     = plan_id
    d["completed_sessions"] = d.get(f"cs_{plan_id}", {})
    d["missed_days"]        = d.get(f"md_{plan_id}", [])
    _save(email, d)

def delete_plan(email, plan_id):
    d = _load(email)
    d["plans"] = [p for p in d.get("plans", []) if p.get("plan_id") != plan_id]
    # clean up progress keys
    d.pop(f"cs_{plan_id}", None)
    d.pop(f"md_{plan_id}", None)
    # if deleted the active plan, switch to latest
    if d.get("active_plan_id") == plan_id:
        remaining = d.get("plans", [])
        if remaining:
            new_aid = remaining[-1]["plan_id"]
            d["active_plan_id"]     = new_aid
            d["completed_sessions"] = d.get(f"cs_{new_aid}", {})
            d["missed_days"]        = d.get(f"md_{new_aid}", [])
        else:
            d["active_plan_id"]     = None
            d["completed_sessions"] = {}
            d["missed_days"]        = []
    _save(email, d)

def load_plan(email):          return load_active_plan(email)
def load_generated_at(email):  return _load(email).get("plan_generated_at")

# ══════════════════════════════════════════════════════════════════
# SESSION PROGRESS
# ══════════════════════════════════════════════════════════════════

def load_completed(email):  return _load(email).get("completed_sessions", {})
def load_missed(email):     return _load(email).get("missed_days", [])

def toggle_session(email, key):
    d  = _load(email)
    cs = d.get("completed_sessions", {})
    cs[key] = not cs.get(key, False)
    d["completed_sessions"] = cs
    aid = d.get("active_plan_id", "")
    if aid: d[f"cs_{aid}"] = cs
    _save(email, d)

def mark_day(email, wi, day_num, n_sessions, done):
    d   = _load(email)
    cs  = d.get("completed_sessions", {})
    md  = d.get("missed_days", [])
    pfx = f"{wi}_{day_num}"
    for si in range(n_sessions):
        cs[f"{pfx}_{si}"] = done
    if done and pfx in md:         md.remove(pfx)
    if not done and pfx not in md: md.append(pfx)
    d["completed_sessions"] = cs
    d["missed_days"]        = md
    aid = d.get("active_plan_id", "")
    if aid: d[f"cs_{aid}"] = cs; d[f"md_{aid}"] = md
    _save(email, d)

def reschedule(email):
    d   = _load(email)
    d["missed_days"] = []
    aid = d.get("active_plan_id", "")
    if aid: d[f"md_{aid}"] = []
    _save(email, d)

# ══════════════════════════════════════════════════════════════════
# CUSTOM QUIZZES  — user-created question banks
# ══════════════════════════════════════════════════════════════════

def save_custom_quiz(email, quiz):
    """Save a custom quiz created by the user."""
    d      = _load(email)
    quizzes = d.get("custom_quizzes", [])
    quiz["quiz_id"]    = f"cq_{len(quizzes)+1}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    quiz["created_at"] = datetime.now().isoformat()
    quiz["attempts"]   = 0
    quiz["best_score"] = 0
    quizzes.append(quiz)
    d["custom_quizzes"] = quizzes
    _save(email, d)
    return quiz["quiz_id"]

def load_custom_quizzes(email):
    return _load(email).get("custom_quizzes", [])

def delete_custom_quiz(email, quiz_id):
    d = _load(email)
    d["custom_quizzes"] = [q for q in d.get("custom_quizzes", [])
                           if q.get("quiz_id") != quiz_id]
    _save(email, d)

def update_quiz_attempt(email, quiz_id, score_pct):
    d = _load(email)
    for q in d.get("custom_quizzes", []):
        if q.get("quiz_id") == quiz_id:
            q["attempts"] = q.get("attempts", 0) + 1
            q["best_score"] = max(q.get("best_score", 0), score_pct)
            q["last_attempted"] = datetime.now().isoformat()
    _save(email, d)

# ══════════════════════════════════════════════════════════════════
# QUIZ SCORES  (per-question history)
# ══════════════════════════════════════════════════════════════════

def save_quiz_score(email, correct, quiz_id=None, topic=None):
    d = _load(email)
    s = d.get("quiz_scores", [])
    s.append({
        "correct":  correct,
        "quiz_id":  quiz_id,
        "topic":    topic,
        "ts":       datetime.now().isoformat(),
    })
    d["quiz_scores"] = s[-200:]
    _save(email, d)

def load_quiz_scores(email): return _load(email).get("quiz_scores", [])

# ══════════════════════════════════════════════════════════════════
# TIMER
# ══════════════════════════════════════════════════════════════════

def save_timer(email, minutes, task=""):
    d = _load(email)
    s = d.get("timer_sessions", [])
    s.append({"minutes": minutes, "task": task,
              "ts": datetime.now().isoformat()})
    d["timer_sessions"] = s[-200:]
    _save(email, d)

def load_timers(email): return _load(email).get("timer_sessions", [])

# ══════════════════════════════════════════════════════════════════
# REMINDERS
# ══════════════════════════════════════════════════════════════════

def save_reminder(email, reminder):
    d = _load(email)
    reminders = d.get("reminders", [])
    reminder["id"]         = f"rem_{len(reminders)+1}_{datetime.now().strftime('%H%M%S')}"
    reminder["created_at"] = datetime.now().isoformat()
    reminders.append(reminder)
    d["reminders"] = reminders
    _save(email, d)

def load_reminders(email): return _load(email).get("reminders", [])

def delete_reminder(email, rid):
    d = _load(email)
    d["reminders"] = [r for r in d.get("reminders", []) if r.get("id") != rid]
    _save(email, d)

def toggle_reminder(email, rid):
    d = _load(email)
    for r in d.get("reminders", []):
        if r.get("id") == rid:
            r["active"] = not r.get("active", True)
    _save(email, d)

# ══════════════════════════════════════════════════════════════════
# NOTES
# ══════════════════════════════════════════════════════════════════

def save_note(email, plan_id, day_key, note_text):
    d     = _load(email)
    notes = d.get("notes", {})
    notes[f"{plan_id}_{day_key}"] = {
        "text": note_text,
        "updated": datetime.now().isoformat()
    }
    d["notes"] = notes
    _save(email, d)

def load_note(email, plan_id, day_key):
    d = _load(email)
    return d.get("notes", {}).get(
        f"{plan_id}_{day_key}", {}).get("text", "")

def load_all_notes(email):
    return _load(email).get("notes", {})
