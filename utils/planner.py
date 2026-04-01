# utils/planner.py
"""
Rule-based study plan generator — NO API KEY REQUIRED.
Produces structured, intelligent study plans using algorithmic logic.
"""

import random
from datetime import datetime, timedelta
from math import ceil

# ── Topic databases per subject category ─────────────────────────

SUBJECT_TEMPLATES = {
    "math": {
        "keywords": ["math","calculus","algebra","geometry","statistics","trigonometry","linear algebra","probability"],
        "beginner":     ["Number Systems","Basic Arithmetic","Fractions & Decimals","Introduction to Algebra","Linear Equations","Coordinate Geometry","Basic Geometry","Introduction to Statistics","Ratios & Proportions","Basic Trigonometry","Quadratic Equations","Functions & Graphs","Revision & Practice","Mock Assessment"],
        "intermediate": ["Advanced Algebra","Differential Calculus","Integral Calculus","Matrices & Determinants","Probability Theory","Sequences & Series","3D Geometry","Complex Numbers","Differential Equations","Vector Algebra","Statistics & Distributions","Numerical Methods","Revision & Mock Test","Final Assessment"],
        "advanced":     ["Real Analysis","Abstract Algebra","Topology","Measure Theory","Complex Analysis","Functional Analysis","Partial Differential Equations","Algebraic Geometry","Number Theory","Advanced Probability","Stochastic Processes","Mathematical Logic","Research Problems","Final Exam Prep"],
    },
    "programming": {
        "keywords": ["python","programming","coding","javascript","java","c++","react","web","software","computer science","data structures","algorithms","machine learning","ai","deep learning","django","flask","nodejs"],
        "beginner":     ["Introduction & Setup","Variables & Data Types","Control Flow (if/else)","Loops (for/while)","Functions & Scope","Lists & Arrays","Dictionaries & Maps","File Handling","Error Handling","Object-Oriented Basics","Modules & Libraries","Mini Project","Code Review & Debugging","Final Project"],
        "intermediate": ["Advanced OOP","Data Structures (Trees, Graphs)","Sorting & Searching Algorithms","Recursion & Dynamic Programming","APIs & HTTP Requests","Database Integration","Testing & Debugging","Design Patterns","Concurrency & Threads","Version Control (Git)","Deployment Basics","System Design Intro","Capstone Project","Assessment & Review"],
        "advanced":     ["Algorithm Complexity (Big-O)","Advanced Data Structures","Distributed Systems","Compiler Design","Operating Systems Concepts","Networking Fundamentals","Security & Cryptography","Cloud Architecture","Microservices","DevOps & CI/CD","Performance Optimization","Research & Open Source","Advanced Project","Technical Interview Prep"],
    },
    "science": {
        "keywords": ["physics","chemistry","biology","science","ecology","genetics","thermodynamics","quantum","organic chemistry","anatomy"],
        "beginner":     ["Introduction to the Subject","Basic Concepts & Definitions","Units & Measurements","Core Laws & Principles","Fundamental Theories","Laboratory Basics","Problem Solving Methods","Real-World Applications","Case Studies","Practical Experiments","Chapter Review","Practice Problems","Mock Test","Final Revision"],
        "intermediate": ["Advanced Theory","Quantitative Analysis","Experimental Design","Research Methods","Mathematical Models","Complex Phenomena","Inter-disciplinary Links","Literature Review","Lab Reports","Problem Sets","Mid-term Revision","Advanced Applications","Research Paper Study","Final Assessment"],
        "advanced":     ["Cutting-Edge Research","Advanced Mathematical Framework","Thesis Reading","Peer-reviewed Papers","Experimental Research","Data Analysis","Computational Methods","Specialized Topics I","Specialized Topics II","Conference Papers","Research Proposal","Independent Study","Dissertation Prep","Final Exam"],
    },
    "history": {
        "keywords": ["history","world war","civilization","geography","political","economics","sociology","philosophy","psychology","culture","literature","art","music"],
        "beginner":     ["Introduction & Timeline","Key Events Overview","Major Figures","Causes & Effects","Social Structure","Economic Factors","Cultural Impact","Political Systems","Primary Sources","Document Analysis","Comparative Study","Essay Writing","Revision","Mock Exam"],
        "intermediate": ["Historiography","Advanced Analysis","Thematic Studies","Regional Comparisons","Primary Source Critique","Statistical Evidence","Theoretical Frameworks","Ideological Perspectives","Extended Writing","Debate & Discussion","Research Skills","Source Evaluation","Timed Essays","Final Assessment"],
        "advanced":     ["Advanced Historiography","Original Research","Archival Study","Methodology","Academic Writing","Peer Review","Specialized Topics","Comparative Analysis","Thesis Development","Conference Preparation","Academic Paper Writing","Expert Interview","Dissertation Work","Defense Preparation"],
    },
    "language": {
        "keywords": ["english","hindi","french","spanish","german","language","grammar","writing","reading","vocabulary","communication","ielts","toefl"],
        "beginner":     ["Alphabet & Phonetics","Basic Vocabulary","Simple Sentences","Greetings & Introductions","Numbers & Time","Colors & Descriptions","Basic Grammar Rules","Present Tense","Past Tense","Future Tense","Reading Comprehension","Listening Practice","Writing Basics","Speaking Practice"],
        "intermediate": ["Complex Grammar","Idioms & Phrases","Academic Vocabulary","Essay Writing","Reading Academic Texts","Listening to Lectures","Debate & Discussion","Business Language","Cultural Context","Advanced Grammar","Formal Writing","Oral Presentations","Mock Test","Full Assessment"],
        "advanced":     ["Advanced Grammar Mastery","Academic & Technical Writing","Literary Analysis","Linguistic Theory","Discourse Analysis","Translation Studies","Rhetoric & Style","Advanced Composition","Research Paper Writing","Critical Reading","Advanced Speaking","Specialized Vocabulary","Practice Exam","Final Assessment"],
    },
    "generic": {
        "keywords": [],
        "beginner":     ["Introduction & Overview","Core Concepts Part 1","Core Concepts Part 2","Fundamentals Deep Dive","Practical Applications","Case Studies & Examples","Problem Solving","Hands-on Practice","Review & Consolidation","Self Assessment","Weak Area Focus","Revision Session","Practice Test","Final Review"],
        "intermediate": ["Advanced Concepts","Theory & Framework","Application Exercises","Critical Analysis","Research Methods","Project Work","Peer Review","Advanced Problems","Integration Topics","Mock Assessment","Targeted Revision","Advanced Practice","Timed Test","Final Assessment"],
        "advanced":     ["Expert-Level Theory","Advanced Research","Specialized Topics I","Specialized Topics II","Original Analysis","Advanced Projects","Publication/Portfolio Prep","Peer Collaboration","Advanced Assessment Prep","Comprehensive Review","Mock Examination","Weak Area Mastery","Final Practice","Comprehensive Final"],
    },
}

