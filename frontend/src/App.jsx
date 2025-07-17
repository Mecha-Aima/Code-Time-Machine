import React, { useState } from 'react';
import ReactMarkdown from 'react-markdown';
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
      const res = await fetch(`${API_BASE}/commits?repo_url=${repoUrl}&count=10`);
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

  const formatCommitHash = (hash) => {
    return hash.substring(0, 8);
  };

  const formatDate = (dateStr) => {
    const date = new Date(dateStr);
    return {
      date: date.toLocaleDateString(),
      time: date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    };
  };

  return (
    <div className="ctm-container">
      <header className="ctm-header">
        <div className="ctm-header-content">
          <h1>Code Time Machine</h1>
          <p className="ctm-desc">Analyze any commit in a remote GitHub repository. Enter a repo URL and optionally a commit hash to get detailed commit analysis, or view commit history.</p>
          <button className="ctm-new-btn" onClick={handleNewAnalysis}>New Analysis</button>
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
            <div className="ctm-table-container">
              <table className="ctm-table">
                <thead>
                  <tr>
                    <th>Hash</th>
                    <th>Message</th>
                    <th>Author</th>
                    <th>Date</th>
                  </tr>
                </thead>
                <tbody>
                  {commitHistory.map((commit) => {
                    const { date, time } = formatDate(commit.date);
                    return (
                      <tr key={commit.hash}>
                        <td>
                          <code className="ctm-commit-hash">{formatCommitHash(commit.hash)}</code>
                        </td>
                        <td className="ctm-commit-message">{commit.message}</td>
                        <td className="ctm-commit-author">{commit.author}</td>
                        <td className="ctm-commit-date">
                          <div className="ctm-date-time">
                            <span className="ctm-date">{date}</span>
                            <span className="ctm-time">{time}</span>
                          </div>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </section>
        )}
        
        {analysisResult && (
          <section className="ctm-content-section ctm-analysis">
            <h2>Commit Analysis</h2>
            
            {analysisResult.commit_metadata && (
              <div className="ctm-analysis-section">
                <h3 className="ctm-section-title">📋 Commit Metadata</h3>
                <div className="ctm-metadata-grid">
                  <div className="ctm-metadata-item">
                    <span className="ctm-metadata-label">Hash:</span>
                    <code className="ctm-metadata-value">{analysisResult.commit_metadata.hash || 'N/A'}</code>
                  </div>
                  <div className="ctm-metadata-item">
                    <span className="ctm-metadata-label">Author:</span>
                    <span className="ctm-metadata-value">{analysisResult.commit_metadata.author || 'N/A'}</span>
                  </div>
                  <div className="ctm-metadata-item">
                    <span className="ctm-metadata-label">Date:</span>
                    <span className="ctm-metadata-value">
                      {analysisResult.commit_metadata.date ? 
                        new Date(analysisResult.commit_metadata.date).toLocaleString() : 
                        'N/A'
                      }
                    </span>
                  </div>
                  <div className="ctm-metadata-item ctm-metadata-message">
                    <span className="ctm-metadata-label">Message:</span>
                    <span className="ctm-metadata-value">{analysisResult.commit_metadata.message || 'N/A'}</span>
                  </div>
                </div>
              </div>
            )}
            
            {analysisResult.analysis && (
              <div className="ctm-analysis-section">
                <h3 className="ctm-section-title">🔍 Code Analysis</h3>
                <div className="ctm-markdown-content">
                  <ReactMarkdown>{analysisResult.analysis}</ReactMarkdown>
                </div>
              </div>
            )}
            
            {analysisResult.fix_suggestion && (
              <div className="ctm-analysis-section">
                <h3 className="ctm-section-title">🔧 Fix Suggestions</h3>
                <div className="ctm-markdown-content">
                  <ReactMarkdown>{analysisResult.fix_suggestion}</ReactMarkdown>
                </div>
              </div>
            )}
          </section>
        )}
      </main>
    </div>
  );
}

export default App;
