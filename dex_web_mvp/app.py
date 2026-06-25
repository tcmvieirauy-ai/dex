import sqlite3
from datetime import datetime
import streamlit as st

from app.database import init_db
from app.config import DATABASE_PATH
from app.dex import chat_with_student
from app.memory import create_or_update_student

st.set_page_config(page_title="Dex", page_icon="D", layout="wide")

init_db()

ADMIN_EMAILS = ["tcmvieira@gmail.com", "tcmvieira.uy@gmail.com"]


def db():
    return sqlite3.connect(DATABASE_PATH)


def init_chat_tables():
    conn = db()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS chat_threads (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_email TEXT NOT NULL,
        title TEXT NOT NULL,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        updated_at TEXT DEFAULT CURRENT_TIMESTAMP
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS chat_messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        thread_id INTEGER NOT NULL,
        role TEXT NOT NULL,
        content TEXT NOT NULL,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS chat_folders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_email TEXT NOT NULL,
        name TEXT NOT NULL,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )
    """)

    conn.commit()
    conn.close()


def create_thread(email, title="New chat"):
    conn = db()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO chat_threads (student_email, title) VALUES (?, ?)",
        (email, title),
    )
    conn.commit()
    thread_id = cur.lastrowid
    conn.close()
    return thread_id


def get_threads(email):
    conn = db()
    cur = conn.cursor()
    cur.execute("""
        SELECT id, title, updated_at
        FROM chat_threads
        WHERE student_email=?
        ORDER BY updated_at DESC
    """, (email,))
    rows = cur.fetchall()
    conn.close()
    return rows


def update_thread_title(thread_id, title):
    conn = db()
    cur = conn.cursor()
    cur.execute(
        "UPDATE chat_threads SET title=?, updated_at=? WHERE id=?",
        (title[:60], datetime.now().isoformat(), thread_id),
    )
    conn.commit()
    conn.close()


def delete_thread(thread_id):
    conn = db()
    cur = conn.cursor()
    cur.execute("DELETE FROM chat_messages WHERE thread_id=?", (thread_id,))
    cur.execute("DELETE FROM chat_threads WHERE id=?", (thread_id,))
    conn.commit()
    conn.close()


def save_chat_message(thread_id, role, content):
    conn = db()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO chat_messages (thread_id, role, content) VALUES (?, ?, ?)",
        (thread_id, role, content),
    )
    cur.execute(
        "UPDATE chat_threads SET updated_at=? WHERE id=?",
        (datetime.now().isoformat(), thread_id),
    )
    conn.commit()
    conn.close()


def get_messages(thread_id):
    conn = db()
    cur = conn.cursor()
    cur.execute(
        "SELECT role, content FROM chat_messages WHERE thread_id=? ORDER BY id",
        (thread_id,),
    )
    rows = cur.fetchall()
    conn.close()
    return rows


def create_folder(email, name):
    conn = db()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO chat_folders (student_email, name) VALUES (?, ?)",
        (email, name),
    )
    conn.commit()
    conn.close()


def get_folders(email):
    conn = db()
    cur = conn.cursor()
    cur.execute(
        "SELECT id, name FROM chat_folders WHERE student_email=? ORDER BY name",
        (email,),
    )
    rows = cur.fetchall()
    conn.close()
    return rows


init_chat_tables()


st.markdown("""
<style>
[data-testid="stSidebar"] {
    display: none;
}

[data-testid="stHeader"] {
    background: #020817;
}

[data-testid="stToolbar"] {
    display: none;
}

[data-testid="stAppViewContainer"] {
    background: #020817;
}

.block-container {
    padding: 0rem 2rem 0rem 2rem;
    max-width: 100%;
}

body {
    overflow: auto;
}

.main-title {
    font-size: 32px;
    font-weight: 800;
    color: white;
    margin-bottom: 0;
}

.subtitle {
    color: #94a3b8;
    font-size: 14px;
}

.top-line {
    border-bottom: 1px solid #1e293b;
    padding-bottom: 18px;
    margin-bottom: 20px;
}

