import hashlib
import random
import sqlite3
from datetime import datetime
from pathlib import Path

import pandas as pd
import streamlit as st

DB_PATH = Path("learning_hub.db")

LANGUAGES = {
    "Python": {
        "topics": [
            ("Data Types", "list, tuple, dict, set, str, int, float"),
            ("Control Flow", "if/elif/else, for loops, while loops"),
            ("Functions", "def, return, *args, **kwargs, lambda"),
            ("OOP", "classes, inheritance, dunder methods"),
            ("Error Handling", "try, except, finally, raise"),
            ("Modules", "import, from module import, packages"),
            ("Comprehensions", "list/dict/set comprehensions"),
            ("File I/O", "with open, read, write"),
            ("Generators", "yield, lazy iteration"),
            ("Decorators", "@decorator, wrappers"),
        ],
        "snippet": """# Python quick cheat sheet\nnums = [1, 2, 3]\nsquares = [n*n for n in nums]\n\ndef greet(name: str) -> str:\n    return f\"Hello {name}\"\n\nclass User:\n    def __init__(self, username):\n        self.username = username\n""",
    },
    "Java": {
        "topics": [
            ("Data Types", "int, double, boolean, char, String"),
            ("Control Flow", "if/else, switch, for, while"),
            ("Methods", "static methods, overloading"),
            ("OOP", "class, inheritance, interface"),
            ("Exceptions", "try/catch/finally, throw"),
            ("Collections", "List, Set, Map"),
            ("Streams", "stream(), filter(), map()"),
            ("File I/O", "Files, BufferedReader"),
            ("Generics", "List<T>, type safety"),
            ("Concurrency", "Thread, ExecutorService"),
        ],
        "snippet": """// Java quick cheat sheet\nimport java.util.*;\n\nclass Main {\n    public static void main(String[] args) {\n        List<Integer> nums = Arrays.asList(1,2,3);\n        nums.stream().map(n -> n*n).forEach(System.out::println);\n    }\n}\n""",
    },
    "C++": {
        "topics": [
            ("Data Types", "int, double, bool, char, std::string"),
            ("Control Flow", "if/else, switch, for, while"),
            ("Functions", "pass by value/reference, overloading"),
            ("OOP", "class, inheritance, polymorphism"),
            ("Memory", "stack, heap, smart pointers"),
            ("STL", "vector, map, set, algorithm"),
            ("Templates", "template<typename T>"),
            ("File I/O", "fstream, ifstream, ofstream"),
            ("Exceptions", "try/catch, throw"),
            ("Concurrency", "std::thread, mutex"),
        ],
        "snippet": """// C++ quick cheat sheet\n#include <iostream>\n#include <vector>\nusing namespace std;\n\nint main() {\n    vector<int> nums = {1,2,3};\n    for (int n : nums) cout << n*n << endl;\n}\n""",
    },
    "JavaScript": {
        "topics": [
            ("Data Types", "number, string, boolean, object, array"),
            ("Control Flow", "if/else, switch, loops"),
            ("Functions", "function, arrow functions"),
            ("Async", "Promise, async/await"),
            ("DOM", "querySelector, events"),
            ("ES Modules", "import/export"),
            ("Array Methods", "map, filter, reduce"),
            ("Objects", "destructuring, spread"),
            ("Error Handling", "try/catch"),
            ("Classes", "class syntax"),
        ],
        "snippet": """// JavaScript quick cheat sheet\nconst nums = [1,2,3];\nconst squares = nums.map(n => n*n);\n\nasync function fetchData() {\n  const res = await fetch('/api');\n  return res.json();\n}\n""",
    },
    "Go": {
        "topics": [
            ("Data Types", "int, float64, string, bool"),
            ("Control Flow", "if, for, switch"),
            ("Functions", "multiple returns, variadic"),
            ("Structs", "type struct, methods"),
            ("Interfaces", "duck typing"),
            ("Error Handling", "error values"),
            ("Goroutines", "go func()"),
            ("Channels", "chan, select"),
            ("Packages", "package/import"),
            ("Slices & Maps", "append, make, map"),
        ],
        "snippet": """// Go quick cheat sheet\npackage main\nimport \"fmt\"\n\nfunc main() {\n    nums := []int{1,2,3}\n    for _, n := range nums {\n        fmt.Println(n * n)\n    }\n}\n""",
    },
    "Rust": {
        "topics": [
            ("Data Types", "i32, f64, bool, String"),
            ("Control Flow", "if, loop, while, for"),
            ("Functions", "fn, return values"),
            ("Ownership", "move, borrow, references"),
            ("Structs", "struct + impl"),
            ("Enums", "enum + match"),
            ("Error Handling", "Result, Option"),
            ("Collections", "Vec, HashMap"),
            ("Traits", "shared behavior"),
            ("Concurrency", "threads, channels"),
        ],
        "snippet": """// Rust quick cheat sheet\nfn main() {\n    let nums = vec![1, 2, 3];\n    for n in nums {\n        println!(\"{}\", n * n);\n    }\n}\n""",
    },
}

