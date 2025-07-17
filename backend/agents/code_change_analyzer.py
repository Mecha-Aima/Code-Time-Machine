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
            print("Error: Diff not found in commit metadata.")
            return state

        # TODO: Fill in the prompt for Gemini API
        prompt = f"""
You are a senior software engineer and expert code assistant.  
Your goal is to read the following git diff and produce an **in-depth, well-structured report** that helps developers understand exactly *what* changed, *why*, and *how* it fits into the repo history—without getting lost in the code.

---
## GOAL
Analyze the diff and generate:
1. A concise commit summary.
2. Detailed breakdown of changes by file/module:
   - What was added, removed, or modified.
   - How these changes affect logic, APIs, or data structures.
3. Context comparison:
   - Reference previous behavior and highlight modifications to logic, interfaces, dependencies.
---
## RETURN FORMAT (in Markdown)
```markdown
### 1. Commit summary  
*…*
\n\n
### 2. File‑by‑file details  
**path/to/file.ext**  
- **Change type**: added/removed/modified  
- **Details**:
  - *…*

Repeat for each changed file.
\n\n
### 3. Context & comparison  
- *…*
\n\n

## WARNINGS & RULES

* Focus on *intent and structure*, not trivial formatting changes.
* Avoid hallucinating code not present in the diff.
* Do not output code sections longer than needed—summarize instead.
* If uncertain, flag it as a **"potential"** issue.
* Keep analysis tight, readable, and developer‑friendly.

The code changes are:
{diff}
        """
        try:
            response = self.client.models.generate_content(model="gemini-2.5-flash", contents=prompt)
            analysis = response.text
        except Exception as e:
            print(f"Error generating analysis with Gemini: {e}")
            analysis = "Error generating analysis."

        state["analysis"] = analysis
        print(f"Generated analysis: {analysis}")
        return state