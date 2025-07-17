import sqlite3
from models.graph_state import GraphState
import os

class StoreResultsNode:
    def __init__(self, db_path: str = "results.db"):
        self.db_path = db_path
        # Create the table once during initialization
        self._ensure_table_exists()

    def _ensure_table_exists(self):
        """Create the table and index if they don't exist"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS results (
                commit_hash TEXT PRIMARY KEY,
                commit_metadata TEXT,
                analysis TEXT
            )
        """)
        conn.commit()
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_commit_hash ON results (commit_hash)")
        conn.commit()
        conn.close()

    def store_results(self, state: GraphState) -> GraphState:
        try:
            # Create a new connection for this operation
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Extract values from state
            commit_hash = state["commit_hash"]
            commit_metadata = str(state["commit_metadata"])  # Convert to string for storage
            analysis = state["analysis"]

            # Store the results in the database
            cursor.execute("""
                INSERT OR REPLACE INTO results (commit_hash, commit_metadata, analysis)
                VALUES (?, ?, ?)
            """, (commit_hash, commit_metadata, analysis))
            conn.commit()

            print(f"Stored results for commit {commit_hash}")
            
        except Exception as e:
            print(f"Error storing results: {e}")
            raise e
        finally:
            # Always close the connection
            if 'conn' in locals():
                conn.close()

        return state


        