QUESTION_STYLES = [
    "concept",
    "usage",
    "best_practice",
    "debug",
    "comparison",
    "output",
    "keyword",
    "scenario",
    "pitfall",
    "review",
]


def get_conn():
    return sqlite3.connect(DB_PATH)


def init_db():
    with get_conn() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS quiz_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                language TEXT NOT NULL,
                question_id TEXT NOT NULL,
                is_correct INTEGER NOT NULL,
                user_answer TEXT,
                answered_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS user_notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                language TEXT NOT NULL,
                note TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def create_user(username: str, password: str):
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO users (username, password_hash, created_at) VALUES (?, ?, ?)",
            (username, hash_password(password), datetime.utcnow().isoformat()),
        )


def verify_user(username: str, password: str) -> bool:
    with get_conn() as conn:
        row = conn.execute(
            "SELECT password_hash FROM users WHERE username = ?", (username,)
        ).fetchone()
    return bool(row and row[0] == hash_password(password))


def generate_100_questions(language: str):
    config = LANGUAGES[language]
    questions = []
    for i, style in enumerate(QUESTION_STYLES):
        for j, (topic, detail) in enumerate(config["topics"]):
            qid = f"{language}-{i}-{j}"
            question_text = (
                f"[{style.upper()}] In {language}, which statement is most accurate about "
                f"{topic.lower()} ({detail})?"
            )
            correct = f"It correctly explains {topic.lower()} in {language}."
            distractors = [
                f"It is unrelated to {language} {topic.lower()}.",
                f"It only applies to database queries, not {topic.lower()}.",
                f"It is deprecated and never used in modern {language}.",
            ]
            options = [correct, *distractors]
            random.Random(f"{qid}-shuffle").shuffle(options)
            questions.append(
                {
                    "id": qid,
                    "language": language,
                    "text": question_text,
                    "options": options,
                    "answer": correct,
                    "explanation": f"Focus on {topic} fundamentals when solving this type of question.",
                }
            )
    return questions


def get_attempted_ids(username: str, language: str):
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT question_id FROM quiz_history WHERE username = ? AND language = ?",
            (username, language),
        ).fetchall()
    return {r[0] for r in rows}


def get_next_question(username: str, language: str):
    all_questions = generate_100_questions(language)
    attempted = get_attempted_ids(username, language)
    remaining = [q for q in all_questions if q["id"] not in attempted]
    if not remaining:
        return None
    return random.choice(remaining)


