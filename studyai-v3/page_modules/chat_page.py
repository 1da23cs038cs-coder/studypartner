# page_modules/chat_page.py  — general chatbot, no API needed
import streamlit as st, random
from utils import storage
from utils.planner import get_chat_response, STUDY_TIPS

QUICK=["Give me study tips","How do I stay motivated?","Explain the Pomodoro technique",
       "What are the best revision strategies?","How to avoid procrastination?","Quiz me on my topic"]

# Extended general knowledge responses
GENERAL_RESPONSES = {
    "hello|hi|hey|greet": [
        "Hey there! 👋 I'm StudyBot, your study companion. I can chat about study strategies, answer questions, give motivation, or talk about your subject. What's on your mind?",
        "Hi! Great to see you. I'm here to help you study smarter, stay motivated, and answer any questions. What would you like to chat about?",
    ],
    "how are you|how r u|how's it": [
        "I'm doing great and ready to help you crush your study goals! 💪 How are you feeling about your studies today?",
        "Always energized when there's learning to do! How's your study session going?",
    ],
    "joke|funny|laugh": [
        "Why did the student eat his homework? Because the teacher told him it was a piece of cake! 😄 Now, back to studying — you've got this!",
        "Why is math always depressed? Because it has too many problems! 😂 Speaking of problems, need help with any study challenges?",
    ],
    "thank|thanks|appreciate": [
        "You're very welcome! That's what I'm here for. Keep up the great work — every study session brings you closer to your goals! 🌟",
        "Happy to help! You're doing amazing by investing in your learning. Keep going! 💜",
    ],
    "bye|goodbye|see you|later": [
        "Goodbye! Great study session today. Remember: consistency is the key to mastery. See you next time! 📚✨",
        "Take care! Don't forget to review your notes before sleeping — your brain consolidates memories during sleep! 🧠💤",
    ],
    "procrastinat|distract|focus|concentrat": [
        "Procrastination is the thief of dreams! Try this: set a 2-minute rule — if a task takes under 2 minutes, do it now. For bigger tasks, break them into tiny steps. Which topic are you struggling to start?",
        "The hardest part is always starting. Try the '5-minute rule' — commit to just 5 minutes of studying. Once you start, momentum takes over. Give it a try right now!",
    ],
    "stress|anxious|worried|overwhelm|panic": [
        "It's completely normal to feel stressed about studying. Take a deep breath 🌬️. Try the 4-7-8 technique: inhale 4 sec, hold 7 sec, exhale 8 sec. Then break your work into tiny, manageable tasks. You've got this! 💪",
        "Feeling overwhelmed? Let's simplify. Pick just ONE thing to focus on for the next 25 minutes. Not the whole syllabus — just one topic. Small wins build confidence!",
    ],
    "sleep|tired|exhausted": [
        "Sleep is CRITICAL for memory! Your brain consolidates everything you learned during sleep. Aim for 7-9 hours. If you're tired now, even a 20-minute power nap can restore focus. Don't sacrifice sleep for cramming!",
        "Being tired kills productivity more than anything else. If you're exhausted: take a 20-min nap, have some water, do 5 min of light exercise. Quality study > quantity of tired hours.",
    ],
    "food|eat|diet|nutrition": [
        "Your brain needs fuel! Best study foods: blueberries (boost memory), dark chocolate (improves focus), nuts (omega-3s for brain health), and staying hydrated. Avoid heavy meals before studying — they cause drowsiness!",
        "For peak brain performance: eat light meals before studying, snack on nuts or fruit, stay hydrated (even mild dehydration reduces concentration by 10%), and avoid too much caffeine.",
    ],
    "exercise|workout|physical": [
        "Exercise is literally brain food! Just 20 minutes of moderate exercise increases BDNF (brain fertilizer) by 200-300%, dramatically improving memory and learning. Try a short walk before your study session!",
        "Physical activity before studying is a secret weapon. It increases blood flow to the prefrontal cortex — the part responsible for focus, decision-making, and learning. Even a 10-min walk helps!",
    ],
    "memory|remember|memorize|forget": [
        "To memorize better: (1) Spaced repetition — review at 1 day, 3 days, 1 week, 1 month intervals. (2) Create acronyms or stories. (3) Teach it to someone. (4) Connect new info to existing knowledge. (5) Use the 'memory palace' technique!",
        "The best memorization technique is active recall — close your notes and try to write everything you remember. The harder it feels, the deeper the memory forms. Pain = gain for memory!",
    ],
}

def _smart_response(msg: str, subject: str) -> str:
    msg_lower = msg.lower()
    # Check general patterns
    for pattern, responses in GENERAL_RESPONSES.items():
        if any(p in msg_lower for p in pattern.split("|")):
            r = random.choice(responses)
            if subject and "{subject}" in r: r = r.replace("{subject}", subject)
            return r
    # Fallback to study planner responses
    return get_chat_response(msg, subject)

def render(user):
    plan=storage.load_active_plan(user["email"])
    subject=plan.get("subject","") if plan else ""

    st.markdown("## 🤖 AI Study Tutor")
    st.markdown(f"<p style='color:#9ca3af;font-size:13px;margin-top:-6px'>"
                f"{'Chat specialized for <b>'+subject+'</b>.' if subject else 'Your general-purpose study companion.'}"
                f" Chat freely about anything!</p>",unsafe_allow_html=True)

    if "chat_history" not in st.session_state or not st.session_state.chat_history:
        st.session_state.chat_history=[{"role":"assistant","content":
            f"Hey! 👋 I'm StudyBot — your AI study companion. "
            f"{'I know you are studying **'+subject+'** — ask me anything about it! ' if subject else ''}"
            "I can chat about study strategies, explain concepts, keep you motivated, or just have a conversation. What's on your mind?"}]

    # Quick prompts
    qcols=st.columns(3)
    for i,qp in enumerate(QUICK):
        with qcols[i%3]:
            full=f"{qp}{' about '+subject if subject and 'my topic' in qp.lower() else ''}"
            if st.button(qp,key=f"qp_{i}",use_container_width=True,type="secondary"):
                _send(full,subject)

    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if prompt:=st.chat_input("Chat about anything — study tips, your subject, motivation..."):
        _send(prompt,subject)

    if len(st.session_state.chat_history)>3:
        if st.button("🗑 Clear chat",type="secondary"):
            st.session_state.chat_history=[st.session_state.chat_history[0]]; st.rerun()

def _send(msg,subject):
    st.session_state.chat_history.append({"role":"user","content":msg})
    with st.chat_message("user"): st.markdown(msg)
    reply=_smart_response(msg,subject)
    with st.chat_message("assistant"): st.markdown(reply)
    st.session_state.chat_history.append({"role":"assistant","content":reply})
