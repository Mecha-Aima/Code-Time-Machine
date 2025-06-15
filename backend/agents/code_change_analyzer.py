from models.graph_state import GraphState
import os
from google import genai

class CodeChangeAnalyzerNode:
    def __init__(self):
        self.client = genai.Client(api_key=os.environ["GOOGLE_API_KEY"])

    def analyze_changes(self, state: GraphState) -> GraphState:
        print("---ANALYZING CODE CHANGES---")
        commit_metadata = state.get("commit_metadata")
        if not commit_metadata:
            raise ValueError("Commit metadata not found in state for analysis.")

        diff = commit_metadata.get("diff")
        if not diff:
            raise ValueError("Diff not found in commit metadata.")

        # TODO: Fill in the prompt for Gemini API
        prompt = f"""Explain the following code changes in plain English:

{diff}
"""
        try:
            response = self.client.models.generate_content(model="gemini-1.5-flash", contents=prompt)
            summary = response.text
        except Exception as e:
            print(f"Error generating summary with Gemini: {e}")
            summary = "Error generating summary."

        state["summary"] = summary
        print(f"Generated summary: {summary}")
        return state