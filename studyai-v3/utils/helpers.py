# utils/helpers.py
from datetime import datetime

def fmt_dt(iso):
    if not iso: return "—"
    try:    return datetime.fromisoformat(iso).strftime("%b %d, %Y at %I:%M %p")
    except: return iso

def rel_time(iso):
    if not iso: return ""
    try:
        diff = (datetime.now()-datetime.fromisoformat(iso)).total_seconds()
        if diff<60:    return "just now"
        if diff<3600:  return f"{int(diff/60)}m ago"
        if diff<86400: return f"{int(diff/3600)}h ago"
        return f"{int(diff/86400)}d ago"
    except: return ""

def get_progress(plan, completed):
    total=done=done_days=total_days=0
    for wi,week in enumerate(plan.get("weeks",[])):
        for day in week.get("days",[]):
            if day.get("isBuffer"): continue
            total_days+=1; day_done=True
            for si in range(len(day.get("sessions",[]))):
                total+=1; k=f"{wi}_{day['dayNum']}_{si}"
                if completed.get(k): done+=1
                else: day_done=False
            if day_done and day.get("sessions"): done_days+=1
    pct=round(done/total*100) if total else 0
    return dict(pct=pct,done=done,total=total,done_days=done_days,total_days=total_days)

def week_progress(plan,completed,wi):
    weeks=plan.get("weeks",[])
    if wi>=len(weeks): return 0
    t=d=0
    for day in weeks[wi].get("days",[]):
        if day.get("isBuffer"): continue
        for si in range(len(day.get("sessions",[]))):
            t+=1
            if completed.get(f"{wi}_{day['dayNum']}_{si}"): d+=1
    return round(d/t*100) if t else 0

def weak_topics(plan,completed):
    w=[]
    for wi,week in enumerate(plan.get("weeks",[])):
        for day in week.get("days",[]):
            for si,s in enumerate(day.get("sessions",[])):
                if not completed.get(f"{wi}_{day['dayNum']}_{si}") and s.get("difficulty")=="hard":
                    w.append(s["topic"])
    return w[:4]

def perf_metrics(done_days,pct,done,total):
    return {"Consistency":min(100,40+done_days*8),"Completion":pct,
            "Speed":min(100,30+done_days*10),"Retention":min(100,50+done*3),
            "Focus":min(100,45+done_days*7)}

def diff_icon(d):  return {"easy":"🟢","medium":"🟡","hard":"🔴"}.get(d,"⚪")
def type_icon(t):  return {"lecture":"📖","practice":"✏️","revision":"🔁","assessment":"📝","project":"🛠","buffer":"🔄"}.get(t,"📌")
