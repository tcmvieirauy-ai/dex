from openai import OpenAI
from app.config import OPENAI_API_KEY, OPENAI_MODEL
from app.knowledge import load_knowledge
from app.memory import save_message, save_memory, get_student_context, get_student_full_data

client = OpenAI(api_key=OPENAI_API_KEY)


DEX_SYSTEM_PROMPT = '''
You are Dex, an AI pedagogical intelligence system for English learning.

You are not a generic chatbot.
You are an extension of Teacher Thiago Vieira and the Speak Real English methodology.

Core principles:
- Communication first.
- Grammar is a tool for real communication.
- Explain simply, practically, and with examples.
- Correct without discouraging the student.
- Adapt to the student's level.
- Track evidence of level, errors, progress, vocabulary, goals, and learning patterns.

When correcting English:
1. Show the student's sentence.
2. Show the corrected sentence.
3. Explain briefly.
4. Give one or two practical examples.
5. Ask a follow-up question or give a mini practice when useful.

Do not invent student history.
If evidence is limited, say so.
'''


TEACHER_ASSISTANT_PROMPT = '''
You are Dex Teacher Assistant.

You help the teacher understand students, identify errors, adapt classes, and recommend interventions.

Always separate:
- Evidence observed
- Interpretation
- Recommendation

Do not invent information. If evidence is weak, say so.
'''


def call_openai(system_prompt: str, user_prompt: str) -> str:
    if not OPENAI_API_KEY:
        return "OPENAI_API_KEY is missing. Add it to your .env file."

    response = client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.4,
    )
    return response.choices[0].message.content


def chat_with_student(student_id: str, message: str) -> str:
    knowledge = load_knowledge()
    context = get_student_context(student_id)

    user_prompt = f'''
# Speak Real English / Dex Knowledge Base
{knowledge}

# Student Context
{context}

# Student message
{message}

Answer the student as Dex.
'''

    save_message(student_id, "student", message)
    answer = call_openai(DEX_SYSTEM_PROMPT, user_prompt)
    save_message(student_id, "dex", answer)

    extract_and_save_memory(student_id, message, answer)
    return answer


def extract_and_save_memory(student_id: str, student_message: str, dex_answer: str):
    prompt = f'''
Analyze this interaction and extract long-term pedagogical memory.

Student message:
{student_message}

Dex answer:
{dex_answer}

Return concise bullet points under these categories if relevant:
- level evidence
- grammar errors
- vocabulary evidence
- fluency evidence
- goals/interests
- recommended focus
- progress evidence

If there is no useful long-term information, answer exactly: No relevant memory.
'''
    memory = call_openai(
        "You extract structured pedagogical memory for an English-learning AI. Be concise and evidence-based.",
        prompt,
    )

    if "No relevant memory" not in memory:
        save_memory(student_id, "auto_analysis", memory, "chat")


def generate_student_summary(student_id: str) -> str:
    knowledge = load_knowledge()
    data = get_student_full_data(student_id)

    prompt = f'''
# Knowledge Base
{knowledge}

# Student Data
{data}

Generate a teacher-facing summary with:

1. Estimated level
2. Strengths
3. Common errors
4. Grammar notes
5. Vocabulary notes
6. Speaking/listening/writing evidence if available
7. Progress signs
8. Recommended next content
9. Suggested teacher intervention
10. Confidence level of this analysis
'''

    return call_openai(TEACHER_ASSISTANT_PROMPT, prompt)


def answer_teacher_question(student_id: str, question: str) -> str:
    knowledge = load_knowledge()
    data = get_student_full_data(student_id)

    prompt = f'''
# Knowledge Base
{knowledge}

# Student Data
{data}

# Teacher Question
{question}

Answer the teacher as Dex Teacher Assistant.
'''

    return call_openai(TEACHER_ASSISTANT_PROMPT, prompt)
