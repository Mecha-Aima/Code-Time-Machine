from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import git
import os # Required for repo_path in CommitMetadataExtractorNode
from langgraph.graph import StateGraph, END

from .models.graph_state import GraphState
from .agents.commit_metadata_extractor import CommitMetadataExtractorNode
from .agents.code_change_analyzer import CodeChangeAnalyzerNode
from .agents.fix_suggester import FixSuggesterNode

# Initialize FastAPI app
app = FastAPI()

# Determine repo_path once, assuming it's the project root for now
# This should ideally be configurable
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

# Initialize nodes with the determined repo_path
metadata_extractor = CommitMetadataExtractorNode(repo_path=PROJECT_ROOT)
code_analyzer = CodeChangeAnalyzerNode()
fix_suggester = FixSuggesterNode()

# Define the graph
workflow = StateGraph(GraphState)

# Add nodes to the graph
workflow.add_node("metadata_extractor", metadata_extractor.extract_metadata)
workflow.add_node("code_analyzer", code_analyzer.analyze_changes)
workflow.add_node("fix_suggester", fix_suggester.suggest_fix)

# Define the edges
workflow.set_entry_point("metadata_extractor")
workflow.add_edge("metadata_extractor", "code_analyzer")
workflow.add_edge("code_analyzer", "fix_suggester")
workflow.add_edge("fix_suggester", END)

# Compile the graph
graph = workflow.compile()

# Example of how to run the graph (for testing purposes)
if __name__ == "__main__":
    # This is a basic example. In a real application, 
    # you'd get the commit_hash from a Git hook, API request, etc.
    initial_state = GraphState(
        commit_hash="test_commit_123",
        commit_metadata=None, # type: ignore
        summary=None,
        fix_suggestion=None,
        user_query="How can I improve this code?"
    )

    print("Running LangGraph pipeline...")
    # Note: LangGraph's stream method returns an iterator.
    # We'll consume it to see the final state.
    final_state = None
    for s in graph.stream(initial_state):
        # s is a dictionary where keys are node names and values are their outputs
        print(f"\nState after node {list(s.keys())[0]}:")
        print(s)
        final_state = s[list(s.keys())[0]] # Get the state from the last executed node
    
    print("\n---FINAL STATE---")
    if final_state:
        print(f"Commit Hash: {final_state.get('commit_hash')}")
        print(f"Commit Metadata: {final_state.get('commit_metadata')}")
        print(f"Summary: {final_state.get('summary')}")
        print(f"Fix Suggestion: {final_state.get('fix_suggestion')}")
        print(f"User Query: {final_state.get('user_query')}")
    else:
        print("Graph execution did not produce a final state.")

# To run this example: GOOGLE_API_KEY=your_key_here python -m backend.main
# (You'll need to set the GOOGLE_API_KEY environment variable, though it's not used by placeholders yet)

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import git
import os # Required for repo_path in CommitMetadataExtractorNode

# ... (keep existing imports and graph setup) ...

class AnalyzeCommitRequest(BaseModel):
    commit_hash: str

class QueryRequest(BaseModel):
    query: str

# Determine repo_path once, assuming it's the project root for now
# This should ideally be configurable
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

@app.post("/analyze-commit")
async def analyze_commit_endpoint(request: AnalyzeCommitRequest):
    initial_state_api = GraphState(
        commit_hash=request.commit_hash,
        commit_metadata=None, # type: ignore
        summary=None,
        fix_suggestion=None,
        user_query=None # User query can be part of a different flow or added later
    )
    
    final_api_state = None
    try:
        # Use ainvoke for a single final state, which is more suitable for an API endpoint
        # Ensure your graph nodes are compatible with async if using ainvoke directly in an async context
        # For simplicity, if graph.stream is synchronous, wrap it or use a background task.
        # Assuming graph.stream is okay to call like this for now based on original example.
        for s in graph.stream(initial_state_api, {"recursion_limit": 10}): # Added recursion_limit for safety
            # The final state is the accumulation of all node outputs
            # We need to merge the states from the stream
            if final_api_state is None:
                final_api_state = {}
            final_api_state.update(s[list(s.keys())[0]])

        if final_api_state and final_api_state.get("commit_metadata") and final_api_state.get("commit_metadata").get("author") == "Error":
             raise HTTPException(status_code=500, detail=f"Error processing commit: {final_api_state.get('commit_metadata').get('message')}")

        # Ensure all expected keys are present, providing defaults if not
        return {
            "commit_metadata": final_api_state.get("commit_metadata"),
            "summary": final_api_state.get("summary"),
            "fix_suggestion": final_api_state.get("fix_suggestion")
        }
    except git.exc.GitCommandError as e:
        raise HTTPException(status_code=400, detail=f"Invalid commit hash or Git error: {e}")
    except Exception as e:
        # Log the exception e for debugging
        print(f"Unhandled error in analyze_commit_endpoint: {e}")
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {e}")

@app.get("/commits")
async def get_commits_endpoint(count: int = 10):
    try:
        repo = git.Repo(PROJECT_ROOT)
        commits = list(repo.iter_commits(max_count=count))
        commit_list = [
            {"hash": commit.hexsha, "message": commit.message.strip(), "author": commit.author.name, "date": commit.authored_datetime.isoformat()}
            for commit in commits
        ]
        return commit_list
    except git.InvalidGitRepositoryError:
        raise HTTPException(status_code=500, detail="Not a valid Git repository")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching commits: {e}")

@app.post("/query")
async def query_endpoint(request: QueryRequest):
    # Placeholder for user-written queries
    # This will be implemented later
    return {"message": "Query endpoint not yet implemented", "received_query": request.query}