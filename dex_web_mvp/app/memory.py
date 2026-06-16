from app.database import get_connection


def ensure_student(student_id: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT OR IGNORE INTO students (id, name, current_level) VALUES (?, ?, ?)",
        (student_id, student_id, "Unknown")
    )
    conn.commit()
    conn.close()


def save_message(student_id: str, role: str, message: str):
    ensure_student(student_id)
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO conversations (student_id, role, message) VALUES (?, ?, ?)",
        (student_id, role, message)
    )
    conn.commit()
    conn.close()


def save_memory(student_id: str, category: str, content: str, source: str = "auto"):
    ensure_student(student_id)
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO student_memory (student_id, category, content, source) VALUES (?, ?, ?, ?)",
        (student_id, category, content, source)
    )
    conn.commit()
    conn.close()


def get_student_context(student_id: str, limit: int = 20) -> str:
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT role, message, created_at FROM conversations WHERE student_id = ? ORDER BY id DESC LIMIT ?",
        (student_id, limit)
    )
    conversations = cursor.fetchall()

    cursor.execute(
        "SELECT category, content, created_at FROM student_memory WHERE student_id = ? ORDER BY id DESC LIMIT 30",
        (student_id,)
    )
    memories = cursor.fetchall()

    conn.close()

    lines = ["# Recent conversations"]
    for role, message, created_at in reversed(conversations):
        lines.append(f"{created_at} - {role}: {message}")

    lines.append("\n# Pedagogical memory")
    for category, content, created_at in memories:
        lines.append(f"{created_at} - {category}: {content}")

    return "\n".join(lines)


def get_student_full_data(student_id: str) -> str:
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT role, message, created_at FROM conversations WHERE student_id = ? ORDER BY id ASC",
        (student_id,)
    )
    conversations = cursor.fetchall()

    cursor.execute(
        "SELECT category, content, source, created_at FROM student_memory WHERE student_id = ? ORDER BY id ASC",
        (student_id,)
    )
    memories = cursor.fetchall()

    conn.close()

    lines = [f"# Student: {student_id}", "\n# Conversations"]
    for role, message, created_at in conversations:
        lines.append(f"{created_at} - {role}: {message}")

    lines.append("\n# Memory")
    for category, content, source, created_at in memories:
        lines.append(f"{created_at} - {category} ({source}): {content}")

    return "\n".join(lines)


def list_students():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM students ORDER BY created_at DESC")
    rows = cursor.fetchall()
    conn.close()
    return [r[0] for r in rows]

def get_student_by_email(email: str):
    email = email.strip().lower()
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, current_level, created_at FROM students WHERE id = ?", (email,))
    student = cursor.fetchone()
    conn.close()
    return student


def create_or_update_student(email: str, name: str = None):
    email = email.strip().lower()
    clean_name = name.strip() if name else email

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT id, name FROM students WHERE id = ?", (email,))
    existing = cursor.fetchone()

    if existing:
        if name and name.strip():
            cursor.execute(
                "UPDATE students SET name = ? WHERE id = ?",
                (clean_name, email)
            )
        conn.commit()
        conn.close()
        return {
            "email": email,
            "name": clean_name if name else existing[1],
            "is_new": False
        }

    cursor.execute(
        "INSERT INTO students (id, name, current_level) VALUES (?, ?, ?)",
        (email, clean_name, "Unknown")
    )

    conn.commit()
    conn.close()

    return {
        "email": email,
        "name": clean_name,
        "is_new": True
    }
