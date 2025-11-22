# backend/scoring_engine.py
"""
Enhanced scoring engine:
 - improved keyword detection (name, age, class/school, family, hobbies, goal)
 - salutation & flow checks
 - grammar via language_tool_python
 - sentiment/engagement via vaderSentiment
 - vocabulary richness via lexicalrichness (MTLD) and TTR
 - LLM feedback via GeminiClient (if configured)
 - robust evidence and signals for observability
"""

import re
import logging
from typing import Dict, Any, List, Tuple, Optional

from .gemini_client import GeminiClient

logger = logging.getLogger(__name__)

# Attempt optional imports (we will fallback gracefully)
try:
    import language_tool_python
except Exception:
    language_tool_python = None
    logger.info("language_tool_python not available — grammar checks will be disabled.")

try:
    from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
    _vader = SentimentIntensityAnalyzer()
except Exception:
    _vader = None
    logger.info("vaderSentiment not available — engagement/sentiment will be fallback.")

try:
    from lexicalrichness import LexicalRichness
except Exception:
    LexicalRichness = None
    logger.info("lexicalrichness not available — MTLD/TTR will be fallback.")

# -------------------------
# Rubric weights (adjustable)
# These weights map to final_score calculation. Change as needed to match official rubric.
# Sum = 100
RUBRIC_WEIGHTS = {
    "keyword_presence": 30,
    "salutation_flow": 5,
    "wpm": 10,
    "filler": 10,
    "semantics": 10,
    "grammar": 15,
    "engagement": 10,
}

# default ideal intro used for semantic comparison (if embeddings implemented later)
IDEAL_INTRO = (
    "My name is [Name]. I am studying in class [Class] at [School]. "
    "My hobbies include [Hobby]. I live with my family consisting of [Family]. "
    "My goal is to become [Goal]."
)

# -------------------------
# Helper / NLP util functions
# -------------------------
def normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip())

def get_words(text: str) -> List[str]:
    return re.findall(r"\w+(?:[-']\w+)?", text)

# -------------------------
# Keyword & pattern detection
# -------------------------
def detect_name(transcript: str) -> Optional[str]:
    """
    Try several patterns to detect the speaker's name.
    Returns the found name string or None.
    """
    # common patterns: "my name is X", "I am X", "I'm X"
    patterns = [
        r"\bmy name is\s+([A-Z][a-zA-Z\-']{1,40})\b",
        r"\bI am\s+([A-Z][a-zA-Z\-']{1,40})\b",
        r"\bI'm\s+([A-Z][a-zA-Z\-']{1,40})\b",
        r"\bthis is\s+([A-Z][a-zA-Z\-']{1,40})\b",
    ]
    for p in patterns:
        m = re.search(p, transcript)
        if m:
            return m.group(1)
    return None

def detect_age(transcript: str) -> Optional[int]:
    """Detect explicit age like '13 years old' or 'I am 13'."""
    m = re.search(r"\b(\d{1,2})\s*(?:years old|yrs|yo)\b", transcript, flags=re.IGNORECASE)
    if m:
        return int(m.group(1))
    m = re.search(r"\bI am\s+(\d{1,2})\b", transcript, flags=re.IGNORECASE)
    if m:
        return int(m.group(1))
    return None

def detect_school_class(transcript: str) -> Dict[str, bool]:
    """Detect mention of class / school / section."""
    found_school = bool(re.search(r"\bschool\b", transcript, flags=re.IGNORECASE))
    found_class = bool(re.search(r"\bclass\s*\d{1,2}\b", transcript, flags=re.IGNORECASE)) or bool(re.search(r"\bclass\s+[A-Za-z0-9]+\b", transcript, flags=re.IGNORECASE))
    found_section = bool(re.search(r"\bsection\b", transcript, flags=re.IGNORECASE))
    # also look for common words like 'grade' or 'std'
    found_grade = bool(re.search(r"\b(grade|std|standard)\b", transcript, flags=re.IGNORECASE))
    return {"school": found_school, "class": found_class, "section": found_section, "grade": found_grade}

