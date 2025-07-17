import React, { useState } from 'react';
import './App.css';

const API_BASE = 'http://localhost:8000';

function App() {
  const [repoUrl, setRepoUrl] = useState('');
  const [commitHash, setCommitHash] = useState('');
  const [commitHistory, setCommitHistory] = useState([]);
  const [analysisResult, setAnalysisResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleNewAnalysis = async () => {
    setRepoUrl('');
    setCommitHash('');
    setCommitHistory([]);
    setAnalysisResult(null);
    setError('');
    setLoading(true);
    try {
      await fetch(`${API_BASE}/rm-repo`, { method: 'POST' });
    } catch (e) {
      // Ignore errors for repo deletion
      setError(e.message);
    }
    setLoading(false);
  };

  const handleCommitHistory = async () => {
    setLoading(true);
    setError('');
    try {
      const res = await fetch(`${API_BASE}/commits?count=10`);
      if (!res.ok) throw new Error('Failed to fetch commit history');
      const data = await res.json();
      setCommitHistory(data);
    } catch (e) {
      setError(e.message);
    }
    setLoading(false);
  };

  const handleAnalyzeCommit = async () => {
    setLoading(true);
    setError('');
    setAnalysisResult(null);
    try {
      const res = await fetch(`${API_BASE}/analyze-commit`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ repo_url: repoUrl, commit_hash: commitHash || null })
      });
      if (!res.ok) throw new Error('Failed to analyze commit');
      const data = await res.json();
      setAnalysisResult(data);
      console.log(data);
    } catch (e) {
      setError(e.message);
    }
    setLoading(false);
  };

  return (
    <div className="ctm-container">
      <header className="ctm-header">
        <div className="ctm-header-content">
          <button className="ctm-new-btn" onClick={handleNewAnalysis}>New Analysis</button>
          <h1>Code Time Machine</h1>
          <p className="ctm-desc">Analyze any commit in a remote GitHub repository. Enter a repo URL and optionally a commit hash to get detailed commit analysis, or view commit history.</p>
        </div>
      </header>
      
      <main className="ctm-main">
        <div className="ctm-form-container">
          <div className="ctm-form">
            <div className="ctm-form-group">
              <label htmlFor="repo-url">Remote Repo URL</label>
              <input
                id="repo-url"
                type="text"
                placeholder="e.g. https://github.com/user/repo"
                value={repoUrl}
                onChange={e => setRepoUrl(e.target.value)}
                className="ctm-input"
              />
            </div>
            
            <div className="ctm-form-group">
              <label htmlFor="commit-hash">
                Commit Hash <span className="ctm-optional">(optional, defaults to most recent)</span>
              </label>
              <input
                id="commit-hash"
                type="text"
                placeholder="e.g. 90e5a216..."
                value={commitHash}
                onChange={e => setCommitHash(e.target.value)}
                className="ctm-input"
              />
            </div>
            
            <div className="ctm-btn-row">
              <button
                className="ctm-btn"
                onClick={handleCommitHistory}
                disabled={!!commitHash || loading}
              >
                Commit History
              </button>
              <button
                className="ctm-btn ctm-analyze"
                onClick={handleAnalyzeCommit}
                disabled={!repoUrl || loading}
              >
                Analyze Commit
              </button>
            </div>
          </div>
        </div>

        {loading && <div className="ctm-loading">Loading...</div>}
        {error && <div className="ctm-error">{error}</div>}
        
        {commitHistory.length > 0 && (
          <section className="ctm-content-section ctm-history">
            <h2>Commit History</h2>
            <ul>
              {commitHistory.map((c, i) => (
                <li key={c.hash} className="ctm-commit">
                  <span className="ctm-commit-hash">{c.hash}</span>
                  <span className="ctm-commit-msg">{c.message}</span>
                  <span className="ctm-commit-author">{c.author}</span>
                  <span className="ctm-commit-date">{new Date(c.date).toLocaleString()}</span>
                </li>
              ))}
            </ul>
          </section>
        )}
        
        {analysisResult && (
          <section className="ctm-content-section ctm-analysis">
            <h2>Commit Analysis</h2>
            <pre>{JSON.stringify(analysisResult, null, 2)}</pre>
          </section>
        )}
      </main>
    </div>
  );
}

export default App;
