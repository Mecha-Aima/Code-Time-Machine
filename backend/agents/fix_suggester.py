from models.graph_state import GraphState
import os
from google import genai

class FixSuggesterNode:
    def __init__(self):
        self.client = genai.Client(api_key=os.environ["GOOGLE_API_KEY"])

    def suggest_fix(self, state: GraphState) -> GraphState:
        print("---SUGGESTING FIXES---")
        analysis = state.get("analysis")
        diff = state.get("commit_metadata", {}).get("diff") # Safely get diff
        commit_message = state.get("commit_metadata", {}).get("message") # Safely get commit message
        user_query = state.get("user_query")

        if not analysis:
            raise ValueError("Analysis not found in state for fix suggestion.")
        if not diff:
            print("Warning: Diff not found in state for fix suggestion.")
        if not commit_message:
            print("Warning: Commit message not found in state for fix suggestion.")

        prompt = f"""Based on the following information:
Analysis of changes: {analysis}
Code diff: {diff if diff else 'N/A'}
Commit message: {commit_message if commit_message else 'N/A'}
User query: {user_query if user_query else 'N/A'}

## TASKS:
- Identify potential bugs, performance implications, edge cases, or backward‑compatibility concerns in the code changes.
- Suggest a hypothetical fix in code form (it can be partial).
- Suggest concise code improvements, refactoring ideas, test additions, or documentation gaps.

If there are no issues or suggestions, just say "No issues found."
"""
        
        try:
            response = self.client.models.generate_content(model="gemini-2.0-flash", contents=prompt)
            fix_suggestion = response.text
        except Exception as e:
            print(f"Error generating fix suggestion with Gemini: {e}")
            fix_suggestion = "Error generating fix suggestion."

        state["fix_suggestion"] = fix_suggestion
        print(f"Generated fix suggestion: {fix_suggestion}")
        return state