# StudyAI v3 — Free Intelligent Study Planner

100% Free · No API Key · Pastel UI · Full-featured

## Quick Start

```bash
cd studyai-v3
pip install streamlit plotly pandas bcrypt python-dotenv Pillow
streamlit run app.py
```

Open → http://localhost:8501
Demo: student@studyai.com / demo123

## What's New in v3

| Feature | Details |
|---|---|
| 🌟 Landing page | App splash screen before login |
| 🔐 Login / Register | Secure bcrypt auth |
| 👤 Profile page | Edit name, role, bio, upload profile photo |
| 📋 Multi-plan storage | All plans saved & switchable |
| 📝 Day notes | Add notes per study day |
| ⏰ Reminders | Set daily study reminders with time & repeat days |
| 🎉 Completion popups | Toast notification when you finish a day |
| 🤖 General chatbot | Talks about anything, not just study topics |
| 🎨 Pastel theme | Soft purple/lavender throughout |
| 🔧 Charts fixed | Fixed duplicate xaxis TypeError |
| 💾 Persistent data | All plans/progress survive logout |

## Project Structure

```
studyai-v3/
├── app.py                        ← Entry point
├── requirements.txt
├── .streamlit/config.toml        ← Pastel theme
├── components/
│   └── styles.py                 ← Global CSS
├── page_modules/
│   ├── landing_page.py           ← App splash
│   ├── login_page.py             ← Auth
│   ├── dashboard_page.py         ← Charts & activity
│   ├── setup_page.py             ← Plan generator
│   ├── plan_page.py              ← Plan view + notes
│   ├── tools_page.py             ← Timer + Quiz + Calendar + Reminders
│   ├── analytics_page.py         ← All analytics charts
│   ├── chat_page.py              ← General AI chatbot
│   └── profile_page.py           ← Profile settings
└── utils/
    ├── auth.py                   ← bcrypt auth + photo
    ├── storage.py                ← Multi-plan JSON storage
    ├── planner.py                ← Free plan generator
    ├── charts.py                 ← Plotly charts (bug fixed)
    └── helpers.py                ← Utilities
```
