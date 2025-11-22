# backend/tests/test_scoring.py
from backend.scoring_engine import analyze

def test_analyze_basic():
    """
    Basic smoke test: run analyze() with a dummy API key (LLM calls will fallback)
    and assert that a final_score is present and numeric.
    """
    transcript = "Hello my name is Ravi. I study in class 9 at ABC School."
    result = analyze(transcript, duration_seconds=40, api_key="DUMMY_KEY")
    assert "final_score" in result
    assert isinstance(result["final_score"], (int, float))
    assert result["final_score"] >= 0