def save_answer(username: str, language: str, question_id: str, is_correct: bool, user_answer: str):
    with get_conn() as conn:
        conn.execute(
            """
            INSERT INTO quiz_history (username, language, question_id, is_correct, user_answer, answered_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                username,
                language,
                question_id,
                int(is_correct),
                user_answer,
                datetime.utcnow().isoformat(),
            ),
        )


def get_progress(username: str):
    rows = []
    with get_conn() as conn:
        for language in LANGUAGES:
            stats = conn.execute(
                """
                SELECT COUNT(*), COALESCE(SUM(is_correct), 0)
                FROM quiz_history
                WHERE username = ? AND language = ?
                """,
                (username, language),
            ).fetchone()
            answered, correct = stats
            rows.append(
                {
                    "Language": language,
                    "Answered": answered,
                    "Correct": correct,
                    "Completion %": round((answered / 100) * 100, 1),
                    "Accuracy %": round((correct / answered) * 100, 1) if answered else 0,
                }
            )
    return pd.DataFrame(rows)


def save_note(username: str, language: str, note: str):
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO user_notes (username, language, note, created_at) VALUES (?, ?, ?, ?)",
            (username, language, note, datetime.utcnow().isoformat()),
        )


def get_notes(username: str):
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT language, note, created_at FROM user_notes WHERE username=? ORDER BY id DESC LIMIT 20",
            (username,),
        ).fetchall()
    return rows


def render_login():
    st.title("🚀 Multi-Language Coding Learning Hub")
    st.caption("Learn Python, Java, C++, JavaScript, Go, and Rust with persistent progress.")

    tab_login, tab_signup = st.tabs(["Login", "Sign Up"])

    with tab_login:
        u = st.text_input("Username", key="login_username")
        p = st.text_input("Password", type="password", key="login_password")
        if st.button("Login", type="primary"):
            if verify_user(u, p):
                st.session_state.user = u
                st.success("Welcome back! Your saved progress has been loaded.")
                st.rerun()
            else:
                st.error("Invalid username or password")

    with tab_signup:
        su = st.text_input("Create username", key="signup_username")
        sp = st.text_input("Create password", type="password", key="signup_password")
        if st.button("Create account"):
            if len(su) < 3 or len(sp) < 4:
                st.warning("Use at least 3 characters for username and 4 for password")
            else:
                try:
                    create_user(su, sp)
                    st.success("Account created. You can now log in.")
                except sqlite3.IntegrityError:
                    st.error("Username already exists.")


def render_dashboard(username: str):
    st.subheader("📊 Dashboard")
    df = get_progress(username)
    c1, c2, c3 = st.columns(3)
    total_answered = int(df["Answered"].sum())
    total_correct = int(df["Correct"].sum())
    c1.metric("Total Questions Answered", total_answered)
    c2.metric("Total Correct", total_correct)
    c3.metric("Overall Accuracy", f"{(total_correct/total_answered*100):.1f}%" if total_answered else "0%")

    st.dataframe(df, use_container_width=True)
    st.bar_chart(df.set_index("Language")[["Completion %", "Accuracy %"]])


def render_quiz(username: str):
    st.subheader("🧠 Adaptive Quiz (100 questions per language)")
    language = st.selectbox("Choose technology", list(LANGUAGES.keys()))

    if st.button("Load New Question") or "current_question" not in st.session_state:
        st.session_state.current_question = get_next_question(username, language)
        st.session_state.current_language = language

    if st.session_state.get("current_language") != language:
        st.session_state.current_question = get_next_question(username, language)
        st.session_state.current_language = language

    q = st.session_state.get("current_question")
    if q is None:
        st.success(f"You completed all 100 {language} questions! 🎉")
        return

    st.write(q["text"])
    answer = st.radio("Select your answer", q["options"], key=f"radio-{q['id']}")

    if st.button("Submit Answer", type="primary"):
        correct = answer == q["answer"]
        save_answer(username, language, q["id"], correct, answer)
        if correct:
            st.success("Correct ✅")
        else:
            st.error(f"Not quite. Correct answer: {q['answer']}")
        st.info(q["explanation"])
        st.session_state.current_question = get_next_question(username, language)
        st.rerun()


def render_cheatsheets():
    st.subheader("📚 Code Cheat Sheets")
    for lang, config in LANGUAGES.items():
        with st.expander(f"{lang} Cheat Sheet"):
            st.code(config["snippet"], language=lang.lower())


def render_special_features(username: str):
    st.subheader("✨ Special Features")
    feature = st.selectbox(
        "Choose special mode",
        ["Daily Challenge", "Lightning Round (5 Qs)", "Personal Notes"],
    )

    if feature == "Daily Challenge":
        all_langs = list(LANGUAGES.keys())
        selected = random.choice(all_langs)
        challenge = get_next_question(username, selected)
        if challenge:
            st.write(f"**Today focus language:** {selected}")
            st.write(challenge["text"])
            user_pick = st.radio("Your challenge answer", challenge["options"], key="challenge")
            if st.button("Submit Daily Challenge"):
                ok = user_pick == challenge["answer"]
                save_answer(username, selected, challenge["id"], ok, user_pick)
                st.success("Great job! Challenge saved.") if ok else st.warning("Saved. Keep practicing!")
        else:
            st.info(f"You already completed {selected}. Pick another mode.")

    elif feature == "Lightning Round (5 Qs)":
        lang = st.selectbox("Round language", list(LANGUAGES.keys()), key="lightning_lang")
        if st.button("Start Lightning Round"):
            st.session_state.lr_score = 0
            st.session_state.lr_count = 0
            st.session_state.lr_lang = lang
            st.session_state.lr_question = get_next_question(username, lang)

        if st.session_state.get("lr_question"):
            q = st.session_state.lr_question
            st.write(f"Question {st.session_state.lr_count + 1} of 5")
            st.write(q["text"])
            pick = st.radio("Answer", q["options"], key=f"lr-{q['id']}")
            if st.button("Submit Lightning Answer"):
                ok = pick == q["answer"]
                save_answer(username, st.session_state.lr_lang, q["id"], ok, pick)
                st.session_state.lr_score += int(ok)
                st.session_state.lr_count += 1
                if st.session_state.lr_count >= 5:
                    st.success(f"Round complete! Score: {st.session_state.lr_score}/5")
                    st.session_state.lr_question = None
                else:
                    st.session_state.lr_question = get_next_question(username, st.session_state.lr_lang)
                st.rerun()

    else:
        lang = st.selectbox("Note language", list(LANGUAGES.keys()), key="notes_lang")
        note = st.text_area("Write what you learned today")
        if st.button("Save Note"):
            if note.strip():
                save_note(username, lang, note.strip())
                st.success("Note saved.")
        st.write("Recent notes")
        for item_lang, item_note, created_at in get_notes(username):
            st.markdown(f"- **{item_lang}** ({created_at[:10]}): {item_note}")


def main():
    st.set_page_config(page_title="Coding Learning Hub", layout="wide")
    init_db()

    if "user" not in st.session_state:
        st.session_state.user = None

    if not st.session_state.user:
        render_login()
        return

    st.sidebar.title(f"👋 Hello, {st.session_state.user}")
    if st.sidebar.button("Logout"):
        st.session_state.user = None
        st.rerun()

    page = st.sidebar.radio(
        "Navigate",
        ["Dashboard", "Quiz", "Cheat Sheets", "Special Features"],
    )

    if page == "Dashboard":
        render_dashboard(st.session_state.user)
    elif page == "Quiz":
        render_quiz(st.session_state.user)
    elif page == "Cheat Sheets":
        render_cheatsheets()
    else:
        render_special_features(st.session_state.user)


if __name__ == "__main__":
    main()
