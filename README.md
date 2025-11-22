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
