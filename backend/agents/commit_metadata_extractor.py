from models.graph_state import GraphState, CommitMetadata
from function_utils import *
import git
from datetime import datetime
import os

class CommitMetadataExtractorNode:
    def __init__(self, repo: git.Repo):
        try:
            self.repo = repo
        except git.InvalidGitRepositoryError:
            print(f"Error: Not a valid Git repository at {self.repo_path}")
            # In a real app, you might raise an exception or handle this more gracefully
            self.repo = None
        except Exception as e:
            print(f"Error initializing GitPython Repo: {e}")
            self.repo = None

    def extract_metadata(self, state: GraphState) -> GraphState:
        print("---EXTRACTING COMMIT METADATA---")
        if not self.repo:
            raise RuntimeError("Git repository not initialized properly.")

        commit_hash = state.get("commit_hash")
        if not commit_hash:
            raise ValueError("Commit hash not found in state")

        try:
            commit = self.repo.commit(commit_hash)
            author_name = commit.author.name
            # Convert commit.authored_datetime to ISO 8601 string format
            commit_date = commit.authored_datetime.isoformat()
            commit_message = commit.message.strip()
            files_changed = list(commit.stats.files.keys())

            # Get diff
            # For the initial commit, there's no parent, so diff against an empty tree
            if not commit.parents:
                EMPTY_TREE_SHA1 = "4b825dc642cb6eb9a060e54bf8d69288fbee4904"
                parent_commit = self.repo.tree(EMPTY_TREE_SHA1)
            else:
                parent_commit = commit.parents[0]
            
            diff_output = self.repo.git.diff(parent_commit.hexsha, commit.hexsha, unified=3)

            extracted_metadata = CommitMetadata(
                author=author_name,
                date=commit_date,
                message=commit_message,
                diff=diff_output,
                files_changed=files_changed
            )

            state["commit_metadata"] = extracted_metadata
            print(f"Extracted metadata for commit: {commit_hash}")
            print(f"  Author: {author_name}")
            print(f"  Date: {commit_date}")
            # print(f"  Message: {commit_message}") # Can be long
            # print(f"  Diff: {diff_output}") # Can be very long

        except git.exc.GitCommandError as e:
            print(f"Git command error: {e}")
            # Populate with error or empty data, or raise
            state["commit_metadata"] = CommitMetadata(author="Error", date="Error", message=f"Error: {e}", diff="Error")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            state["commit_metadata"] = CommitMetadata(author="Error", date="Error", message=f"Error: {e}", diff="Error")
        
        return state