def detect_family(transcript: str) -> bool:
    return bool(re.search(r"\bfamily\b|\bmother\b|\bfather\b|\bsister\b|\bbrother\b|\bparents\b", transcript, flags=re.IGNORECASE))

def detect_hobbies(transcript: str) -> bool:
    # look for verbs and nouns indicating hobbies
    hobby_patterns = r"\b(hobby|hobbies|enjoy|like|love|playing|play|reading|drawing|singing|dancing|cricket|football|football|painting|coding)\b"
    return bool(re.search(hobby_patterns, transcript, flags=re.IGNORECASE))

def detect_goal(transcript: str) -> bool:
    return bool(re.search(r"\b(goal|aim|want to be|aspire|dream)\b", transcript, flags=re.IGNORECASE))

def detect_fun_fact(transcript: str) -> bool:
    return bool(re.search(r"\b(fun fact|one thing people|people don't know|secret)\b", transcript, flags=re.IGNORECASE))

def detect_salutation_and_closing(transcript: str) -> Dict[str, bool]:
    has_salutation = bool(re.search(r"\b(hello|hi|good morning|good evening|hey everyone|hello everyone)\b", transcript, flags=re.IGNORECASE))
    has_closing = bool(re.search(r"\b(thank you|thanks for listening|thank you for listening|thanks)\b", transcript, flags=re.IGNORECASE))
    return {"salutation": has_salutation, "closing": has_closing}

def detect_flow(transcript: str) -> Dict[str, bool]:
    """
    Check for presence of:
      - intro: name/class/school
      - body: hobbies / family / interests
      - closing: thank you or similar
    """
    name = bool(detect_name(transcript))
    school_class = any(detect_school_class(transcript).values())
    body = detect_hobbies(transcript) or detect_family(transcript) or detect_fun_fact(transcript)
    closing = detect_salutation_and_closing(transcript)["closing"]
    return {"intro": name or school_class, "body": body, "closing": closing}

# -------------------------
# Filler detection
# -------------------------
FILLERS = {"umm", "uh", "like", "you know", "basically", "actually", "erm", "hmm"}
def count_fillers(words: List[str]) -> Tuple[int, float]:
    lower = [w.lower() for w in words]
    count = sum(1 for f in FILLERS for w in lower if w == f)
    percent = (count / max(1, len(words))) * 100
    return count, percent

# -------------------------
# Grammar checks (language_tool)
# -------------------------
def grammar_evidence(transcript: str) -> Dict[str, Any]:
    if language_tool_python is None:
        return {"enabled": False, "errors": None, "matches": None}
    try:
        tool = language_tool_python.LanguageTool("en-US")
        matches = tool.check(transcript)
        return {"enabled": True, "errors": len(matches), "matches": matches}
    except Exception as e:
        logger.exception("LanguageTool error: %s", e)
        return {"enabled": False, "errors": None, "matches": None}

def grammar_score_from_errors(error_count: int, word_count: int) -> float:
    """
    Map grammar errors -> score.
    Example heuristic:
      - 0 errors => 100
      - errors per 100 words >= 10 => 0
      - linear otherwise
    """
    if word_count <= 0:
        return 60.0
    errors_per_100 = (error_count / word_count) * 100
    if errors_per_100 <= 1:
        return 100.0
    if errors_per_100 >= 10:
        return 0.0
    # linear mapping between 1 and 10 -> 100 down to 0
    score = 100.0 - ((errors_per_100 - 1) / (10 - 1)) * 100.0
    return max(0.0, min(100.0, score))

# -------------------------
# Vocabulary richness
# -------------------------
def vocabulary_measures(transcript: str) -> Dict[str, float]:
    words = get_words(transcript)
    wc = len(words)
    unique = len(set([w.lower() for w in words]))
    ttr = unique / max(1, wc)
    mtld = None
    if LexicalRichness is not None:
        try:
            lx = LexicalRichness(transcript)
            mtld = lx.mtld()
        except Exception as e:
            logger.exception("lexicalrichness error: %s", e)
            mtld = None
    return {"word_count": wc, "unique": unique, "ttr": ttr, "mtld": mtld}

