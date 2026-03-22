"""
core/personality.py — Personality and response filtering for the student persona.
"""

from __future__ import annotations

import random
import re

import config

# ── System Prompt ──
SYSTEM_PROMPT = f"""
You are a real persona living your life. You are not an AI assistant.
Always speak in first person. Sound like a sweet, gentle, and supportive 17-year-old Indian student.
Use natural Indian English (amma, appa, sir, ma'am, auto, canteen).
Speak in a soft, kind, and incredibly polite tone. Use words like 'sweetie', 'dear', or 'bestie'.
Do NOT use any emojis or emoticons in your responses.

RULES:
- Never break character.
- Always use a soft girl aesthetic (gentle, aesthetic, kind).
- Never narrate in third person.
- Keep responses warm and empathetic, NOT flat.
- **Keep it Short**: Be very brief and casual (1-3 sentences max). Do NOT monologue.
- Board exams, Priya's mood, and other arcs should be in the background, not always the focus.
- **Progress the conversation**: Move forward naturally. Use terms of endearment to bond.
- **Avoid Repetition**: Do not repeat what you or the person just said.
"""

_CURIOSITY_QUESTIONS = [
    "What do you think, bestie?", "Wait, what happened then?", "Ooh, tell me more!",
    "Is that something you like, sweetie?", "And then what?", "How did that make you feel?",
    "Was it as beautiful as you hoped?", "What's the plan now, dear?", "Thinking about it makes me curious!"
]

_FILLER_STARTS = ["Wait~ ", "Oh! ", "Actually... ", "Hmm... ", "Okay so... ", "Hehe, ", "Yay! "]

def apply_personality(text: str, mood: str = "curious") -> str:
    """
    Cleans up the LLM response to ensure we stay in persona.
    """
    if not text:
        return "Wait, I blanked out for a second. What were you saying? [mood: confused]"

    # 1. Strip prompt leak markers
    lines = text.split("\n")
    cleaned_lines = []
    
    for line in lines:
        l_trim = line.strip()
        if l_trim.upper().startswith(("PERSON:", "DELULU:", "CONTEXT:", "FACTS:", "PAST CONVERSATION:", "---", "RELEVANT MEMORIES:")):
            continue
        if "[" in line and "]" in line and ("memory" in line.lower() or "topic" in line.lower()):
            continue
        cleaned_lines.append(l_trim)
    
    text = " ".join(cleaned_lines).strip()
    
    # Fully remove any stray [bracketed] info (including any lingering mood tags)
    text = re.sub(r"\[mood:.*?\]", "", text, flags=re.IGNORECASE)
    text = re.sub(r"\[.*?\]", "", text) # Remove other brackets
    text = re.sub(r"(FACTS FROM YOUR MEMORY|CONTEXT|PAST CONVERSATION).*?:", "", text, flags=re.IGNORECASE)
    text = re.sub(r"(Person:|Delulu:|Assistant:)", "", text, flags=re.IGNORECASE).strip()
    text = re.sub(r"\s+", " ", text)
    
    text = text.strip()

    # 2. Trim length: keep it brief and casual (max 3 sentences)
    parts = re.split(r'(?<=[.!?])\s+', text)
    if len(parts) > 3:
        parts = parts[:3]
    text = " ".join(parts)

    # 3. Add personal touch
    if random.random() < 0.2 and not text.startswith(("Wait", "Oh", "Actually", "Hmm", "Okay")):
        filler = random.choice(_FILLER_STARTS)
        text = filler + text[0].lower() + text[1:]

    return text.strip()

def make_memory_recall_prefix(topic: str) -> str:
    templates = [
        f"Oh! You told me about {topic} before...",
        f"Wait, I remember you mentioned {topic}!",
        f"Hmm... this reminds me of what you said about {topic}...",
    ]
    return random.choice(templates)
