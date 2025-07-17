from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
import git
import os
from langgraph.graph import StateGraph, END
import asyncio
from fastapi.middleware.cors import CORSMiddleware

from models.graph_state import GraphState
from agents import FixSuggesterNode, StoreResultsNode, CodeChangeAnalyzerNode, CommitMetadataExtractorNode
from function_utils import *

REPO_PATH = os.path.join(os.path.dirname(__file__), 'cloned_repo')

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def init_graph(repo: git.Repo):
    metadata_extractor = CommitMetadataExtractorNode(repo)
    code_analyzer = CodeChangeAnalyzerNode()
    fix_suggester = FixSuggesterNode()
    store_results = StoreResultsNode()

    workflow = StateGraph(GraphState)

    workflow.add_node("metadata_extractor", metadata_extractor.extract_metadata)
    workflow.add_node("code_analyzer", code_analyzer.analyze_changes)
    workflow.add_node("fix_suggester", fix_suggester.suggest_fix)
    workflow.add_node("store_results", store_results.store_results)

    workflow.set_entry_point("metadata_extractor")
    workflow.add_edge("metadata_extractor", "code_analyzer")
    workflow.add_edge("code_analyzer", "fix_suggester")
    workflow.add_edge("fix_suggester", "store_results")
    workflow.add_edge("store_results", END)

    graph = workflow.compile()

    return graph


async def main():
    initial_state = GraphState(
        commit_hash="90e5a21687fef349a765562ccb33600afec28d04",
        commit_metadata=None, # type: ignore
        analysis=None,
        fix_suggestion=None,
        user_query="How can I improve this code?"
    )

    graph = init_graph(REPO_PATH)

    print("🔄 ---Running LangGraph pipeline---")
    final_state = None
    async for s in graph.astream(initial_state):
        # s is a dictionary where keys are node names and values are their outputs
        print(f"\nState after node {list(s.keys())[0]}:")
        print(s)
        final_state = s[list(s.keys())[0]] # Get the state from the last executed node
    
    print("\n🟥 ---FINAL STATE---")
    if final_state:
        print(f"Commit Hash: {final_state.get('commit_hash')}")
        print(f"Commit Metadata: {final_state.get('commit_metadata')}")
        print(f"Analysis: {final_state.get('analysis')}")
        print(f"Fix Suggestion: {final_state.get('fix_suggestion')}")
        print(f"User Query: {final_state.get('user_query')}")
    else:
        print("Graph execution did not produce a final state.")

# Example of how to run the graph (for testing purposes)
if __name__ == "__main__":
    asyncio.run(main())
    delete_cloned_repo(REPO_PATH)


# FastAPI Endpoints
class AnalyzeCommitRequest(BaseModel):
    commit_hash: Optional[str]
    repo_url: str

class QueryRequest(BaseModel):
    query: str



@app.post("/analyze-commit")
async def analyze_commit_endpoint(request: AnalyzeCommitRequest):
    print("🔄 ---Running LangGraph pipeline---")
    try:
        repo = clone_repo(request.repo_url, REPO_PATH)
    except git.InvalidGitRepositoryError:
        print(f"Error: Not a valid Git repository at {request.repo_url}")
        raise HTTPException(status_code=400, detail=f"Not a valid Git repository at {request.repo_url}")
    except Exception as e:
        print(f"Error initializing GitPython Repo: {e}")
        raise HTTPException(status_code=500, detail=f"Error initializing GitPython Repo: {e}")
        
    if request.commit_hash is None:
        commit = get_most_recent_commit(repo)
        request.commit_hash = commit.hexsha
    
    initial_state_api = GraphState(
        commit_hash=request.commit_hash,
        commit_metadata=None, # type: ignore
        analysis=None,
        fix_suggestion=None,
        user_query=None,
    )

    graph = init_graph(repo)
    
    final_api_state = None
    try:
        async for s in graph.astream(initial_state_api, {"recursion_limit": 10}): # Added recursion_limit for safety
            # The final state is the accumulation of all node outputs
            # We need to merge the states from the stream
            if final_api_state is None:
                final_api_state = {}
            final_api_state.update(s[list(s.keys())[0]])
            print("✅ Processed node: ", s[list(s.keys())[0]])

        if final_api_state and final_api_state.get("commit_metadata") and final_api_state.get("commit_metadata").get("author") == "Error":
             raise HTTPException(status_code=500, detail=f"Error processing commit: {final_api_state.get('commit_metadata').get('message')}")

        # Ensure all expected keys are present, providing defaults if not
        return {
            "commit_metadata": final_api_state.get("commit_metadata"),
            "analysis": final_api_state.get("analysis"),
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
        repo = git.Repo(REPO_PATH)
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


@app.post("/rm-repo")
async def rm_repo_endpoint():
    delete_cloned_repo(REPO_PATH)
    return {"message": "Repo deleted successfully"}

@app.get("/")
async def root():
    return {"message": "Code Time Machine"}