SESSION_TYPES = {
    "lecture":    {"icon": "📖", "label": "Study & Notes"},
    "practice":   {"icon": "✏️", "label": "Practice Problems"},
    "revision":   {"icon": "🔁", "label": "Revision"},
    "assessment": {"icon": "📝", "label": "Self Assessment"},
    "project":    {"icon": "🛠",  "label": "Project Work"},
    "buffer":     {"icon": "🔄", "label": "Catch-up / Buffer"},
}

DIFFICULTY_COLORS = {"easy": "🟢", "medium": "🟡", "hard": "🔴"}

STUDY_TIPS = [
    "Use the Pomodoro technique — 25 min focus, 5 min break",
    "Summarize key points in your own words after each session",
    "Teach the concept to someone else to reinforce understanding",
    "Create mind maps to visualize connections between topics",
    "Review notes within 24 hours to improve retention by 60%",
    "Practice active recall instead of passive re-reading",
    "Space your revision sessions — don't cram",
    "Connect new concepts to what you already know",
    "Test yourself with practice problems after each topic",
    "Get 7-8 hours of sleep — memory consolidates during sleep",
    "Eliminate distractions — use focus mode on your phone",
    "Break complex topics into smaller, manageable chunks",
]

def _detect_category(subject: str) -> str:
    s = subject.lower()
    for cat, data in SUBJECT_TEMPLATES.items():
        if cat == "generic": continue
        if any(kw in s for kw in data["keywords"]):
            return cat
    return "generic"

