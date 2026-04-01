# utils/charts.py  — FIXED: no duplicate xaxis/yaxis in update_layout
import plotly.graph_objects as go
from datetime import datetime, timedelta

# Pastel palette
P1="#c4b5fd"; P2="#a78bfa"; P3="#7c6af7"   # purple ramp
P4="#86efac"; P5="#4ade80"; P6="#16a34a"   # green ramp
P7="#fca5a5"; P8="#f97316"                 # red/orange
P9="#93c5fd"; P10="#60a5fa"                # blue
BG="#faf8ff"; BG2="#f0eeff"; GRID="#e8e0ff"
TEXT="#2d2150"; MUTED="#7c6fa0"

def _base_layout(**extra):
    """Build layout dict — caller adds xaxis/yaxis explicitly to avoid duplicates."""
    layout = dict(
        paper_bgcolor=BG, plot_bgcolor=BG2,
        font=dict(color=TEXT, family="sans-serif", size=12),
        margin=dict(l=10, r=10, t=36, b=10),
    )
    layout.update(extra)
    return layout

def activity_bar(timer_sessions):
    today = datetime.now().date()
    days  = [(today-timedelta(days=i)) for i in range(6,-1,-1)]
    by_day = {d:0.0 for d in days}
    for s in timer_sessions:
        d = datetime.fromisoformat(s["ts"]).date()
        if d in by_day: by_day[d] += s["minutes"]/60
    labels = [d.strftime("%a") for d in days]
    vals   = [round(by_day[d],2) for d in days]
    colors = [P3 if i==len(days)-1 else P1 for i in range(len(days))]
    fig = go.Figure(go.Bar(x=labels,y=vals,marker_color=colors,marker_line_width=0,
        text=[f"{v:.1f}h" if v>0 else "" for v in vals],
        textposition="outside",textfont=dict(color=MUTED,size=10)))
    fig.update_layout(**_base_layout(
        title=dict(text="Hours studied — last 7 days",font=dict(size=13,color=TEXT)),
        height=200,
        xaxis=dict(gridcolor=GRID,zerolinecolor=GRID,tickfont=dict(color=MUTED)),
        yaxis=dict(gridcolor=GRID,zerolinecolor=GRID,tickfont=dict(color=MUTED),title="Hours"),
    ))
    return fig

def progress_line(pct, n_weeks):
    xs = list(range(n_weeks+1))
    ys = [round(pct*(i/n_weeks)**1.1) for i in xs]
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=xs,y=ys,mode="lines+markers",
        line=dict(color=P3,width=2),marker=dict(size=5,color=P3),
        fill="tozeroy",fillcolor="rgba(124,106,247,0.12)"))
    fig.update_layout(**_base_layout(
        height=130,showlegend=False,
        xaxis=dict(showticklabels=False,showgrid=False),
        yaxis=dict(range=[0,105],ticksuffix="%",gridcolor=GRID,
                   zerolinecolor=GRID,tickfont=dict(color=MUTED)),
    ))
    return fig

def heatmap_chart(timer_sessions,days=56):
    today  = datetime.now().date()
    counts = {}
    for s in timer_sessions:
        d = datetime.fromisoformat(s["ts"]).date()
        counts[d] = counts.get(d,0)+1
    all_days = [(today-timedelta(days=i)) for i in range(days-1,-1,-1)]
    vals = [min(counts.get(d,0),4) for d in all_days]
    while len(vals)%7!=0: vals.insert(0,0)
    matrix = [vals[i:i+7] for i in range(0,len(vals),7)]
    fig = go.Figure(go.Heatmap(
        z=matrix,x=["Sun","Mon","Tue","Wed","Thu","Fri","Sat"],
        y=[f"Wk{i+1}" for i in range(len(matrix))],
        colorscale=[[0,BG2],[0.25,"#ede9fe"],[0.5,P1],[0.75,P2],[1,P3]],
        showscale=False,zmin=0,zmax=4))
    fig.update_layout(**_base_layout(
        height=180,
        title=dict(text="Activity heatmap",font=dict(size=13,color=TEXT)),
        xaxis=dict(tickfont=dict(color=MUTED)),
        yaxis=dict(tickfont=dict(color=MUTED)),
    ))
    return fig

def topic_bars(plan, completed):
    tm={}
    for wi,week in enumerate(plan.get("weeks",[])):
        for day in week.get("days",[]):
            for si,s in enumerate(day.get("sessions",[])):
                t=s["topic"][:24]
                if t not in tm: tm[t]=[0,0]
                tm[t][1]+=1
                if completed.get(f"{wi}_{day['dayNum']}_{si}"): tm[t][0]+=1
    items=sorted(tm.items(),key=lambda x:x[1][0]/max(x[1][1],1),reverse=True)[:8]
    if not items:
        fig=go.Figure(); fig.update_layout(**_base_layout(height=200)); return fig
    labels=[k for k,_ in items]
    pcts  =[round(v[0]/v[1]*100) for _,v in items]
    colors=[P6 if p>=70 else P9 if p>=40 else P7 for p in pcts]
    fig=go.Figure(go.Bar(x=pcts,y=labels,orientation="h",
        marker_color=colors,marker_line_width=0,
        text=[f"{p}%" for p in pcts],textposition="outside",
        textfont=dict(color=MUTED,size=10)))
    fig.update_layout(**_base_layout(
        height=max(200,len(labels)*34),
        title=dict(text="Topic completion",font=dict(size=13,color=TEXT)),
        xaxis=dict(range=[0,115],ticksuffix="%",gridcolor=GRID,
                   zerolinecolor=GRID,tickfont=dict(color=MUTED)),
        yaxis=dict(gridcolor=GRID,zerolinecolor=GRID,tickfont=dict(color=MUTED)),
    ))
    return fig

