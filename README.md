# 🪨 Sizif Telegram Bot

A Telegram bot designed for personal growth and self-discipline. Inspired by the myth of Sisyphus, the project guides users through a 30-day development program with daily tasks, visualizations, and motivational content.
- 📄 This README is also available in: [Русский (README_ru.md)](README_ru.md)

![Python](https://img.shields.io/badge/Python-3.12-blue?logo=python)
![Aiogram](https://img.shields.io/badge/Aiogram-3.x-blueviolet?logo=telegram)
![SQLite](https://img.shields.io/badge/SQLite-Used-green?logo=sqlite)

---

## 🚀 Features

- 📆 30-day self-development program
- 📝 Daily personal tasks
- 🎯 Goal setting and progress tracking
- 💬 Motivational quote generation
- 🧠 Visualization of dreams and future
- 🛠️ State management (motivation, energy, etc.)

---

## 🛠️ Technologies

- `Python 3.12+`
- `Aiogram 3.x` — Telegram Bot API
- `SQLite` — local database
- `asyncio`, `random`, `datetime` — standard libraries

---

## 📦 Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/Dolmyan/Sizif.git
   cd Sizif
   ```

2. **Create a virtual environment**:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Create `.env` file** based on `.env.example`:
   ```env
   BOT_TOKEN=your_telegram_bot_token
   ADMIN_ID=your_admin_user_id
   ```

---

## ▶️ Run

```bash
python run.py
```

---

## 🗂️ Project Structure

```
Sizif/
│
├── run.py                  # Entry point
├── database.py             # SQLite interaction
├── config.py               # Environment settings
├── .env.example            # Example env file
│
├── app/
│   ├── handlers.py         # Bot handlers
│   ├── generators.py       # Motivations, quotes, etc.
│   └── utils.py            # Utility functions
│
└── data/
    ├── quotes.txt          # Motivational quotes
    ├── dreams.json         # Sample dreams
    └── ...
```

---

## 🤝 Authors

- Developer: [@bigboyandroid](https://t.me/bigboyandroid)
