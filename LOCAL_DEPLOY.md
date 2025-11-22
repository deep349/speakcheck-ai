## LOCAL_DEPLOY.md

### *Local Setup & Deployment Guide for SpeakCheck AI*

This document explains how to install, configure, and run **SpeakCheck AI** on your local machine (Windows, macOS, or Linux).

## 1. Prerequisites

Make sure you have the following installed:

* **Python 3.9+**
* **pip** (comes with Python)
* **Git**
* (Optional) **Java** — required for LanguageTool grammar checking
  If absent, grammar scoring will use defaults or LLM fallback.

## 2. Clone the Repository

```bash
git clone https://github.com/your-username/speakcheck-ai.git
cd speakcheck-ai
```

Replace `your-username` with your actual GitHub username.

## 3. Create and Activate Virtual Environment

## Windows (PowerShell)

```powershell
py -m venv venv
.\venv\Scripts\Activate.ps1
```

If PowerShell blocks activation:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\venv\Scripts\Activate.ps1
```

## macOS / Linux

```bash
python3 -m venv venv
source venv/bin/activate
```

## 4. Install Dependencies

```bash
pip install -r requirements.txt
```

If you see warnings for missing Java (for LanguageTool), you can still run the app — grammar checks will fallback.

## 5. Set Up Environment Variables

Create a `.env` file in the project root:

### `.env`

```
GOOGLE_API_KEY=your_gemini_api_key_here
```

This enables LLM-based grammar & engagement feedback.
If left empty, the app will still run with rule-based analysis.


## 6. Run the Streamlit Application

From the project root:

```bash
streamlit run frontend/streamlit_app.py
```

You should now see:

```
Local URL: http://localhost:8501
```

Open the link in your browser.

Paste a transcript, enter duration (seconds), and click **Analyze**.

---

## 7. Running Tests

To run unit tests:

```bash
pytest backend/tests/test_scoring.py -q
```

## 8. Optional: Windows One-Click Run Script

Create a file named `run_local.bat`:

```
@echo off
call venv\Scripts\activate
streamlit run frontend\streamlit_app.py
pause
```

Double-clicking `run_local.bat` will start the app.

## 9. Troubleshooting

###  *ModuleNotFoundError: backend*

Run Streamlit **from project root**, not from inside another folder.

Correct:

```bash
streamlit run frontend/streamlit_app.py
```

### *LanguageTool errors*

Install Java (JDK or JRE) if you want grammar scoring.
Otherwise, grammar score defaults to non-Java mode.

### *Gemini API authentication issues*

* Check `.env` spelling: `GOOGLE_API_KEY=...`
* Make sure your key is for Gemini models (not deprecated ones)

### *Streamlit not found*

Install dependencies again:

```bash
pip install -r requirements.txt
```

## 10. Summary

After following this guide, you will have:

* Virtual environment created
* Dependencies installed
* Environment variables configured
* Streamlit frontend running locally on `localhost:8501`
* Optional LLM scoring enabled
* Tests runnable via pytest