def _get_topics(subject: str, difficulty: str, n: int) -> list:
    cat = _detect_category(subject)
    base = SUBJECT_TEMPLATES[cat][difficulty].copy()
    # Personalize with subject name
    result = []
    for i, t in enumerate(base):
        if i < n:
            result.append(t)
    # If we need more topics, repeat with variations
    while len(result) < n:
        extra = [f"{subject.title()} — Advanced Practice {len(result)+1}",
                 f"{subject.title()} — Deep Dive {len(result)+1}",
                 f"Revision: {random.choice(base)}"]
        result.extend(extra)
    return result[:n]

def _make_session(topic: str, stype: str, duration: int, diff: str, tip: str) -> dict:
    return {
        "topic": topic,
        "type": stype,
        "duration": duration,
        "difficulty": diff,
        "notes": tip,
    }

def _sessions_for_day(topic: str, day_idx: int, mins: int, difficulty: str,
                      is_assessment: bool = False, is_buffer: bool = False) -> list:
    if is_buffer:
        return [_make_session("Review & catch-up", "buffer", mins, "easy",
                               random.choice(STUDY_TIPS))]
    if is_assessment:
        return [
            _make_session(f"Practice test: {topic}", "assessment", round(mins * 0.6), "medium",
                           "Attempt without referring to notes"),
            _make_session("Review incorrect answers", "revision", round(mins * 0.4), "easy",
                           "Understand mistakes and revise weak areas"),
        ]

    diff_map = {"beginner": ["easy","easy","medium"], "intermediate": ["easy","medium","hard"],
                "advanced": ["medium","hard","hard"]}
    diffs = diff_map.get(difficulty, ["easy","medium","hard"])

    # Vary session structure across days
    patterns = [
        [("lecture", 0.5), ("practice", 0.5)],
        [("lecture", 0.4), ("practice", 0.4), ("revision", 0.2)],
        [("practice", 0.6), ("revision", 0.4)],
        [("lecture", 0.35), ("practice", 0.35), ("project", 0.3)],
    ]
    pattern = patterns[day_idx % len(patterns)]
    sessions = []
    for stype, ratio in pattern:
        dur = max(15, round(mins * ratio))
        d = diffs[min(len(diffs)-1, len(sessions))]
        tip = random.choice(STUDY_TIPS)
        label = f"{topic}" if stype == "lecture" else f"Practice: {topic}" if stype == "practice" else f"Revise: {topic}"
        sessions.append(_make_session(label, stype, dur, d, tip))
    return sessions

