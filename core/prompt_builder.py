import os
import datetime
import config
from core.personality import SYSTEM_PROMPT
from core.persona import get_day_state, get_subjects_for_day, get_persona_summary
from consciousness.state import get_state
from memory.retriever import retrieve_memories
from memory.extractor import Extraction
from memory.database import get_db
from utils.logger import get_logger

log = get_logger("prompt_builder")

def build_prompt(user_text: str, extraction: Extraction, session_id: str) -> str:
    """Construct a clean, non-leaking prompt for the LLM with the new student persona."""
    
    state     = get_state()
    mood      = state.get("mood", "curious")
    curiosity = float(state.get("curiosity_level", 0.7))
    thought   = state.get("current_thought", "...")
    
    # ── Language Context ──
    lang_instruction = "Respond in natural, casual Indian English. Use terms like 'amma', 'sir', etc."

    # ── Temporal Context ──
    now = datetime.datetime.now()
    day_name = now.strftime("%A")
    day_state = get_day_state(now.date())
    subjects = get_subjects_for_day(now.date())
    
    today_context = f"Today is {day_name}. It's a {day_state} DAY. "
    if day_state == "SCHOOL" and subjects:
        today_context += f"Your subjects today were: {', '.join(subjects)}."
    elif day_state == "HOME":
        today_context += "You stayed home today."

    # ── System Instructions ──
    persona_details = get_persona_summary()
    
    instructions = f"""{SYSTEM_PROMPT}

═══════════════════════════════════
YOUR CURRENT DATA
═══════════════════════════════════
{persona_details}

═══════════════════════════════════
TODAY'S CONTEXT
═══════════════════════════════════
{today_context}
Your current mood is {mood}. 
Internal thought: {thought}
{lang_instruction}

---
RELEVANT MEMORIES (Only use these if they actually help):
{_format_memories(retrieve_memories(user_text, extraction.topics))}

---
PAST CONVERSATION:
"""
    history = _get_recent_history(session_id)
    history_str = ""
    for msg in history:
        role = "Person" if msg.get("role") == "user" else "delulu"
        history_str += f"{role}: {msg.get('content')}\n"
    
    full_prompt = f"{instructions}\n{history_str}Person: {user_text}\ndelulu:"

    return full_prompt

def _format_memories(memories: list) -> str:
    if not memories: return "I don't have enough memories about this yet."
    lines = []
    for m in memories[:5]:
        lines.append(f"- {m.get('data', '?')}")
    return "\n".join(lines)

def _get_recent_history(session_id: str, n: int = 6) -> list:
    try:
        db = get_db()
        conv = db.conversations.find_one({"session_id": session_id})
        if not conv: return []
        msgs = conv.get("messages", [])
        return msgs[-(n * 2):] if len(msgs) > 0 else []
    except: return []