def weekly_hours(plan,completed):
    labels,hours=[],[]
    for wi,week in enumerate(plan.get("weeks",[])):
        t=d=0
        for day in week.get("days",[]):
            for si,_ in enumerate(day.get("sessions",[])):
                if not day.get("isBuffer"):
                    t+=1
                    if completed.get(f"{wi}_{day['dayNum']}_{si}"): d+=1
        ratio=d/t if t else 0
        h=round(len(week["days"])*(plan.get("hoursPerDay",2))*ratio,1)
        labels.append(f"Wk{week['weekNum']}")
        hours.append(h)
    fig=go.Figure(go.Bar(x=labels,y=hours,marker_color=P1,marker_line_width=0,
        text=[f"{h}h" if h>0 else "" for h in hours],
        textposition="outside",textfont=dict(color=MUTED,size=10)))
    fig.update_layout(**_base_layout(
        height=200,
        title=dict(text="Hours studied per week",font=dict(size=13,color=TEXT)),
        xaxis=dict(gridcolor=GRID,zerolinecolor=GRID,tickfont=dict(color=MUTED)),
        yaxis=dict(gridcolor=GRID,zerolinecolor=GRID,tickfont=dict(color=MUTED),title="Hours"),
    ))
    return fig

def radar_chart(metrics):
    cats=list(metrics.keys()); vals=list(metrics.values())
    fig=go.Figure(go.Scatterpolar(
        r=vals+[vals[0]],theta=cats+[cats[0]],fill="toself",
        fillcolor="rgba(167,139,250,0.2)",
        line=dict(color=P3,width=2),marker=dict(color=P3,size=5)))
    fig.update_layout(
        polar=dict(bgcolor=BG2,
            radialaxis=dict(range=[0,100],tickfont=dict(color=MUTED,size=9),
                            gridcolor=GRID,linecolor=GRID),
            angularaxis=dict(tickfont=dict(color=TEXT,size=11),gridcolor=GRID)),
        paper_bgcolor=BG,font=dict(color=TEXT),
        margin=dict(l=40,r=40,t=40,b=40),height=260,showlegend=False,
        title=dict(text="Performance radar",font=dict(size=13,color=TEXT)))
    return fig

def type_donut(plan,completed):
    td={}
    for wi,week in enumerate(plan.get("weeks",[])):
        for day in week.get("days",[]):
            for si,s in enumerate(day.get("sessions",[])):
                t=s.get("type","other")
                if completed.get(f"{wi}_{day['dayNum']}_{si}"): td[t]=td.get(t,0)+1
    if not td: td={"No data":1}
    cmap={"lecture":P9,"practice":P4,"revision":P1,"assessment":P7,"project":"#fde68a","buffer":"#d1fae5","No data":GRID}
    labels=list(td.keys()); vals=list(td.values())
    colors=[cmap.get(l,P2) for l in labels]
    fig=go.Figure(go.Pie(labels=labels,values=vals,hole=0.55,
        marker=dict(colors=colors,line=dict(color=BG,width=2)),
        textfont=dict(color=TEXT,size=11)))
    fig.update_layout(paper_bgcolor=BG,font=dict(color=TEXT),
        legend=dict(font=dict(color=MUTED,size=10),bgcolor=BG),
        margin=dict(l=10,r=10,t=30,b=10),height=230,
        title=dict(text="Sessions by type (done)",font=dict(size=13,color=TEXT)))
    return fig

def quiz_line(scores):
    if not scores:
        fig=go.Figure(); fig.update_layout(**_base_layout(height=180)); return fig
    recent=scores[-20:]
    xs=list(range(1,len(recent)+1))
    ys=[100 if s["correct"] else 0 for s in recent]
    rolling=[round(sum(ys[max(0,i-4):i+1])/min(5,i+1)) for i in range(len(ys))]
    fig=go.Figure()
    fig.add_trace(go.Bar(x=xs,y=ys,name="Question",
        marker_color=[P6 if y else P7 for y in ys],marker_line_width=0,opacity=0.6))
    fig.add_trace(go.Scatter(x=xs,y=rolling,name="Avg",
        line=dict(color=P3,width=2),mode="lines"))
    fig.update_layout(**_base_layout(
        height=200,
        title=dict(text="Quiz performance",font=dict(size=13,color=TEXT)),
        xaxis=dict(gridcolor=GRID,zerolinecolor=GRID,tickfont=dict(color=MUTED)),
        yaxis=dict(range=[0,110],ticksuffix="%",gridcolor=GRID,
                   zerolinecolor=GRID,tickfont=dict(color=MUTED)),
        legend=dict(bgcolor=BG,font=dict(color=MUTED,size=10)),
    ))
    return fig
