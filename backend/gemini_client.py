# gemini_client.py
import os
import json
import re
import logging

logger = logging.getLogger(__name__)

# Try to import either SDK
try:
    import google.genai as genai
    _SDK = "genai"
except Exception:
    try:
        import google.generativeai as genai
        _SDK = "generativeai"
    except Exception:
        genai = None
        _SDK = None


class GeminiClient:
    def __init__(self, api_key: str = None, model: str = "gemini-2.5-flash"):
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        self.model = model

        if not self.api_key:
            raise ValueError("Gemini API key not provided. Set GOOGLE_API_KEY or pass it.")

        if genai is None:
            logger.warning("No Google GenAI SDK installed. GeminiClient will not call LLM.")
            self.available = False
        else:
            self.available = True
            try:
                # configure SDK
                genai.configure(api_key=self.api_key)
            except Exception as e:
                logger.exception("Failed to configure GenAI SDK: %s", e)
                self.available = False

    def generate_json(self, prompt: str, max_tokens: int = 300):
        """
        Ask LLM to return JSON. Returns dict or {"_raw": text}.
        """

        if not self.available:
            return {"_raw": "SDK not installed or not configured."}

        try:
            # Support both SDK styles
            if _SDK == "genai":
                resp = genai.generate_text(
                    model=self.model,
                    prompt=prompt,
                    max_output_tokens=max_tokens
                )
                text = getattr(resp, "text", None) or str(resp)

            else:  # generativeai
                resp = genai.generate(
                    model=self.model,
                    prompt=prompt,
                    max_output_tokens=max_tokens
                )
                text = getattr(resp, "text", None) or str(resp)

        except Exception as e:
            logger.exception("LLM call failed: %s", e)
            return {"_raw": str(e)}

        # Extract JSON
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if not match:
            return {"_raw": text}

        try:
            return json.loads(match.group())
        except Exception as e:
            logger.exception("JSON parsing error: %s", e)
            return {"_raw": match.group()}