.chat-scroll {
    min-height: 60vh;
    max-height: 60vh;
    overflow-y: auto;
    padding: 10px 20px 20px 20px;
    border-radius: 12px;
}

.welcome-box {
    text-align: center;
    margin-top: 90px;
}

.dex-logo {
    width: 70px;
    height: 70px;
    border: 2px solid #4f7cff;
    border-radius: 18px;
    color: #4f7cff;
    font-size: 38px;
    font-weight: 800;
    display: flex;
    align-items: center;
    justify-content: center;
    margin: auto;
    box-shadow: 0 0 28px rgba(79,124,255,0.35);
}

.welcome-title {
    font-size: 34px;
    font-weight: 800;
    color: white;
    margin-top: 20px;
}

.welcome-title span {
    color: #4f7cff;
}

.suggestion-card {
    border: 1px solid #243244;
    background: #07111f;
    border-radius: 14px;
    padding: 14px;
    color: white;
    min-height: 70px;
    font-size: 14px;
}

.user-message {
    background: #2563eb;
    color: white;
    padding: 14px 18px;
    border-radius: 16px;
    margin: 12px 0 12px auto;
    max-width: 70%;
}

.dex-message {
    background: #111827;
    color: white;
    padding: 14px 18px;
    border-radius: 16px;
    margin: 12px auto 12px 0;
    max-width: 70%;
}

.right-panel {
    background: #030b18;
    border-left: 1px solid #1e293b;
    padding: 22px;
    height: 82vh;
    overflow-y: auto;
    position: sticky;
    top: 20px;
}

.user-card {
    display: flex;
    gap: 12px;
    align-items: center;
    margin-bottom: 24px;
}