def generate_plan(subject: str, duration: int, unit: str,
                  hours_per_day: float, difficulty: str, goals: list) -> dict:
    """Generate a complete study plan — no API needed."""

    # Calculate total days
    if unit == "weeks":   total_days = duration * 7
    elif unit == "months": total_days = duration * 30
    else:                  total_days = duration

    study_days  = round(total_days * 0.86)
    buffer_days = total_days - study_days
    weeks_count = ceil(total_days / 7)
    mins_per_day = round(hours_per_day * 60)

    # Get topic list
    topics = _get_topics(subject, difficulty, study_days + 5)

    # Build week goals
    week_themes_map = {
        1: f"Foundations of {subject.title()}",
        2: f"Core Concepts & Theory",
        3: f"Application & Practice",
        4: f"Advanced Topics",
        5: f"Integration & Projects",
        6: f"Revision & Consolidation",
        7: f"Assessment Preparation",
        8: f"Final Mastery",
    }

    weeks = []
    global_day = 0
    topic_idx  = 0
    assessment_every = 8  # add assessment day every N study days
    study_day_count = 0

    for wi in range(weeks_count):
        week_num = wi + 1
        theme    = week_themes_map.get(week_num, f"Week {week_num} — {subject.title()}")
        days_in_week = min(7, total_days - wi * 7)
        if days_in_week <= 0: break

        week_days   = []
        buffer_used = 0
        study_in_week = 0

        for di in range(days_in_week):
            global_day += 1
            day_num = global_day

            # Buffer day: 1 per week (last day of week, or proportional)
            is_buffer = (di == 6) or (buffer_days > 0 and di == days_in_week - 1 and buffer_used == 0)
            if is_buffer and buffer_used == 0:
                buffer_used += 1
                buffer_days = max(0, buffer_days - 1)
                day = {
                    "dayNum":   day_num,
                    "title":    "Buffer Day — Review & Catch-up",
                    "isBuffer": True,
                    "sessions": _sessions_for_day("", di, mins_per_day, difficulty, is_buffer=True),
                }
                week_days.append(day)
                continue

            # Assessment day
            is_assessment = (study_day_count > 0 and study_day_count % assessment_every == 0)
            topic = topics[topic_idx % len(topics)]
            topic_idx += 1
            study_day_count += 1
            study_in_week += 1

            sessions = _sessions_for_day(topic, di, mins_per_day, difficulty,
                                          is_assessment=is_assessment)
            day_title = f"Assessment: {topic}" if is_assessment else topic
            week_days.append({
                "dayNum":   day_num,
                "title":    day_title,
                "isBuffer": False,
                "sessions": sessions,
            })

        # Week goals
        covered = [d["title"] for d in week_days if not d["isBuffer"]][:3]
        week_goals = [
            f"Complete all {study_in_week} study sessions",
            f"Master: {covered[0] if covered else subject}",
            "Review and self-test at end of week",
        ]

        weeks.append({
            "weekNum": week_num,
            "title":   theme,
            "goals":   week_goals,
            "days":    week_days,
        })

    # Milestones
    mid = weeks[len(weeks)//2]["title"] if weeks else "Mid-point"
    milestones = [
        f"Complete Week 1 — Foundations established",
        f"Reach 50% — {mid} mastered",
        f"Final week complete — {subject.title()} mastered ✓",
    ]

    now = datetime.now().strftime("%B %d, %Y at %I:%M %p")
    return {
        "title":        f"{subject.title()} Study Plan",
        "description":  f"Personalized {difficulty} plan for {subject.title()} — {duration} {unit}, {hours_per_day}h/day. Generated {now}.",
        "subject":      subject,
        "difficulty":   difficulty,
        "hoursPerDay":  hours_per_day,
        "totalDays":    total_days,
        "generatedAt":  datetime.now().isoformat(),
        "goals":        goals,
        "milestones":   milestones,
        "weeks":        weeks,
    }


# ── Quiz engine ───────────────────────────────────────────────────

QUIZ_BANK = {
    "study_skills": [
        {"question": "What is the most effective study technique according to research?",
         "options":  ["Re-reading notes","Highlighting text","Active recall & self-testing","Listening to recordings"],
         "answer": 2, "explanation": "Active recall forces your brain to retrieve information, strengthening memory far more than passive review."},
        {"question": "How long should a Pomodoro focus session last?",
         "options":  ["15 minutes","25 minutes","45 minutes","60 minutes"],
         "answer": 1, "explanation": "The Pomodoro Technique uses 25-minute focused sessions followed by a 5-minute break."},
        {"question": "When is the best time to review new material for long-term retention?",
         "options":  ["1 week later","Within 24 hours","1 month later","Right before the exam"],
         "answer": 1, "explanation": "Reviewing within 24 hours leverages the forgetting curve — you retain 60% more when you review early."},
        {"question": "What is spaced repetition?",
         "options":  ["Studying the same topic repeatedly in one session","Reviewing material at increasing intervals over time","Taking breaks between Pomodoro sessions","Spacing out your study schedule evenly"],
         "answer": 1, "explanation": "Spaced repetition reviews material at growing intervals (1 day → 3 days → 1 week) to maximize long-term retention."},
        {"question": "Which environment is best for studying?",
         "options":  ["Loud café with background noise","Bedroom with TV on","Quiet, well-lit, distraction-free space","Anywhere, environment doesn't matter"],
         "answer": 2, "explanation": "A quiet, well-lit environment minimizes cognitive load from distractions, improving focus and comprehension."},
        {"question": "What does the Feynman Technique involve?",
         "options":  ["Reading textbooks twice","Explaining a concept simply as if teaching a child","Creating color-coded notes","Memorizing formulas repeatedly"],
         "answer": 1, "explanation": "The Feynman Technique reveals gaps in understanding by forcing you to explain concepts in simple terms."},
        {"question": "How much sleep do students need for optimal memory consolidation?",
         "options":  ["4-5 hours","6-7 hours","7-9 hours","10+ hours"],
         "answer": 2, "explanation": "During sleep, the brain consolidates memories from short-term to long-term storage. 7-9 hours is optimal."},
        {"question": "What is interleaving in studying?",
         "options":  ["Studying one subject for hours","Mixing different topics or subjects in one session","Using multiple colors in notes","Alternating between reading and watching videos"],
         "answer": 1, "explanation": "Interleaving — mixing topics — improves long-term retention and problem-solving ability compared to blocked practice."},
    ],
    "general_knowledge": [
        {"question": "What percentage of information do people typically forget within 24 hours without review?",
         "options":  ["20%","50%","70%","90%"],
         "answer": 2, "explanation": "Ebbinghaus's forgetting curve shows ~70% of new information is forgotten within 24 hours without reinforcement."},
        {"question": "Which learning style framework is commonly used in education?",
         "options":  ["VARK (Visual, Auditory, Reading, Kinesthetic)","STEM (Science, Technology, Engineering, Math)","SMART (Specific, Measurable, Achievable...)","GROW (Goal, Reality, Options, Will)"],
         "answer": 0, "explanation": "VARK identifies four learning preferences: Visual, Auditory, Reading/Writing, and Kinesthetic."},
        {"question": "What is a growth mindset?",
         "options":  ["Believing your abilities are fixed from birth","Believing intelligence and skills can be developed through effort","Focusing only on your natural talents","Avoiding challenges to prevent failure"],
         "answer": 1, "explanation": "Carol Dweck's research shows a growth mindset — believing abilities can improve with effort — leads to greater achievement."},
        {"question": "Which technique involves writing key concepts as questions and answering them?",
         "options":  ["Mind mapping","Cornell note-taking","SQ3R method","Skimming"],
         "answer": 1, "explanation": "The Cornell method divides notes into questions, answers, and summaries, promoting active learning and review."},
    ],
}

def get_quiz_question(subject: str, topics_studied: list) -> dict:
    """Return a quiz question — topic-aware, no API needed."""
    # Build topic-specific questions if possible
    subject_lower = subject.lower()

    # Check for subject-specific bank
    all_q = QUIZ_BANK["study_skills"] + QUIZ_BANK["general_knowledge"]

    # Add dynamic topic-based questions
    if topics_studied:
        topic = random.choice(topics_studied[:10])
        dynamic_questions = [
            {
                "question": f"What is the recommended approach when first learning '{topic}'?",
                "options": [
                    "Memorize all details immediately",
                    "Understand the core concept, then practice with examples",
                    "Skip to advanced material directly",
                    "Read about it once and move on"
                ],
                "answer": 1,
                "explanation": f"When learning new topics like '{topic}', start with core concepts and reinforce with practice."
            },
            {
                "question": f"Which study method works best for mastering '{topic}'?",
                "options": [
                    "Read the topic once thoroughly",
                    "Watch videos only",
                    "Study → Practice → Review → Teach someone else",
                    "Memorize key terms and definitions only"
                ],
                "answer": 2,
                "explanation": "The study-practice-review-teach cycle maximizes retention and deep understanding of any topic."
            },
            {
                "question": f"How should you handle a difficult concept in '{topic}'?",
                "options": [
                    "Skip it and move to easier topics",
                    "Read it 10 times until memorized",
                    "Break it into smaller parts, understand each, then connect them",
                    "Ask someone to solve it for you"
                ],
                "answer": 2,
                "explanation": "Breaking complex concepts into smaller components (chunking) makes them easier to understand and remember."
            },
            {
                "question": f"What is the best way to test your understanding of '{topic}'?",
                "options": [
                    "Re-read your notes",
                    "Close your book and try to explain the concept from memory",
                    "Highlight important sections",
                    "Copy notes again neatly"
                ],
                "answer": 1,
                "explanation": "Self-testing (active recall) without looking at materials is the most effective way to assess true understanding."
            },
        ]
        all_q = dynamic_questions + all_q

    q = random.choice(all_q)
    return q


# ── AI Chat responses ─────────────────────────────────────────────

CHAT_RESPONSES = {
    "explain": [
        "Great question! Here's how to understand this: Start by breaking it into smaller parts. Focus on the 'why' before the 'how'. Try to connect it with something you already know — that creates a mental anchor.",
        "To understand this concept well: (1) Read a simple overview first, (2) Work through 2-3 examples step by step, (3) Close your notes and try to reproduce it from memory. That cycle builds real understanding.",
        "The best way to tackle this: Think of it like building a house — you need a solid foundation (basics) before adding floors (advanced concepts). Make sure your fundamentals are solid first.",
    ],
    "tips": [
        "Here are proven study strategies: ① Use active recall — test yourself instead of re-reading. ② Space your sessions — short daily sessions beat long cramming. ③ Teach it — explain concepts aloud to find gaps. ④ Sleep well — memory consolidates during sleep.",
        "Top tips for your subject: (1) Create a distraction-free study space. (2) Use the Pomodoro method — 25 min focus, 5 min break. (3) Review notes within 24 hours. (4) Practice problems daily. (5) Connect topics to real-world examples.",
        "Effective study habits: Start each session by reviewing yesterday's material (5 min). Then learn new content (main session). End with a quick self-quiz on what you learned today. This 3-step pattern dramatically improves retention.",
    ],
    "quiz": [
        "Let's do a quick mental check! Think about the last topic you studied. Can you: (1) Explain it in simple words? (2) Give 2 real-world examples? (3) Identify what you're still unsure about? Write down your answers — it reveals gaps.",
        "Self-quiz time! Without looking at your notes, try to answer: What are the 3 most important concepts from today's session? What's one thing you found confusing? What practical application does this topic have? This active recall strengthens memory.",
        "Here's a challenge: Take the main topic you studied today and write a 5-sentence summary from memory. Then compare with your notes. The gaps you find are exactly what to focus on next session.",
    ],
    "motivation": [
        "You're doing great by showing up and studying consistently! Remember: progress compounds. One hour every day for a month = 30 hours of mastery. Each session moves you forward, even when it feels slow.",
        "Learning is hard — that's actually a good sign! Struggle means your brain is forming new connections. Research shows productive struggle leads to deeper learning than easy review. Keep going!",
        "Every expert was once a beginner. The difference between people who succeed and those who don't is simply consistency. You're already ahead of most people just by having a plan and following it.",
    ],
    "schedule": [
        "For optimal scheduling: Study your hardest topics first when your energy is highest (usually morning). Save revision and easy tasks for lower-energy periods. Always end the session knowing exactly what you'll start with tomorrow.",
        "Your study schedule tip: Block time on your calendar like a meeting you can't miss. Include buffer time (you're already doing this with your plan!). Review your weekly goals every Sunday to stay on track.",
        "Time management advice: Use time-boxing — assign specific topics to specific time slots. If you finish early, review or go deeper. If you run over, stop anyway and note where you are. This prevents one subject from dominating.",
    ],
    "default": [
        "That's a thoughtful question! The key principle here is active engagement — don't just read, interact with the material. Write summaries, draw diagrams, solve problems, and test yourself regularly.",
        "Here's my take on that: Focus on understanding over memorization. Ask yourself 'why does this work?' and 'how does this connect to what I already know?' That builds lasting knowledge.",
        "Good thinking! Remember that learning is non-linear — some days click, some don't. What matters is showing up consistently. Your study plan is your anchor. Trust the process and keep going.",
        "My suggestion: When you're stuck, step back and look at the bigger picture. How does this piece fit into the whole subject? Often, confusion clears when you see the context.",
    ],
}

def get_chat_response(message: str, subject: str = "", history: list = None) -> str:
    """Rule-based smart chat — no API needed."""
    msg = message.lower()

    if any(w in msg for w in ["explain","what is","how does","define","tell me","describe","understand"]):
        base = random.choice(CHAT_RESPONSES["explain"])
    elif any(w in msg for w in ["tip","advice","strategy","technique","method","how to study","improve"]):
        base = random.choice(CHAT_RESPONSES["tips"])
    elif any(w in msg for w in ["quiz","test","question","assess","check","recall"]):
        base = random.choice(CHAT_RESPONSES["quiz"])
    elif any(w in msg for w in ["motivat","tired","hard","difficult","struggling","stuck","give up","cant","can't"]):
        base = random.choice(CHAT_RESPONSES["motivation"])
    elif any(w in msg for w in ["schedule","plan","time","when","organize","routine","timetable"]):
        base = random.choice(CHAT_RESPONSES["schedule"])
    else:
        base = random.choice(CHAT_RESPONSES["default"])

    if subject:
        base = base.replace("this topic", f"{subject}").replace("your subject", f"{subject}")
    return base


# ── Smart Recommendations ─────────────────────────────────────────

RECOMMENDATIONS = [
    "Break your study sessions into 25-minute focused blocks with 5-minute breaks (Pomodoro technique).",
    "Review your notes from the previous session for 5 minutes before starting new material.",
    "Practice active recall by closing your notes and trying to write down everything you remember.",
    "Create a simple mind map connecting all the topics you've studied this week.",
    "Solve practice problems daily — even 10 minutes of problem-solving beats 1 hour of re-reading.",
    "Teach the concept to a friend or explain it aloud to yourself — this reveals hidden gaps.",
    "Focus extra time on topics marked 'hard' — they give the biggest improvement per study hour.",
    "Use flashcards for key terms and definitions — review them during short breaks.",
    "Write a 3-sentence summary of each session before closing your books.",
    "Set a specific, measurable goal before each session (e.g., 'Complete 10 practice problems on Topic X').",
]

def get_recommendations(subject: str, weak_topics: list, pct: int) -> list:
    recs = []
    if weak_topics:
        recs.append(f"Focus extra time on: **{weak_topics[0]}** — this is your current weak area.")
    if pct < 30:
        recs.append("Your completion is below 30%. Try marking at least 2 sessions done each day to build momentum.")
    elif pct < 60:
        recs.append("You're making good progress. Maintain consistency — daily small sessions beat weekly marathons.")
    else:
        recs.append(f"Excellent! You're {pct}% done. Focus on revision and self-testing in remaining sessions.")

    # Add random general tips
    random.shuffle(RECOMMENDATIONS)
    for r in RECOMMENDATIONS[:3 - len(recs)]:
        recs.append(r)
    return recs[:3]
