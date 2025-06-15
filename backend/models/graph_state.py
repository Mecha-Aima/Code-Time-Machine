from typing import TypedDict, Optional

class CommitMetadata(TypedDict):
    author: str
    date: str
    message: str
    diff: str

class GraphState(TypedDict):
    commit_hash: str
    commit_metadata: CommitMetadata
    summary: Optional[str]
    fix_suggestion: Optional[str]
    user_query: Optional[str]