.avatar {
    width: 48px;
    height: 48px;
    border-radius: 50%;
    background: linear-gradient(135deg, #4f7cff, #7c3aed);
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 800;
    color: white;
}

.user-name {
    color: white;
    font-weight: 700;
    font-size: 16px;
}

.user-email {
    color: #94a3b8;
    font-size: 12px;
}

.section-label {
    color: #94a3b8;
    font-size: 12px;
    letter-spacing: 1px;
    margin-top: 22px;
    margin-bottom: 10px;
}

.folder-item {
    color: #e5e7eb;
    padding: 6px 0;
    font-size: 14px;
}

.small-muted {
    color: #94a3b8;
    font-size: 13px;
}
</style>
""", unsafe_allow_html=True)


if "student_email" not in st.session_state:
    st.session_state.student_email = None

if "student_name" not in st.session_state:
    st.session_state.student_name = None

if "active_thread_id" not in st.session_state:
    st.session_state.active_thread_id = None


# LOGIN
if st.session_state.student_email is None:
    col1, col2, col3 = st.columns([1, 1.1, 1])

    with col2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown("<div class='dex-logo'>D</div>", unsafe_allow_html=True)
        st.markdown("<h1 style='text-align:center;color:white;'>Welcome to Dex</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align:center;color:#94a3b8;'>Log in to continue your English learning journey.</p>", unsafe_allow_html=True)

        email = st.text_input("Email")
        name = st.text_input("Name")

        if st.button("Continue", use_container_width=True):
            if not email.strip():
                st.warning("Please enter your email.")
            else:
                student = create_or_update_student(email.strip(), name.strip())
                st.session_state.student_email = student["email"]
                st.session_state.student_name = student["name"]
                st.session_state.active_thread_id = None
                st.rerun()

    st.stop()


student_email = st.session_state.student_email
student_name = st.session_state.student_name or student_email

threads = get_threads(student_email)

if st.session_state.active_thread_id is None and threads:
    st.session_state.active_thread_id = threads[0][0]


main_col, right_col = st.columns([3, 1], gap="medium")


# MAIN AREA
with main_col:
    st.markdown("""
    <div class="top-line">
        <span class="main-title">Dex</span>
        <span style="margin-left:18px;" class="subtitle">AI English learning assistant</span>
    </div>
    """, unsafe_allow_html=True)

    messages = []
    if st.session_state.active_thread_id:
        messages = get_messages(st.session_state.active_thread_id)

    st.markdown("<div class='chat-scroll'>", unsafe_allow_html=True)

    if not messages:
        st.markdown(
            f"""
            <div class='welcome-box'>
                <div class='dex-logo'>D</div>
                <div class='welcome-title'>Welcome back, <span>{student_name}</span>!</div>
                <p class='subtitle'>Ask Dex anything about English.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.markdown("<div class='suggestion-card'>💬 Difference between will and going to?</div>", unsafe_allow_html=True)
        with c2:
            st.markdown("<div class='suggestion-card'>📘 Explain Present Perfect simply.</div>", unsafe_allow_html=True)
        with c3:
            st.markdown("<div class='suggestion-card'>🎙️ Give me 5 phrasal verbs.</div>", unsafe_allow_html=True)
        with c4:
            st.markdown("<div class='suggestion-card'>💡 Help my speaking skills.</div>", unsafe_allow_html=True)
    else:
        for role, content in messages:
            css = "user-message" if role == "student" else "dex-message"
            st.markdown(f"<div class='{css}'>{content}</div>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

    user_input = st.chat_input("Ask Dex something...")

    if user_input:
        if st.session_state.active_thread_id is None:
            title = user_input[:45] + ("..." if len(user_input) > 45 else "")
            st.session_state.active_thread_id = create_thread(student_email, title)

        current_messages = get_messages(st.session_state.active_thread_id)

        save_chat_message(st.session_state.active_thread_id, "student", user_input)

        if len(current_messages) == 0:
            update_thread_title(st.session_state.active_thread_id, user_input)

        with st.spinner("Dex is thinking..."):
            response = chat_with_student(student_email, user_input)

        save_chat_message(st.session_state.active_thread_id, "dex", response)
        st.rerun()


# RIGHT PANEL
with right_col:
    st.markdown("<div class='right-panel'>", unsafe_allow_html=True)

    st.markdown("<div class='main-title'>Dex</div>", unsafe_allow_html=True)

    initial = (student_name[0] if student_name else "D").upper()

    st.markdown(
        f"""
        <div class='user-card'>
            <div class='avatar'>{initial}</div>
            <div>
                <div class='user-name'>{student_name}</div>
                <div class='user-email'>{student_email}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if st.button("+ New Chat", use_container_width=True):
        st.session_state.active_thread_id = create_thread(student_email, "New chat")
        st.rerun()

    with st.expander("+ New Folder"):
        folder_name = st.text_input("Folder name")
        if st.button("Create Folder"):
            if folder_name.strip():
                create_folder(student_email, folder_name.strip())
                st.rerun()

    folders = get_folders(student_email)

    st.markdown("<div class='section-label'>FOLDERS</div>", unsafe_allow_html=True)

    if folders:
        for _, fname in folders:
            st.markdown(f"<div class='folder-item'>📁 {fname}</div>", unsafe_allow_html=True)
    else:
        st.markdown("<div class='small-muted'>No folders yet.</div>", unsafe_allow_html=True)

    st.divider()

    st.markdown("<div class='section-label'>RECENT CHATS</div>", unsafe_allow_html=True)

    search = st.text_input("Search chats", placeholder="Search chats...")

    filtered = threads
    if search.strip():
        filtered = [t for t in threads if search.lower() in t[1].lower()]

    for tid, title, _ in filtered[:12]:
        c1, c2 = st.columns([5, 1])
        with c1:
            if st.button(f"💬 {title}", key=f"open_{tid}", use_container_width=True):
                st.session_state.active_thread_id = tid
                st.rerun()
        with c2:
            if st.button("🗑", key=f"delete_{tid}"):
                delete_thread(tid)
                if st.session_state.active_thread_id == tid:
                    st.session_state.active_thread_id = None
                st.rerun()

    st.divider()

    if st.button("Logout", use_container_width=True):
        st.session_state.student_email = None
        st.session_state.student_name = None
        st.session_state.active_thread_id = None
        st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)