# -------------------------
# Engagement / sentiment
# -------------------------
def engagement_from_sentiment(transcript: str) -> Dict[str, Any]:
    if _vader is None:
        return {"available": False, "compound": 0.0, "engagement_score": 60.0}
    vs = _vader.polarity_scores(transcript)
    compound = vs.get("compound", 0.0)
    # Map compound (-1..1) to 0..100: -1 -> 20, 0 -> 60, +1 -> 100 (heuristic)
    engagement_score = 60.0 + (compound * 40.0)
    engagement_score = max(0.0, min(100.0, engagement_score))
    return {"available": True, "compound": compound, "engagement_score": engagement_score}

# -------------------------
# Semantic placeholder (embedding aware)
# -------------------------
def semantic_similarity_placeholder(transcript: str) -> Dict[str, Any]:
    # Placeholder: simple heuristic or fixed fallback.
    return {"similarity": 0.60, "score": 60.0}

# -------------------------
# Top-level orchestrator: analyze()
# -------------------------
def analyze(transcript: str, duration_seconds: float, api_key: Optional[str] = None) -> Dict[str, Any]:
    """
    Run the full scoring pipeline and return:
      {
        "final_score": float,
        "breakdown": { ... per-criterion ... },
        "signals": { raw evidence ... }
      }
    """
    text = normalize_text(transcript)
    words = get_words(text)
    wc = len(words)
    wpm = (wc / max(1, duration_seconds)) * 60.0 if duration_seconds > 0 else 0.0

    # Keyword detections
    name = detect_name(text)
    age = detect_age(text)
    sc = detect_school_class(text)
    family = detect_family(text)
    hobbies = detect_hobbies(text)
    goal = detect_goal(text)
    fun_fact = detect_fun_fact(text)

    keywords_found = {
        "name": bool(name),
        "age": bool(age),
        "school_or_class": bool(sc["school"] or sc["class"] or sc["grade"] or sc["section"]),
        "family": family,
        "hobbies": hobbies,
        "goal": goal,
        "fun_fact": fun_fact,
    }

    # Keyword presence scoring (30 points weight)
    # Count must-have items (name, age/school/class, family, hobbies) and bonus items (goal, fun_fact)
    must_have = ["name", "school_or_class", "family", "hobbies"]
    bonus = ["age", "goal", "fun_fact"]
    found_must = sum(1 for k in must_have if keywords_found.get(k))
    found_bonus = sum(1 for k in bonus if keywords_found.get(k))
    must_score = (found_must / len(must_have)) * 100.0
    bonus_score = (found_bonus / len(bonus)) * 100.0
    # combine into 0..100 for keyword presence
    keyword_presence_score = (0.8 * must_score) + (0.2 * bonus_score)

    # Salutation & flow
    sal_cl = detect_salutation_and_closing(text)
    flow = detect_flow(text)
    salutation_flow_score = 0.0
    # salutation (2.5 pts), flow intro/body/closing (2.5 pts distributed)
    salutation_score = 100.0 if sal_cl["salutation"] else 0.0
    intro_score = 100.0 if flow["intro"] else 0.0
    body_score = 100.0 if flow["body"] else 0.0
    closing_score = 100.0 if flow["closing"] else 0.0
    # aggregate into 0..100
    salutation_flow_score = (0.4 * salutation_score + 0.2 * intro_score + 0.2 * body_score + 0.2 * closing_score)

    # Filler
    filler_count, filler_percent = count_fillers(words)
    if filler_percent <= 2:
        filler_score = 100.0
    elif filler_percent >= 10:
        filler_score = 0.0
    else:
        filler_score = 100.0 - ((filler_percent - 2.0) / (10.0 - 2.0)) * 100.0

    # WPM scoring
    if 110 <= wpm <= 150:
        wpm_score = 100.0
    elif 90 <= wpm < 110 or 150 < wpm <= 170:
        wpm_score = 70.0
    else:
        wpm_score = 40.0

    # Semantics
    semantic = semantic_similarity_placeholder(text)
    semantic_score = semantic["score"]

    # Grammar
    grammar_info = grammar_evidence(text)
    if grammar_info.get("enabled") and grammar_info.get("errors") is not None:
        grammar_score = grammar_score_from_errors(grammar_info["errors"], wc)
    else:
        grammar_score = 60.0  # fallback

    # Engagement / Sentiment
    eng_info = engagement_from_sentiment(text)
    engagement_score = eng_info.get("engagement_score", 60.0)

    # Vocabulary
    vocab = vocabulary_measures(text)

    # LLM feedback (optional)
    llm_info = None
    if api_key:
        try:
            client = GeminiClient(api_key=api_key)
            # request human-like feedback (short)
            prompt = (
                "You are an objective grader. Return JSON with keys:\n"
                "grammar_score (0-100), grammar_feedback (short), engagement_score (0-100), engagement_feedback (short).\n\n"
                f"Transcript: '''{text}'''\nReturn JSON only."
            )
            llm_info = client.generate_json(prompt)
            # if LLM provided numeric scores, override / merge with deterministic ones (careful)
            if isinstance(llm_info, dict) and "grammar_score" in llm_info:
                try:
                    grammar_score = float(llm_info.get("grammar_score", grammar_score))
                except Exception:
                    pass
            if isinstance(llm_info, dict) and "engagement_score" in llm_info:
                try:
                    engagement_score = float(llm_info.get("engagement_score", engagement_score))
                except Exception:
                    pass
        except Exception as e:
            logger.exception("LLM scoring failed (continuing with deterministic scores): %s", e)
            llm_info = {"_raw": str(e)}

    # Compose breakdown using rubric weights
    breakdown = {
        "Keyword Presence": {"score": keyword_presence_score, "evidence": keywords_found},
        "Salutation & Flow": {"score": salutation_flow_score, "evidence": {"salutation": sal_cl, "flow": flow}},
        "Speech Rate (WPM)": {"score": wpm_score, "evidence": {"wpm": wpm, "word_count": wc, "duration": duration_seconds}},
        "Filler Words": {"score": filler_score, "evidence": {"filler_count": filler_count, "filler_percent": filler_percent}},
        "Content Semantics": {"score": semantic_score, "evidence": semantic},
        "Grammar & Syntax": {"score": grammar_score, "evidence": grammar_info},
        "Engagement & Sentiment": {"score": engagement_score, "evidence": eng_info},
        "Vocabulary": {"ttr": vocab.get("ttr"), "mtld": vocab.get("mtld")}
    }

    # Weighted final score
    weighted_sum = (
        breakdown["Keyword Presence"]["score"] * RUBRIC_WEIGHTS["keyword_presence"] +
        breakdown["Salutation & Flow"]["score"] * RUBRIC_WEIGHTS["salutation_flow"] +
        breakdown["Speech Rate (WPM)"]["score"] * RUBRIC_WEIGHTS["wpm"] +
        breakdown["Filler Words"]["score"] * RUBRIC_WEIGHTS["filler"] +
        breakdown["Content Semantics"]["score"] * RUBRIC_WEIGHTS["semantics"] +
        breakdown["Grammar & Syntax"]["score"] * RUBRIC_WEIGHTS["grammar"] +
        breakdown["Engagement & Sentiment"]["score"] * RUBRIC_WEIGHTS["engagement"]
    )

    total_weight = sum(RUBRIC_WEIGHTS.values())
    final_score = weighted_sum / total_weight if total_weight > 0 else 0.0

    signals = {
        "word_count": wc,
        "wpm": wpm,
        "rules": {
            "keywords_found": keywords_found,
            "found_must": found_must,
            "found_bonus": found_bonus,
        },
        "grammar_info": grammar_info,
        "vocab": vocab,
        "llm": llm_info,
    }

    return {
        "final_score": final_score,
        "breakdown": breakdown,
        "signals": signals
    }