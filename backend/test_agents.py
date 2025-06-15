import os
from agents.code_change_analyzer import CodeChangeAnalyzerNode
from agents.fix_suggester import FixSuggesterNode
from agents.commit_metadata_extractor import CommitMetadataExtractorNode
from models.graph_state import GraphState, CommitMetadata

# Set your Gemini API key in the environment before running
os.environ["GOOGLE_API_KEY"] = os.getenv("GOOGLE_API_KEY", "YOUR_API_KEY_HERE")

# --- Test CommitMetadataExtractorNode (GitPython) ---
def test_commit_metadata_extractor():
    print("\nTesting CommitMetadataExtractorNode...")
    extractor = CommitMetadataExtractorNode()
    # Use HEAD commit for testing
    import git
    repo = git.Repo(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    commit_hash = repo.head.commit.hexsha
    state = GraphState(commit_hash=commit_hash, commit_metadata=None, summary=None, fix_suggestion=None, user_query=None)
    state = extractor.extract_metadata(state)
    print("Extracted commit metadata:", state["commit_metadata"])
    return state

# --- Test CodeChangeAnalyzerNode (Gemini) ---
def test_code_change_analyzer(state):
    print("\nTesting CodeChangeAnalyzerNode...")
    analyzer = CodeChangeAnalyzerNode()
    state = analyzer.analyze_changes(state)
    print("Summary:", state["summary"])
    return state

# --- Test FixSuggesterNode (Gemini) ---
def test_fix_suggester(state):
    print("\nTesting FixSuggesterNode...")
    suggester = FixSuggesterNode()
    # Add a user query for context
    state["user_query"] = "Are there any issues with this commit?"
    state = suggester.suggest_fix(state)
    print("Fix suggestion:", state["fix_suggestion"])
    return state

if __name__ == "__main__":
    # 1. Test GitPython commit metadata extraction
    state = test_commit_metadata_extractor()
    # 2. Test Gemini code change analyzer
    state = test_code_change_analyzer(state)
    # 3. Test Gemini fix suggester
    state = test_fix_suggester(state)