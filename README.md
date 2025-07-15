# Reddit User Persona Generator

This is a Python-based project that generates a detailed **user persona** by analyzing a Reddit user’s **posts** and **comments** using **LLM-based natural language analysis**. The output includes characteristics like interests, personality traits, writing tone, and more — along with proper citations from Reddit.

This project was built as part of the Generative AI Internship Assignment for **BeyondChats**.

---

## 🚀 Features

- Scrapes recent Reddit posts and comments of a user
- Generates an LLM-backed psychological and stylistic persona
- Cites exact URLs for every inferred trait
- Clean CLI interface
- Fully PEP-8 compliant code structure

---

## 🧰 Technologies Used

- Python 3.10+
- [PRAW](https://praw.readthedocs.io/en/stable/) – Reddit API wrapper
- [Google Gemini API](https://ai.google.dev/)
- `python-dotenv` for secure environment variable management

---

## 🔧 Setup Instructions

### 1. Clone this repository

```bash
git clone https://github.com/your-username/reddit-user-persona-generator.git
cd reddit-user-persona-generator
````

### 2. Install dependencies

We recommend using a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

---

### 3. Setup `.env` file

Create a `.env` file in the project root directory with the following content:

```env
# Reddit API (Create from https://www.reddit.com/prefs/apps)
REDDIT_CLIENT_ID=your_reddit_client_id
REDDIT_CLIENT_SECRET=your_reddit_client_secret

# Gemini API (Get from https://ai.google.dev/)
GOOGLE_API_KEY=your_google_gemini_api_key
```

---

## 🧪 How to Run

Run the script by providing any Reddit profile URL:

```bash
python main.py https://www.reddit.com/user/kojied/
```

This will:

1. Extract the username from the URL.
2. Scrape up to 30 posts and 30 comments.
3. Generate a structured persona using Gemini LLM.
4. Save the output to a file:
   👉 `kojied_persona.txt`

---

## 📁 Example Output

Each output `.txt` file will include:

* **Interests**
* **Personality traits**
* **Tone of writing**
* **Possible education/profession**
* **Political/Social leanings**
* **Citations** for each inferred trait

---

## 📦 File Structure

```
reddit-user-persona-generator/
│
├── main.py                  # CLI entry point
├── persona_utils.py         # Core logic and helper functions
├── requirements.txt         # Python dependencies
├── .env                     # (not committed) for API keys
├── kojied_persona.txt       # Sample output
├── Hungry-Move-6603_persona.txt  # Sample output
└── README.md                # You're here
```

---

## ✅ PEP-8 Compliant

All code follows PEP-8 standards for style and formatting. Verified using:

```bash
flake8 main.py persona_utils.py
```

---

## 📌 Notes

* Ensure your Reddit app is created as a **script app**, not web or installed.
* If Gemini API throws a quota error, try reducing post/comment limit or use a smaller model.
* Only public Reddit data is used; no login or upvote activity is tracked.

---

