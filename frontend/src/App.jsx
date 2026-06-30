import React, { useState, useEffect } from 'react';
import './App.css';

const API_BASE = 'http://localhost:8000/api';

export default function App() {
  // Navigation
  const [activeTab, setActiveTab] = useState('dashboard');

  // API Data State
  const [metrics, setMetrics] = useState({
    total_feedback: 0,
    average_rating: 0,
    sentiment_distribution: { positive: 0, neutral: 0, negative: 0 },
    category_distribution: {},
    urgency_count: 0,
    resolution_rate: 0
  });
  
  const [trends, setTrends] = useState([]);
  const [feedback, setFeedback] = useState([]);
  const [totalFeedbackCount, setTotalFeedbackCount] = useState(0);
  const [currentPage, setCurrentPage] = useState(1);
  const [insights, setInsights] = useState({
    trending_keywords: [],
    anomalies: { volume_anomaly_detected: false, sentiment_anomaly_detected: false },
    ai_recommendations: []
  });
  
  const [integrations, setIntegrations] = useState([]);

  // Filter State
  const [search, setSearch] = useState('');
  const [filterSource, setFilterSource] = useState('');
  const [filterCategory, setFilterCategory] = useState('');
  const [filterSentiment, setFilterSentiment] = useState('');
  const [filterStatus, setFilterStatus] = useState('');
  const [filterUrgentOnly, setFilterUrgentOnly] = useState(false);

  // Status & Loaders
  const [loading, setLoading] = useState(false);
  const [syncing, setSyncing] = useState(false);
  const [training, setTraining] = useState(false);
  const [actioningId, setActioningId] = useState(null);
  const [notification, setNotification] = useState(null);

  // Simulator Inputs
  const [simTab, setSimTab] = useState('webhook');
  const [simWebhook, setSimWebhook] = useState({ text: '', rating: 5, email: '', name: '' });
  const [simEmail, setSimEmail] = useState({ from: '', subject: '', body: '' });
  const [csvFile, setCsvFile] = useState(null);

  // Show temporary toast notifications
  const showToast = (message, type = 'success') => {
    setNotification({ message, type });
    setTimeout(() => setNotification(null), 4000);
  };

  // Data Fetching Functions
  const fetchMetrics = async () => {
    try {
      const res = await fetch(`${API_BASE}/dashboard/metrics`);
      const data = await res.json();
      setMetrics(data);
    } catch (e) {
      console.error("Failed fetching metrics", e);
    }
  };

  const fetchTrends = async () => {
    try {
      const res = await fetch(`${API_BASE}/dashboard/trends?days=7`);
      const data = await res.json();
      setTrends(data);
    } catch (e) {
      console.error("Failed fetching trends", e);
    }
  };

  const fetchFeedback = async (page = 1) => {
    setLoading(true);
    try {
      const params = new URLSearchParams({
        page,
        limit: 10,
        search,
        source: filterSource,
        category: filterCategory,
        sentiment_label: filterSentiment,
        status: filterStatus
      });
      if (filterUrgentOnly) params.append('is_urgent', 'true');
      
      const res = await fetch(`${API_BASE}/feedback?${params.toString()}`);
      const data = await res.json();
      setFeedback(data.items);
      setTotalFeedbackCount(data.total);
      setCurrentPage(data.page);
    } catch (e) {
      console.error("Failed fetching feedback", e);
      showToast("Could not retrieve feedback feed.", "error");
    } finally {
      setLoading(false);
    }
  };

  const fetchInsights = async () => {
    try {
      const res = await fetch(`${API_BASE}/insights`);
      const data = await res.json();
      setInsights(data);
    } catch (e) {
      console.error("Failed fetching insights", e);
    }
  };

  const fetchIntegrations = async () => {
    try {
      const res = await fetch(`${API_BASE}/integrations`);
      const data = await res.json();
      setIntegrations(data);
    } catch (e) {
      console.error("Failed fetching integrations", e);
    }
  };

  // Load Initial Data
  useEffect(() => {
    fetchMetrics();
    fetchTrends();
    fetchIntegrations();
    fetchInsights();
  }, []);

  // Update feedback list when filters change
  useEffect(() => {
    const handler = setTimeout(() => {
      fetchFeedback(1);
    }, 250); // debounce typing
    return () => clearTimeout(handler);
  }, [search, filterSource, filterCategory, filterSentiment, filterStatus, filterUrgentOnly]);

  // Sync external mobile app store / G2 reviews
  const triggerSyncReviews = async () => {
    setSyncing(true);
    try {
      const res = await fetch(`${API_BASE}/simulation/sync-external`, { method: 'POST' });
      const data = await res.json();
      if (data.success) {
        showToast(`Synced ${data.count} new reviews from: App Store, Google Play, and G2!`);
        fetchMetrics();
        fetchTrends();
        fetchFeedback(1);
        fetchInsights();
      }
    } catch (e) {
      showToast("Sync failed. Check if API is running.", "error");
    } finally {
      setSyncing(false);
    }
  };

  // Update Item fields (e.g. status change, category tagging)
  const updateFeedbackStatus = async (itemId, status) => {
    try {
      const res = await fetch(`${API_BASE}/feedback/${itemId}`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ status })
      });
      const data = await res.json();
      if (data.id) {
        showToast(`Status updated to ${status}`);
        setFeedback(prev => prev.map(item => item.id === itemId ? data : item));
        fetchMetrics();
      }
    } catch (e) {
      showToast("Failed to update status", "error");
    }
  };

  const updateFeedbackCategory = async (itemId, category) => {
    try {
      const res = await fetch(`${API_BASE}/feedback/${itemId}`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ category })
      });
      const data = await res.json();
      if (data.id) {
        showToast(`Category updated to ${category}`);
        setFeedback(prev => prev.map(item => item.id === itemId ? data : item));
        fetchMetrics();
      }
    } catch (e) {
      showToast("Failed to update category", "error");
    }
  };

  // Trigger manually created Jira tasks / CRM syncs
  const createJira = async (itemId) => {
    setActioningId(itemId);
    try {
      const res = await fetch(`${API_BASE}/feedback/${itemId}/jira`, { method: 'POST' });
      const data = await res.json();
      if (data.success) {
        showToast(`Jira ticket created successfully: ${data.ticket_key}`);
        window.open(data.ticket_url, '_blank');
      }
    } catch (e) {
      showToast("Jira ticket creation failed", "error");
    } finally {
      setActioningId(null);
    }
  };

  const syncSalesforce = async (itemId) => {
    setActioningId(itemId);
    try {
      const res = await fetch(`${API_BASE}/feedback/${itemId}/salesforce`, { method: 'POST' });
      const data = await res.json();
      if (data.success) {
        showToast(`CRM sync completed: Lead ID ${data.lead_id}`);
        window.open(data.lead_url, '_blank');
      }
    } catch (e) {
      showToast("Salesforce CRM sync failed", "error");
    } finally {
      setActioningId(null);
    }
  };

  // Retrain the custom scikit-learn classifier
  const trainClassifier = async () => {
    setTraining(true);
    try {
      const res = await fetch(`${API_BASE}/model/train`, { method: 'POST' });
      const data = await res.json();
      if (data.success) {
        showToast(data.message);
      } else {
        showToast(data.detail || "Training failed", "error");
      }
    } catch (e) {
      showToast("Training failed. Make sure database contains tagged items.", "error");
    } finally {
      setTraining(false);
    }
  };

  // Toggle integrations settings
  const toggleIntegration = async (name, activeState, currentConfig) => {
    try {
      const res = await fetch(`${API_BASE}/integrations/${name}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          config_json: currentConfig,
          is_active: !activeState
        })
      });
      const data = await res.json();
      if (data.id) {
        showToast(`${name.toUpperCase()} integration updated.`);
        fetchIntegrations();
      }
    } catch (e) {
      showToast("Failed updating integration configurations", "error");
    }
  };

  // Submit mock feedback ingestion payload
  const handleWebhookSubmit = async (e) => {
    e.preventDefault();
    try {
      const res = await fetch(`${API_BASE}/feedback/ingest`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          text: simWebhook.text,
          source: 'web',
          rating: simWebhook.rating,
          metadata_json: { email: simWebhook.email, name: simWebhook.name }
        })
      });
      const data = await res.json();
      if (data.id) {
        showToast("Webhook form feedback ingested successfully!");
        setSimWebhook({ text: '', rating: 5, email: '', name: '' });
        fetchMetrics();
        fetchTrends();
        fetchFeedback(1);
        fetchInsights();
      }
    } catch (err) {
      showToast("Ingestion failed.", "error");
    }
  };

  const handleEmailSubmit = async (e) => {
    e.preventDefault();
    try {
      const res = await fetch(`${API_BASE}/feedback/ingest`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          text: `Subject: ${simEmail.subject}\n\n${simEmail.body}`,
          source: 'email',
          metadata_json: { sender: simEmail.from, subject: simEmail.subject }
        })
      });
      const data = await res.json();
      if (data.id) {
        showToast("Email parsed and ingested successfully!");
        setSimEmail({ from: '', subject: '', body: '' });
        fetchMetrics();
        fetchTrends();
        fetchFeedback(1);
        fetchInsights();
      }
    } catch (err) {
      showToast("Ingestion failed.", "error");
    }
  };

  const handleCsvUpload = async (e) => {
    e.preventDefault();
    if (!csvFile) return;

    const formData = new FormData();
    formData.append('file', csvFile);

    try {
      const res = await fetch(`${API_BASE}/feedback/upload`, {
        method: 'POST',
        body: formData
      });
      const data = await res.json();
      if (data.success) {
        showToast(`Imported ${data.count} items from CSV file.`);
        setCsvFile(null);
        // Clear input element
        document.getElementById('csvFileInput').value = '';
        fetchMetrics();
        fetchTrends();
        fetchFeedback(1);
        fetchInsights();
      }
    } catch (err) {
      showToast("CSV import failed", "error");
    }
  };

  // Helper values for rendering SVG Trend Lines
  const renderTrendSvg = () => {
    if (trends.length === 0) return null;
    
    const width = 500;
    const height = 180;
    const padding = 25;
    
    // Find max value in positive/negative/neutral to scale y-axis
    const maxVal = Math.max(
      ...trends.map(t => Math.max(t.positive_count, t.neutral_count, t.negative_count)), 
      2 // minimum ceiling
    );

    const pointsX = (index) => padding + (index * (width - padding * 2)) / (trends.length - 1);
    const pointsY = (val) => height - padding - (val * (height - padding * 2)) / maxVal;

    const createPath = (key) => {
      return trends.reduce((path, t, idx) => {
        const x = pointsX(idx);
        const y = pointsY(t[key]);
        return path + `${idx === 0 ? 'M' : 'L'} ${x} ${y} `;
      }, '');
    };

    const posPath = createPath('positive_count');
    const neuPath = createPath('neutral_count');
    const negPath = createPath('negative_count');

    return (
      <svg viewBox={`0 0 ${width} ${height}`} className="trend-svg-element" style={{ width: '100%', height: '100%' }}>
        {/* Y Axis Grid lines */}
        {[0, 0.5, 1].map((ratio, i) => {
          const y = padding + ratio * (height - padding * 2);
          return (
            <line key={i} x1={padding} y1={y} x2={width - padding} y2={y} stroke="rgba(255,255,255,0.05)" strokeDasharray="4" />
          );
        })}
        
        {/* Positive Line (Green) */}
        {posPath && <path d={posPath} fill="none" stroke="var(--color-positive)" strokeWidth="3" strokeLinecap="round" />}
        {/* Neutral Line (Blue/Gray) */}
        {neuPath && <path d={neuPath} fill="none" stroke="var(--color-neutral)" strokeWidth="2.5" strokeLinecap="round" />}
        {/* Negative Line (Red) */}
        {negPath && <path d={negPath} fill="none" stroke="var(--color-negative)" strokeWidth="3" strokeLinecap="round" />}

        {/* Data points markers */}
        {trends.map((t, idx) => {
          const x = pointsX(idx);
          return (
            <g key={idx}>
              <line x1={x} y1={padding} x2={x} y2={height - padding} stroke="rgba(255,255,255,0.03)" />
              {/* Pos marker */}
              <circle cx={x} cy={pointsY(t.positive_count)} r="4" fill="var(--color-positive)" />
              {/* Neg marker */}
              <circle cx={x} cy={pointsY(t.negative_count)} r="4" fill="var(--color-negative)" />
              {/* Date text labels */}
              {idx % 2 === 0 && (
                <text x={x} y={height - 5} fill="var(--text-muted)" fontSize="9" textAnchor="middle">
                  {t.date.split('-').slice(1).join('/')}
                </text>
              )}
            </g>
          );
        })}
      </svg>
    );
  };

  return (
    <div className="app-container">
      {/* Visual Header */}
      <header className="app-header">
        <div className="brand">
          <div className="brand-logo">FIS // Intelligence</div>
        </div>
        <div className="system-status">
          <div className="status-dot"></div>
          <span>Systems Operational</span>
          <button 
            className="btn btn-secondary" 
            style={{ padding: '6px 12px', fontSize: '12px', marginLeft: '12px' }}
            onClick={triggerSyncReviews}
            disabled={syncing}
          >
            {syncing ? 'Syncing...' : '🔄 Sync External APIs'}
          </button>
        </div>
      </header>

      {/* Main Workspace Frame */}
      <div className="app-main">
        {/* Side Dashboard Navigation Tabs */}
        <aside className="app-sidebar">
          <div 
            className={`nav-item ${activeTab === 'dashboard' ? 'active' : ''}`}
            onClick={() => setActiveTab('dashboard')}
          >
            📊 Analytics Dashboard
          </div>
          <div 
            className={`nav-item ${activeTab === 'feed' ? 'active' : ''}`}
            onClick={() => setActiveTab('feed')}
          >
            📥 Feedback Stream
          </div>
          <div 
            className={`nav-item ${activeTab === 'insights' ? 'active' : ''}`}
            onClick={() => {
              setActiveTab('insights');
              fetchInsights();
            }}
          >
            💡 Actions & Insights
          </div>
          <div 
            className={`nav-item ${activeTab === 'settings' ? 'active' : ''}`}
            onClick={() => {
              setActiveTab('settings');
              fetchIntegrations();
            }}
          >
            ⚙️ System Settings
          </div>
          <div 
            className={`nav-item ${activeTab === 'simulator' ? 'active' : ''}`}
            onClick={() => setActiveTab('simulator')}
          >
            🧪 Ingestion Sandbox
          </div>
        </aside>

        {/* Core Content Body Viewport */}
        <main className="app-content">
          
          {/* Dashboard View Tab */}
          {activeTab === 'dashboard' && (
            <div className="fade-in" style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
              <div className="metrics-grid">
                <div className="glass-panel metric-card">
                  <div className="metric-label">Total Ingested</div>
                  <div className="metric-val">{metrics.total_feedback}</div>
                </div>
                <div className="glass-panel metric-card">
                  <div className="metric-label">Average Rating</div>
                  <div className="metric-val">{metrics.average_rating ? `${metrics.average_rating} ⭐` : 'N/A'}</div>
                </div>
                <div className="glass-panel metric-card">
                  <div className="metric-label">Active Urgent Alerts</div>
                  <div className="metric-val" style={{ color: 'var(--color-negative)' }}>{metrics.urgency_count}</div>
                </div>
                <div className="glass-panel metric-card">
                  <div className="metric-label">Issue Resolution Rate</div>
                  <div className="metric-val" style={{ color: 'var(--color-positive)' }}>{metrics.resolution_rate}%</div>
                </div>
              </div>

              <div className="charts-row">
                {/* SVG Trend Line Chart */}
                <div className="glass-panel">
                  <div className="chart-header">
                    <div className="chart-title">Feedback Sentiment Trends (Last 7 Days)</div>
                    <div style={{ display: 'flex', gap: '8px', fontSize: '11px' }}>
                      <span style={{ color: 'var(--color-positive)' }}>● Positive</span>
                      <span style={{ color: 'var(--color-neutral)' }}>● Neutral</span>
                      <span style={{ color: 'var(--color-negative)' }}>● Negative</span>
                    </div>
                  </div>
                  <div style={{ height: '200px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                    {trends.length > 0 ? renderTrendSvg() : <div className="empty-state">No trend data available. Sync or submit feedback.</div>}
                  </div>
                </div>

                {/* Sentiment Distribution Ring/Pie Breakdown */}
                <div className="glass-panel" style={{ display: 'flex', flexDirection: 'column' }}>
                  <div className="chart-header">
                    <div className="chart-title">Sentiment Ratio Split</div>
                  </div>
                  <div style={{ flex: 1, display: 'flex', flexDirection: 'column', justifyContent: 'center', gap: '16px' }}>
                    {metrics.total_feedback > 0 ? (
                      <>
                        <div style={{ display: 'flex', height: '24px', borderRadius: '6px', overflow: 'hidden' }}>
                          <div 
                            style={{ 
                              width: `${(metrics.sentiment_distribution.positive / metrics.total_feedback) * 100}%`,
                              background: 'var(--color-positive)' 
                            }} 
                          />
                          <div 
                            style={{ 
                              width: `${(metrics.sentiment_distribution.neutral / metrics.total_feedback) * 100}%`,
                              background: 'var(--color-neutral)' 
                            }} 
                          />
                          <div 
                            style={{ 
                              width: `${(metrics.sentiment_distribution.negative / metrics.total_feedback) * 100}%`,
                              background: 'var(--color-negative)' 
                            }} 
                          />
                        </div>
                        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '10px', fontSize: '13px' }}>
                          <div>
                            <div style={{ color: 'var(--color-positive)', fontWeight: '600' }}>Positive</div>
                            <div style={{ fontSize: '18px', fontWeight: '700' }}>{Math.round((metrics.sentiment_distribution.positive / metrics.total_feedback) * 100)}%</div>
                            <div style={{ color: 'var(--text-muted)' }}>{metrics.sentiment_distribution.positive} count</div>
                          </div>
                          <div>
                            <div style={{ color: 'var(--color-neutral)', fontWeight: '600' }}>Neutral</div>
                            <div style={{ fontSize: '18px', fontWeight: '700' }}>{Math.round((metrics.sentiment_distribution.neutral / metrics.total_feedback) * 100)}%</div>
                            <div style={{ color: 'var(--text-muted)' }}>{metrics.sentiment_distribution.neutral} count</div>
                          </div>
                          <div>
                            <div style={{ color: 'var(--color-negative)', fontWeight: '600' }}>Negative</div>
                            <div style={{ fontSize: '18px', fontWeight: '700' }}>{Math.round((metrics.sentiment_distribution.negative / metrics.total_feedback) * 100)}%</div>
                            <div style={{ color: 'var(--text-muted)' }}>{metrics.sentiment_distribution.negative} count</div>
                          </div>
                        </div>
                      </>
                    ) : (
                      <div className="empty-state">No feedback recorded.</div>
                    )}
                  </div>
                </div>
              </div>

              {/* Categorization Bar Chart */}
              <div className="glass-panel">
                <div className="chart-header">
                  <div className="chart-title">Topic Distribution Breakdown</div>
                </div>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                  {Object.keys(metrics.category_distribution).length > 0 ? (
                    Object.entries(metrics.category_distribution)
                      .sort((a, b) => b[1] - a[1])
                      .map(([cat, count]) => {
                        const pct = Math.round((count / metrics.total_feedback) * 100);
                        return (
                          <div key={cat} style={{ display: 'flex', alignItems: 'center', gap: '16px', fontSize: '13px' }}>
                            <div style={{ width: '120px', fontWeight: '500', color: 'var(--text-secondary)' }}>{cat}</div>
                            <div style={{ flex: 1, height: '8px', background: 'rgba(255,255,255,0.05)', borderRadius: '99px', overflow: 'hidden' }}>
                              <div style={{ width: `${pct}%`, height: '100%', background: 'var(--primary)', borderRadius: '99px' }} />
                            </div>
                            <div style={{ width: '80px', textAlign: 'right', fontWeight: '600' }}>{count} ({pct}%)</div>
                          </div>
                        );
                      })
                  ) : (
                    <div className="empty-state">No category distributions recorded.</div>
                  )}
                </div>
              </div>
            </div>
          )}

          {/* Feedback Stream Tab */}
          {activeTab === 'feed' && (
            <div className="fade-in" style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
              
              {/* Filter controls header */}
              <div className="filter-bar">
                <input 
                  type="text" 
                  className="search-input" 
                  placeholder="🔍 Search comment content or category..."
                  value={search}
                  onChange={(e) => setSearch(e.target.value)}
                />
                
                <div className="filter-group">
                  <label>Channel:</label>
                  <select value={filterSource} onChange={(e) => setFilterSource(e.target.value)}>
                    <option value="">All</option>
                    <option value="web">Web Forms</option>
                    <option value="email">Email Box</option>
                    <option value="api_appstore">App Store</option>
                    <option value="api_googleplay">Google Play</option>
                    <option value="api_g2">G2 Reviews</option>
                    <option value="file">File Uploads</option>
                  </select>
                </div>

                <div className="filter-group">
                  <label>Topic:</label>
                  <select value={filterCategory} onChange={(e) => setFilterCategory(e.target.value)}>
                    <option value="">All</option>
                    <option value="General">General</option>
                    <option value="Bug">Bug</option>
                    <option value="Feature Request">Feature Request</option>
                    <option value="Pricing/Billing">Pricing/Billing</option>
                    <option value="UI/UX">UI/UX</option>
                    <option value="Support">Support</option>
                  </select>
                </div>

                <div className="filter-group">
                  <label>Sentiment:</label>
                  <select value={filterSentiment} onChange={(e) => setFilterSentiment(e.target.value)}>
                    <option value="">All</option>
                    <option value="positive">Positive</option>
                    <option value="neutral">Neutral</option>
                    <option value="negative">Negative</option>
                  </select>
                </div>

                <div className="filter-group">
                  <label>Status:</label>
                  <select value={filterStatus} onChange={(e) => setFilterStatus(e.target.value)}>
                    <option value="">All</option>
                    <option value="new">New</option>
                    <option value="assigned">Assigned</option>
                    <option value="resolved">Resolved</option>
                  </select>
                </div>

                <div 
                  className={`toggle-switch-container ${filterUrgentOnly ? 'active' : ''}`}
                  onClick={() => setFilterUrgentOnly(!filterUrgentOnly)}
                >
                  <div className="toggle-switch" />
                  <label style={{ fontSize: '12px', fontWeight: '500', color: 'var(--text-secondary)', cursor: 'pointer' }}>Urgent Only</label>
                </div>

                <div style={{ marginLeft: 'auto', display: 'flex', gap: '8px' }}>
                  <a href={`${API_BASE}/reports/export/csv`} download className="btn btn-secondary" style={{ padding: '8px 14px', fontSize: '13px' }}>
                    📊 Export CSV
                  </a>
                  <a href={`${API_BASE}/reports/export/html`} target="_blank" rel="noopener noreferrer" className="btn btn-secondary" style={{ padding: '8px 14px', fontSize: '13px' }}>
                    📄 HTML Report
                  </a>
                </div>
              </div>

              {/* Feed Card Streams */}
              {loading ? (
                <div className="loader"></div>
              ) : feedback.length > 0 ? (
                <div className="feed-list">
                  {feedback.map((item) => (
                    <div key={item.id} className="glass-panel feed-card">
                      <div className="feed-card-header">
                        <div className="feed-badges">
                          <span className={`badge badge-${item.sentiment_label?.slice(0,3)}`}>{item.sentiment_label}</span>
                          
                          {/* Category re-tagger selector dropdown */}
                          <select 
                            value={item.category} 
                            onChange={(e) => updateFeedbackCategory(item.id, e.target.value)}
                            style={{ padding: '2px 8px', fontSize: '11px', border: '1px solid var(--border-color)', height: '22px', borderRadius: '4px', background: 'rgba(255,255,255,0.03)' }}
                          >
                            <option value="General">General</option>
                            <option value="Bug">Bug</option>
                            <option value="Feature Request">Feature Request</option>
                            <option value="Pricing/Billing">Pricing/Billing</option>
                            <option value="UI/UX">UI/UX</option>
                            <option value="Support">Support</option>
                          </select>

                          {/* Source badge indicator */}
                          <span className={`badge badge-source badge-source-${item.source.split('_')[0]}`}>
                            {item.source.replace('api_', '').toUpperCase()}
                          </span>

                          {item.is_urgent && (
                            <span className="badge" style={{ background: 'var(--color-urgent-bg)', color: 'var(--color-urgent)' }}>
                              🚨 Urgent Alert
                            </span>
                          )}
                        </div>

                        <div className="feed-card-date">
                          {new Date(item.created_at).toLocaleString()}
                        </div>
                      </div>

                      <div className="feed-card-body">
                        {item.text}
                      </div>

                      <div className="feed-card-footer">
                        {/* Priority Score representation */}
                        <div className="urgency-score-bar-container">
                          <div className="urgency-score-label">Urgency Score: {item.urgency_score}/100</div>
                          <div className="urgency-progress-track">
                            <div 
                              className="urgency-progress-bar"
                              style={{ 
                                width: `${item.urgency_score}%`, 
                                background: item.is_urgent ? 'var(--color-negative)' : 'var(--primary)' 
                              }} 
                            />
                          </div>
                        </div>

                        {/* Actions buttons */}
                        <div className="feed-card-actions">
                          <select
                            value={item.status}
                            onChange={(e) => updateFeedbackStatus(item.id, e.target.value)}
                            style={{ height: '34px', fontSize: '13px', background: 'rgba(255,255,255,0.04)' }}
                          >
                            <option value="new">New</option>
                            <option value="assigned">Assigned</option>
                            <option value="resolved">Resolved</option>
                          </select>

                          <button 
                            className="btn btn-secondary" 
                            style={{ padding: '8px 12px', fontSize: '13px' }}
                            onClick={() => createJira(item.id)}
                            disabled={actioningId === item.id}
                          >
                            🛠️ Jira Ticket
                          </button>

                          <button 
                            className="btn btn-secondary" 
                            style={{ padding: '8px 12px', fontSize: '13px' }}
                            onClick={() => syncSalesforce(item.id)}
                            disabled={actioningId === item.id}
                          >
                            🤝 CRM Sync
                          </button>
                        </div>
                      </div>
                    </div>
                  ))}
                  
                  {/* Simple pagination */}
                  <div style={{ display: 'flex', justify: 'center', gap: '12px', marginTop: '10px' }}>
                    <button 
                      className="btn btn-secondary"
                      disabled={currentPage === 1}
                      onClick={() => fetchFeedback(currentPage - 1)}
                    >
                      ◀ Previous
                    </button>
                    <span style={{ alignSelf: 'center', fontSize: '14px', color: 'var(--text-secondary)' }}>
                      Page {currentPage} of {Math.ceil(totalFeedbackCount / 10) || 1}
                    </span>
                    <button 
                      className="btn btn-secondary"
                      disabled={currentPage >= Math.ceil(totalFeedbackCount / 10)}
                      onClick={() => fetchFeedback(currentPage + 1)}
                    >
                      Next ▶
                    </button>
                  </div>
                </div>
              ) : (
                <div className="glass-panel empty-state">No feedback matching the current filters.</div>
              )}
            </div>
          )}

          {/* Insights & Actions Tab */}
          {activeTab === 'insights' && (
            <div className="fade-in insights-grid">
              
              {/* Left Column: Anomalies and trending words */}
              <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
                <div className="glass-panel">
                  <h3 style={{ fontSize: '16px', fontWeight: '600', marginBottom: '16px' }}>System Anomalies</h3>
                  <div className="insight-anomalies">
                    {insights.anomalies.volume_anomaly_detected ? (
                      <div className="anomaly-alert-card danger">
                        <span className="anomaly-icon">🔥</span>
                        <div className="anomaly-content">
                          <h4>Volume Anomaly Flagged</h4>
                          <p>Feedback volume has spiked unexpectedly within the last 24 hours. Historical average is {insights.anomalies.avg_historical_volume} daily items, while recent volume is {insights.anomalies.recent_volume}.</p>
                        </div>
                      </div>
                    ) : (
                      <div className="anomaly-alert-card" style={{ color: 'var(--text-secondary)' }}>
                        <span className="anomaly-icon">✅</span>
                        <div className="anomaly-content">
                          <h4>Volume Ingestion Normal</h4>
                          <p>Ingestion limits and volume rates are stable.</p>
                        </div>
                      </div>
                    )}

                    {insights.anomalies.sentiment_anomaly_detected ? (
                      <div className="anomaly-alert-card danger">
                        <span className="anomaly-icon">📉</span>
                        <div className="anomaly-content">
                          <h4>Negative Sentiment Surge</h4>
                          <p>Negative comments have spiked to {insights.anomalies.negative_feedback_ratio}% of total input in the last 24 hours. Potential system malfunction or payment failure.</p>
                        </div>
                      </div>
                    ) : (
                      <div className="anomaly-alert-card" style={{ color: 'var(--text-secondary)' }}>
                        <span className="anomaly-icon">✅</span>
                        <div className="anomaly-content">
                          <h4>Sentiment Rates Normal</h4>
                          <p>Positive-to-negative sentiment indices are within average bounds.</p>
                        </div>
                      </div>
                    )}
                  </div>
                </div>

                <div className="glass-panel">
                  <h3 style={{ fontSize: '16px', fontWeight: '600', marginBottom: '8px' }}>Trending Keywords</h3>
                  <p style={{ fontSize: '12px', color: 'var(--text-muted)', marginBottom: '16px' }}>Words showing frequency spikes compared to historical norms.</p>
                  
                  {insights.trending_keywords.length > 0 ? (
                    <div className="keyword-cloud">
                      {insights.trending_keywords.map((kw, i) => (
                        <div className="keyword-tag" key={i}>
                          <span>{kw.word}</span>
                          <span className="spike-score">+{Math.round(kw.score * 100)}%</span>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <div className="empty-state" style={{ padding: '20px' }}>No trending keywords extracted yet.</div>
                  )}
                </div>
              </div>

              {/* Right Column: AI Insights recommendations list */}
              <div className="glass-panel">
                <h3 style={{ fontSize: '16px', fontWeight: '600', marginBottom: '8px' }}>Product Manager Recommendations</h3>
                <p style={{ fontSize: '12px', color: 'var(--text-muted)', marginBottom: '20px' }}>AI-generated action plans analyzed from latest feedback records.</p>
                
                <div className="recommendations-list">
                  {insights.ai_recommendations.length > 0 ? (
                    insights.ai_recommendations.map((rec, i) => (
                      <div key={i} className="glass-panel recommendation-card" style={{ borderLeft: '3px solid var(--primary)', background: 'rgba(255,255,255,0.01)' }}>
                        <div className="rec-header">
                          <span className="rec-title">{rec.title}</span>
                          <span className="badge badge-source">{rec.category}</span>
                        </div>
                        <div className="rec-description">{rec.description}</div>
                        <div className="rec-meta">
                          <span>Impact Score: {rec.impact_score}/100</span>
                          <button className="btn btn-secondary" style={{ padding: '4px 10px', fontSize: '11px' }} onClick={() => showToast("Insight added to roadmap!")}>
                            ➕ Add to Roadmap
                          </button>
                        </div>
                      </div>
                    ))
                  ) : (
                    <div className="empty-state">No AI recommendations available. Try synching reviews first.</div>
                  )}
                </div>
              </div>
            </div>
          )}

          {/* System Settings Tab */}
          {activeTab === 'settings' && (
            <div className="fade-in settings-grid">
              
              {/* Integrations manager */}
              <div className="glass-panel">
                <h3 style={{ fontSize: '16px', fontWeight: '600', marginBottom: '16px' }}>Business Integrations</h3>
                <div className="integrations-list">
                  {integrations.map((intg) => (
                    <div key={intg.id} className="integration-item">
                      <div className="integration-info">
                        <h4>{intg.name}</h4>
                        <p>{intg.name === 'slack' || intg.name === 'teams' ? 'Alerts webhook pipeline' : 'Workflow sync connector'}</p>
                      </div>
                      
                      <div className="integration-actions">
                        <div 
                          className={`toggle-switch-container ${intg.is_active ? 'active' : ''}`}
                          onClick={() => toggleIntegration(intg.name, intg.is_active, intg.config_json)}
                        >
                          <div className="toggle-switch" />
                          <label style={{ fontSize: '12px', fontWeight: '500', color: 'var(--text-secondary)', cursor: 'pointer' }}>
                            {intg.is_active ? 'Active' : 'Inactive'}
                          </label>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Machine Learning Trainer tool */}
              <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
                <div className="glass-panel trainer-card">
                  <div className="trainer-icon">🧠</div>
                  <h3 style={{ fontSize: '16px', fontWeight: '600' }}>Categorization ML Model</h3>
                  <p style={{ fontSize: '13px', color: 'var(--text-secondary)' }}>
                    Train the local scikit-learn classifier pipeline on your manually categorized feedback data to improve automation accuracy.
                  </p>
                  <button 
                    className="btn btn-primary"
                    style={{ margin: '10px auto 0 auto' }}
                    onClick={trainClassifier}
                    disabled={training}
                  >
                    {training ? 'Training Model...' : '🚀 Retrain ML Engine'}
                  </button>
                </div>
              </div>
            </div>
          )}

          {/* Ingestion Sandbox Simulator Tab */}
          {activeTab === 'simulator' && (
            <div className="fade-in glass-panel simulator-card">
              <h2 style={{ fontSize: '18px', fontWeight: '600', marginBottom: '8px' }}>Ingestion Sandbox Simulator</h2>
              <p style={{ fontSize: '13px', color: 'var(--text-secondary)', marginBottom: '24px' }}>
                Simulate form submissions or emails. Ingested messages are evaluated through clean-sentiment-categorization layers in real-time.
              </p>

              <div className="simulator-tabs">
                <button 
                  className={`sim-tab-btn ${simTab === 'webhook' ? 'active' : ''}`}
                  onClick={() => setSimTab('webhook')}
                >
                  🌐 Web Contact Form
                </button>
                <button 
                  className={`sim-tab-btn ${simTab === 'email' ? 'active' : ''}`}
                  onClick={() => setSimTab('email')}
                >
                  📧 Email Inbox Parser
                </button>
                <button 
                  className={`sim-tab-btn ${simTab === 'file' ? 'active' : ''}`}
                  onClick={() => setSimTab('file')}
                >
                  📁 CSV Batch Upload
                </button>
              </div>

              {simTab === 'webhook' && (
                <form onSubmit={handleWebhookSubmit}>
                  <div className="form-row">
                    <div className="form-group">
                      <label>Sender Full Name</label>
                      <input 
                        type="text" 
                        value={simWebhook.name} 
                        onChange={(e) => setSimWebhook({...simWebhook, name: e.target.value})} 
                        placeholder="John Doe" 
                      />
                    </div>
                    <div className="form-group">
                      <label>Sender Email Address</label>
                      <input 
                        type="email" 
                        value={simWebhook.email} 
                        onChange={(e) => setSimWebhook({...simWebhook, email: e.target.value})} 
                        placeholder="john.doe@company.com" 
                      />
                    </div>
                  </div>
                  <div className="form-row">
                    <div className="form-group">
                      <label>Feedback Rating (Stars)</label>
                      <select 
                        value={simWebhook.rating} 
                        onChange={(e) => setSimWebhook({...simWebhook, rating: parseInt(e.target.value)})}
                      >
                        <option value="5">5 Stars (Excellent)</option>
                        <option value="4">4 Stars (Good)</option>
                        <option value="3">3 Stars (Average)</option>
                        <option value="2">2 Stars (Poor)</option>
                        <option value="1">1 Star (Critical)</option>
                      </select>
                    </div>
                  </div>
                  <div className="form-group full-width">
                    <label>Contact Message (Feedback Text)</label>
                    <textarea 
                      rows="4" 
                      value={simWebhook.text}
                      onChange={(e) => setSimWebhook({...simWebhook, text: e.target.value})}
                      placeholder="Type details... include urgent keywords like 'broken' or 'crash' to trigger Slack alert rules."
                      required
                    />
                  </div>
                  <button type="submit" className="btn btn-primary" style={{ marginTop: '12px' }}>
                    🔌 Ingest Webhook Form
                  </button>
                </form>
              )}

              {simTab === 'email' && (
                <form onSubmit={handleEmailSubmit}>
                  <div className="form-row">
                    <div className="form-group">
                      <label>From: Email Sender</label>
                      <input 
                        type="email" 
                        value={simEmail.from} 
                        onChange={(e) => setSimEmail({...simEmail, from: e.target.value})} 
                        placeholder="customer@corporate.com" 
                        required 
                      />
                    </div>
                    <div className="form-group">
                      <label>Subject Header</label>
                      <input 
                        type="text" 
                        value={simEmail.subject} 
                        onChange={(e) => setSimEmail({...simEmail, subject: e.target.value})} 
                        placeholder="Billing issue / urgent support inquiry" 
                        required 
                      />
                    </div>
                  </div>
                  <div className="form-group full-width">
                    <label>Email Plain Body</label>
                    <textarea 
                      rows="4" 
                      value={simEmail.body} 
                      onChange={(e) => setSimEmail({...simEmail, body: e.target.value})} 
                      placeholder="Describe the complaint..." 
                      required 
                    />
                  </div>
                  <button type="submit" className="btn btn-primary" style={{ marginTop: '12px' }}>
                    📥 Ingest parsed Email
                  </button>
                </form>
              )}

              {simTab === 'file' && (
                <form onSubmit={handleCsvUpload} style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
                  <div className="form-group">
                    <label>Select Feedback CSV File</label>
                    <p style={{ fontSize: '11px', color: 'var(--text-muted)', marginBottom: '8px' }}>
                      CSV must contain header columns for text feedback (e.g. "text", "feedback", "message") and optional ratings ("rating", "stars").
                    </p>
                    <input 
                      id="csvFileInput"
                      type="file" 
                      accept=".csv"
                      onChange={(e) => setCsvFile(e.target.files[0])}
                      required 
                    />
                  </div>
                  <button type="submit" className="btn btn-primary" style={{ alignSelf: 'flex-start' }} disabled={!csvFile}>
                    📤 Upload CSV File
                  </button>
                </form>
              )}

            </div>
          )}

        </main>
      </div>

      {/* Floating Notifications Toasts */}
      {notification && (
        <div 
          className="fade-in"
          style={{ 
            position: 'fixed',
            bottom: '24px',
            right: '24px',
            background: notification.type === 'error' ? 'var(--color-negative)' : 'var(--bg-secondary)',
            border: '1px solid rgba(255, 255, 255, 0.1)',
            borderLeft: notification.type === 'error' ? 'none' : '3px solid var(--color-positive)',
            color: '#fff',
            padding: '16px 24px',
            borderRadius: '6px',
            boxShadow: '0 10px 30px rgba(0,0,0,0.5)',
            zIndex: 100,
            fontSize: '14px',
            fontWeight: '500'
          }}
        >
          {notification.message}
        </div>
      )}
    </div>
  );
}
