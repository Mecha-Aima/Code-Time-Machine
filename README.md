# Code Time Machine

## Overview

**Code Time Machine** is a full-stack application that allows users to analyze any commit in a remote GitHub repository. It provides detailed commit analysis, including summaries, file-by-file breakdowns, context comparisons, and AI-powered suggestions for improvements or fixes. The system leverages FastAPI for the backend, React for the frontend, and integrates with Google Gemini for advanced code analysis and suggestions.

---

## Features

- **Analyze any commit** in a public GitHub repository
- **Detailed commit summaries** and file-by-file change breakdowns
- **Contextual analysis**: Understand what changed, why, and how it fits into the repo history
- **AI-powered fix suggestions**: Identify bugs, performance issues, and get improvement ideas
- **Commit history viewer**: Browse recent commits and select any for analysis
- **Modern, responsive UI** built with React

---

## Architecture

```
Frontend (React) <----REST----> Backend (FastAPI + LangGraph) <----> Google Gemini API
```

- **Frontend**: React app for user interaction, commit selection, and displaying analysis results
- **Backend**: FastAPI app orchestrating the analysis pipeline using LangGraph and custom agents
- **Agents**:
  - **CommitMetadataExtractorNode**: Extracts metadata and diffs for a given commit
  - **CodeChangeAnalyzerNode**: Uses Gemini to generate structured, in-depth commit analysis
  - **FixSuggesterNode**: Uses Gemini to suggest fixes, improvements, and highlight issues
  - **StoreResultsNode**: Persists analysis results in a local SQLite database

---

## Backend Setup

### 1. Python Environment

- Python 3.10+
- (Recommended) Create a virtual environment:
  ```bash
  cd backend
  python3 -m venv venv
  source venv/bin/activate
  ```

### 2. Install Dependencies

Create a `requirements.txt` with the following content:
```txt
fastapi
uvicorn
pydantic
gitpython
langgraph
google-generativeai
```
Install with:
```bash
pip install -r requirements.txt
```

- **Note:** You must set the `GOOGLE_API_KEY` environment variable for Gemini API access.
  ```bash
  export GOOGLE_API_KEY=your_google_api_key
  ```

### 3. Run the Backend

```bash
uvicorn main:app --reload
```
- The API will be available at `http://localhost:8000`

---

## Frontend Setup

### 1. Install Dependencies

```bash
cd frontend
npm install
```

### 2. Run the Frontend

```bash
npm start
```
- The app will be available at `http://localhost:3000`

---

## Usage

1. Start both the backend and frontend servers.
2. Open the frontend in your browser.
3. Enter a remote GitHub repository URL and (optionally) a commit hash.
4. View commit history, select a commit, and analyze it.
5. Review the AI-generated analysis and suggestions.

---

## API Endpoints

`POST /analyze-commit`
- **Request:** `{ "repo_url": "<repo_url>", "commit_hash": "<hash>" (optional) }`
- **Response:** `{ commit_metadata, analysis, fix_suggestion }`
- **Description:** Runs the full analysis pipeline on the specified commit.

**`GET /commits?repo_url=<repo_url>&count=10`**
- **Response:** List of recent commits with hash, message, author, and date.

**`POST /rm-repo`**
- **Description:** Deletes the currently cloned repository from the backend.

**`POST /query`**
- **Description:** (Placeholder) For future user-written queries.

---

## Project Structure

```
Code Time Machine/
  backend/
    agents/           # Analysis pipeline agents
    api/              # (Reserved for future API modules)
    main.py           # FastAPI app and pipeline orchestration
    function_utils.py # Repo management utilities
    models/           # State and metadata models
    results.db        # SQLite database for results
  frontend/
    src/              # React source code
    public/           # Static assets
    package.json      # Frontend dependencies
```

---

## Contributing

1. Fork the repository
2. Create a new branch (`git checkout -b feature/your-feature`)
3. Commit your changes
4. Push to your fork and open a Pull Request

---

## License

This project is licensed under the MIT License. 