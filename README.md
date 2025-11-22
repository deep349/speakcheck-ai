# SpeakCheck AI

SpeakCheck AI is an AI-powered communication assessment system designed to evaluate student self-introductions.
The tool analyzes a text transcript and provides a detailed scoring breakdown based on multiple communication criteria.

## Overview

SpeakCheck AI evaluates:

* Keyword presence (name, age, class/school, family, hobbies, etc.)
* Salutation and flow (introduction, body, closing)
* Speech rate (words per minute)
* Filler words
* Grammar and syntax
* Engagement and sentiment
* Vocabulary richness (TTR, MTLD)
* Semantic relevance (placeholder, embeddings-ready)

The system combines rule-based logic, NLP tools, and optional Gemini AI feedback.

## Features

* Multi-criteria scoring rubric
* Streamlit-based user interface
* Detailed evidence and breakdown for each score
* Optional integration with Google Gemini for enhanced feedback
* Modular Python backend for easy extension
* Supports testing through pytest

## Scoring Formula (Rubric Explanation)

**SpeakCheck AI** evaluates a student’s self-introduction using a weighted rubric.
Each component is scored between **0 and 100**, then combined using fixed weights.

## **Rubric Weights**

```
Keyword Presence ............... 30
Salutation & Flow .............. 5
Speech Rate (WPM) .............. 10
Filler Words ................... 10
Content Semantics .............. 10
Grammar & Syntax ............... 15
Engagement & Sentiment ......... 10
-----------------------------------
Total Weight ................... 100
```

**Final Score Formula**

```
final_score = (sum of (sub_score × weight)) / 100
```

## **1. Keyword Presence (Weight: 30)**

Checks for:

* name
* school/class
* family
* hobbies
* **bonus:** age, goal, fun-fact

Computation:

```
must_have = [name, school_or_class, family, hobbies]   # 4 items
bonus = [age, goal, fun_fact]                          # 3 items

must_score = (found_must / 4) × 100
bonus_score = (found_bonus / 3) × 100

keyword_presence_score = 0.8 × must_score + 0.2 × bonus_score
```

## **2. Salutation & Flow (Weight: 5)**

Checks for:

* salutation (hello/hi/good morning)
* intro (name or class/school)
* body (family/hobbies/fun fact)
* closing (thank you)

Formula:

```
salutation_flow_score =
    0.4 × salutation +
    0.2 × intro +
    0.2 × body +
    0.2 × closing
```

Each is either **0 or 100**, producing a final percentage.

## **3. Speech Rate (WPM) (Weight: 10)**

```
wpm = (word_count / duration_seconds) × 60
```

Scoring buckets:

```
110–150 WPM ............. 100
90–110 or 150–170 ....... 70
otherwise ............... 40
```

## **4. Filler Words (Weight: 10)**

Detects fillers like: “umm”, “uh”, “like”, “basically”, “you know”, etc.

```
filler_percent = (filler_count / total_words) × 100
```

Score mapping:

```
<= 2% fillers ............ 100
>= 10% fillers ........... 0
between 2–10% ............ linear scale from 100 → 0
```

Formula:

```
filler_score = 100 - ((filler_percent - 2) / 8) × 100
```

---

## **5. Content Semantics (Weight: 10)**

Current version uses a placeholder:

```
semantic_score = 60
```

(Embeddings can be added later for true semantic similarity.)

## **6. Grammar & Syntax (Weight: 15)**

Uses **LanguageTool** to count grammar issues.

```
errors_per_100 = (errors / total_words) × 100
```

Scoring:

```
<= 1 error per 100 words .......... 100
>= 10 errors per 100 words ........ 0
between 1–10 ....................... linear scale
```

Formula:

```
grammar_score = 100 - ((errors_per_100 - 1) / 9) × 100
```

## **7. Engagement & Sentiment (Weight: 10)**

Based on VADER compound sentiment score (range −1 to +1).

Mapping:

```
engagement_score = 60 + (compound × 40)
```

Examples:

```
compound = 1   → score ≈ 100
compound = 0   → score = 60
compound = -1  → score ≈ 20
```

## **Vocabulary Metrics (Not Scored)**

Shown as evidence only:

* **TTR** (Type-Token Ratio)
* **MTLD** (via lexicalrichness)

Not included in final score.

## Technologies Used

* Python
* Streamlit
* LanguageTool (grammar checking)
* VaderSentiment (sentiment analysis)
* LexicalRichness (vocabulary metrics)
* Optional: Gemini API for AI-generated feedback

## Project Structure

```
speakcheck-ai/
├── backend/
│   ├── scoring_engine.py
│   ├── gemini_client.py
│   ├── observability.py
│   ├── session_store.py
│   └── tests/
│       └── test_scoring.py
├── frontend/
│   └── streamlit_app.py
├── README.md
├── requirements.txt
└── .env.example
```

## Installation

1. Clone the repository:

```
git clone https://github.com/your-username/speakcheck-ai.git
cd speakcheck-ai
```

2. Create a virtual environment:

```
python -m venv venv
```

3. Activate the virtual environment:
   Windows:

```
venv\Scripts\activate
```

Mac/Linux:

```
source venv/bin/activate
```

4. Install dependencies:

```
pip install -r requirements.txt
```

5. Add your Gemini API key in a `.env` file:

```
GOOGLE_API_KEY=your_key_here
```

## Running the Application

Start the Streamlit frontend:

```
streamlit run frontend/streamlit_app.py
```

This opens the app at:

```
http://localhost:8501
```

## Running Tests

```
pytest backend/tests/test_scoring.py -q
```

## Future Improvements

* Semantic similarity using embeddings
* Audio input and automatic speech transcription
* Teacher dashboard for batch evaluation
* Exportable PDF feedback reports
* Multi-language support

## License
XYZ
