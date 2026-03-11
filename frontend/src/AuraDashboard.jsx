import React, { useState, useEffect } from "react";
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";
import {
  AlertCircle,
  Activity,
  Users,
  TrendingUp,
  Bell,
  Clock,
  Shield,
} from "lucide-react";
import "./AuraDashboard.css";

const API_URL = process.env.REACT_APP_API_URL || "http://localhost:8000";

const AuraDashboard = () => {
  const [activeTab, setActiveTab] = useState("overview");
  const [students, setStudents] = useState([]);
  const [alerts, setAlerts] = useState([]);
  const [analytics, setAnalytics] = useState(null);
  const [selectedStudent, setSelectedStudent] = useState(null);
  const [notifications, setNotifications] = useState([]);
  const [isLive, setIsLive] = useState(false);
  const [currentTime, setCurrentTime] = useState(new Date());
  const [riskFilter, setRiskFilter] = useState(null); // null = show all

  // Fetch data on component mount
  useEffect(() => {
    fetchStudents();
    fetchAlerts();
    fetchAnalytics();

    // Connect to live feed
    connectToLiveFeed();

    // Update clock every second
    const timer = setInterval(() => setCurrentTime(new Date()), 1000);

    return () => clearInterval(timer);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const fetchStudents = async () => {
    try {
      const response = await fetch(`${API_URL}/api/students?limit=100`);
      const data = await response.json();
      console.log("Fetched students:", data.length, "students");
      console.log("Sample student:", data[0]);
      setStudents(data);
    } catch (error) {
      console.error("Error fetching students:", error);
    }
  };

  const fetchAlerts = async () => {
    try {
      const response = await fetch(`${API_URL}/api/alerts`);
      const data = await response.json();
      setAlerts(data);
    } catch (error) {
      console.error("Error fetching alerts:", error);
    }
  };

  const fetchAnalytics = async () => {
    try {
      const response = await fetch(`${API_URL}/api/alerts/analytics`);
      const data = await response.json();
      setAnalytics(data);
    } catch (error) {
      console.error("Error fetching analytics:", error);
    }
  };

  const connectToLiveFeed = () => {
    const eventSource = new EventSource(`${API_URL}/api/feed/live`);

    eventSource.onopen = () => {
      setIsLive(true);
      console.log("Live feed connected");
    };

    eventSource.onmessage = (event) => {
      const data = JSON.parse(event.data);

      if (data.type === "new_predictions") {
        setNotifications((prev) => [
          {
            message: `${data.count} new predictions received`,
            time: new Date(),
          },
          ...prev.slice(0, 9),
        ]);
        fetchStudents();
        fetchAlerts();
        fetchAnalytics();
      }
    };

    eventSource.onerror = () => {
      setIsLive(false);
      eventSource.close();
      // Reconnect after 5 seconds
      setTimeout(connectToLiveFeed, 5000);
    };
  };

  const assignCounsellor = async (studentId) => {
    try {
      const encodedStudentId = encodeURIComponent(studentId);
      await fetch(`${API_URL}/api/alerts/${encodedStudentId}/assign`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          counsellor_id: "dr.patel",
          notes: "Initial assignment for follow-up",
        }),
      });
      fetchAlerts();
    } catch (error) {
      console.error("Error assigning counsellor:", error);
    }
  };

  const snoozeAlert = async (studentId) => {
    try {
      const encodedStudentId = encodeURIComponent(studentId);
      await fetch(`${API_URL}/api/alerts/snooze/${encodedStudentId}`, {
        method: "POST",
      });
      fetchAlerts();
    } catch (error) {
      console.error("Error snoozing alert:", error);
    }
  };

  const viewStudentDetail = async (studentId) => {
    console.log("Fetching details for student ID:", studentId);
    
    if (!studentId || studentId.length < 5) {
      console.error("Invalid student ID:", studentId);
      alert(`Invalid student ID: ${studentId}`);
      return;
    }
    
    try {
      // URL-encode the student ID to handle special characters like #
      const encodedStudentId = encodeURIComponent(studentId);
      const url = `${API_URL}/api/students/${encodedStudentId}`;
      console.log("Fetching from URL:", url);
      
      const response = await fetch(url);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      console.log("Received student data:", data);
      
      // Validate data structure before setting
      if (data && data.latest_risk && data.behavioral_history) {
        setSelectedStudent(data);
      } else {
        console.error("Invalid student data structure:", data);
        alert("Unable to load student details. Please try again.");
      }
    } catch (error) {
      console.error("Error fetching student details:", error);
      alert(`Failed to fetch student details for ${studentId}. Error: ${error.message}`);
    }
  };

  const getRiskBadgeColor = (level) => {
    const colors = {
      critical: "#dc2626",
      high: "#ea580c",
      medium: "#ca8a04",
      low: "#16a34a",
    };
    return colors[level] || "#6b7280";
  };

  const getRiskCount = (level) => {
    if (!analytics?.risk_distribution) return 0;
    return analytics.risk_distribution[level]?.count || 0;
  };

  const toggleRiskFilter = (level) => {
    // Toggle filter: if same level is clicked, clear filter; otherwise set new filter
    setRiskFilter(riskFilter === level ? null : level);
  };

  const getFilteredStudents = () => {
    if (!riskFilter) return students;
    return students.filter(student => student.risk_level === riskFilter);
  };

  return (
    <div className="aura-dashboard">
      {/* Top Bar */}
      <header className="top-bar">
        <div className="logo-section">
          <Shield size={32} className="logo-icon" />
          <div>
            <h1>AURA</h1>
            <p className="subtitle">Student Wellness Intelligence</p>
          </div>
        </div>

        <div className="status-section">
          <div className={`live-indicator ${isLive ? "active" : ""}`}>
            <span className="live-dot"></span>
            {isLive ? "LIVE" : "OFFLINE"}
          </div>

          <div className="clock">
            <Clock size={16} />
            <span>{currentTime.toLocaleTimeString()}</span>
          </div>

          <div className="notification-bell">
            <Bell size={20} />
            {notifications.length > 0 && (
              <span className="badge">{notifications.length}</span>
            )}
          </div>
        </div>
      </header>

      {/* KPI Cards */}
      <div className="kpi-cards">
        <div 
          className={`kpi-card critical ${riskFilter === 'critical' ? 'active-filter' : ''}`}
          onClick={() => toggleRiskFilter('critical')}
          style={{ cursor: 'pointer' }}
          title="Click to filter critical risk students"
        >
          <AlertCircle size={24} />
          <div className="kpi-content">
            <div className="kpi-value">{getRiskCount("critical")}</div>
            <div className="kpi-label">Critical</div>
          </div>
        </div>

        <div 
          className={`kpi-card high ${riskFilter === 'high' ? 'active-filter' : ''}`}
          onClick={() => toggleRiskFilter('high')}
          style={{ cursor: 'pointer' }}
          title="Click to filter high risk students"
        >
          <TrendingUp size={24} />
          <div className="kpi-content">
            <div className="kpi-value">{getRiskCount("high")}</div>
            <div className="kpi-label">High</div>
          </div>
        </div>

        <div 
          className={`kpi-card medium ${riskFilter === 'medium' ? 'active-filter' : ''}`}
          onClick={() => toggleRiskFilter('medium')}
          style={{ cursor: 'pointer' }}
          title="Click to filter medium risk students"
        >
          <Activity size={24} />
          <div className="kpi-content">
            <div className="kpi-value">{getRiskCount("medium")}</div>
            <div className="kpi-label">Medium</div>
          </div>
        </div>

        <div 
          className={`kpi-card total ${riskFilter === null ? 'active-filter' : ''}`}
          onClick={() => setRiskFilter(null)}
          style={{ cursor: 'pointer' }}
          title="Click to show all students"
        >
          <Users size={24} />
          <div className="kpi-content">
            <div className="kpi-value">{analytics?.total_students || 0}</div>
            <div className="kpi-label">Total Students</div>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="tabs">
        <button
          className={activeTab === "overview" ? "active" : ""}
          onClick={() => setActiveTab("overview")}
        >
          Overview
        </button>
        <button
          className={activeTab === "alerts" ? "active" : ""}
          onClick={() => setActiveTab("alerts")}
        >
          Alerts
        </button>
        <button
          className={activeTab === "analytics" ? "active" : ""}
          onClick={() => setActiveTab("analytics")}
        >
          Analytics
        </button>
      </div>

      {/* Tab Content */}
      <div className="tab-content">
        {/* Overview Tab */}
        {activeTab === "overview" && (
          <div className="overview-tab">
            <div className="student-table">
              <div className="table-header">
                <h2>Student Risk Overview</h2>
                {riskFilter && (
                  <div className="filter-badge">
                    Filtering: <span className="filter-value">{riskFilter.toUpperCase()}</span>
                    <span className="filter-count">({getFilteredStudents().length} students)</span>
                    <button className="clear-filter" onClick={() => setRiskFilter(null)} title="Clear filter">✕</button>
                  </div>
                )}
              </div>
              <table>
                <thead>
                  <tr>
                    <th>ID</th>
                    <th>Risk Level</th>
                    <th>Anomaly Score</th>
                    <th>Sleep</th>
                    <th>Isolation</th>
                    <th>Academic</th>
                    <th>Action</th>
                  </tr>
                </thead>
                <tbody>
                  {getFilteredStudents().slice(0, 50).map((student) => (
                    <tr key={student.student_id}>
                      <td className="mono">{student.student_id}</td>
                      <td>
                        <span
                          className="risk-badge"
                          style={{
                            backgroundColor: getRiskBadgeColor(
                              student.risk_level,
                            ),
                          }}
                        >
                          {student.risk_level}
                        </span>
                      </td>
                      <td>{(student.anomaly_score * 100).toFixed(0)}%</td>
                      <td>
                        <div className="score-bar">
                          <div
                            className="score-fill"
                            style={{
                              width: `${(student.sleep_score || 0) * 100}%`,
                              backgroundColor:
                                (student.sleep_score || 0) > 0.7
                                  ? "#dc2626"
                                  : "#16a34a",
                            }}
                          ></div>
                        </div>
                      </td>
                      <td>
                        <div className="score-bar">
                          <div
                            className="score-fill"
                            style={{
                              width: `${(student.isolation_score || 0) * 100}%`,
                              backgroundColor:
                                (student.isolation_score || 0) > 0.7
                                  ? "#dc2626"
                                  : "#16a34a",
                            }}
                          ></div>
                        </div>
                      </td>
                      <td>
                        <div className="score-bar">
                          <div
                            className="score-fill"
                            style={{
                              width: `${(student.drift_score || 0) * 100}%`,
                              backgroundColor:
                                (student.drift_score || 0) > 0.7
                                  ? "#dc2626"
                                  : "#16a34a",
                            }}
                          ></div>
                        </div>
                      </td>
                      <td>
                        <button
                          className="btn-small"
                          onClick={() => viewStudentDetail(student.student_id)}
                        >
                          View
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* Alerts Tab */}
        {activeTab === "alerts" && (
          <div className="alerts-tab">
            <h2>Critical & High Risk Alerts</h2>
            <div className="alert-cards">
              {alerts.map((alert) => (
                <div key={alert.student_id} className="alert-card">
                  <div className="alert-header">
                    <div>
                      <span className="mono">{alert.student_id}</span>
                      <span
                        className="risk-badge"
                        style={{
                          backgroundColor: getRiskBadgeColor(alert.risk_level),
                        }}
                      >
                        {alert.risk_level.toUpperCase()}
                      </span>
                    </div>
                    <div className="alert-score">
                      Score: {(alert.anomaly_score * 100).toFixed(0)}%
                    </div>
                  </div>

                  <div className="metric-tiles">
                    <div className="metric-tile">
                      <div className="metric-label">Sleep</div>
                      <div className="metric-value">
                        {((alert.sleep_score || 0) * 100).toFixed(0)}%
                      </div>
                    </div>
                    <div className="metric-tile">
                      <div className="metric-label">Isolation</div>
                      <div className="metric-value">
                        {((alert.isolation_score || 0) * 100).toFixed(0)}%
                      </div>
                    </div>
                    <div className="metric-tile">
                      <div className="metric-label">Academic</div>
                      <div className="metric-value">
                        {((alert.drift_score || 0) * 100).toFixed(0)}%
                      </div>
                    </div>
                  </div>

                  <div className="recommendation">
                    <strong>AI Recommendation:</strong>
                    <p>{alert.recommendation}</p>
                  </div>

                  <div className="alert-actions">
                    <button
                      className="btn-primary"
                      onClick={() => assignCounsellor(alert.student_id)}
                    >
                      Assign
                    </button>
                    <button
                      className="btn-secondary"
                      onClick={() => snoozeAlert(alert.student_id)}
                    >
                      Snooze
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Analytics Tab */}
        {activeTab === "analytics" && analytics && (
          <div className="analytics-tab">
            <h2>System Analytics</h2>

            <div className="analytics-grid">
              <div className="analytics-card">
                <h3>Risk Distribution</h3>
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart
                    data={Object.entries(analytics.risk_distribution || {}).map(
                      ([level, data]) => ({
                        level,
                        count: data.count,
                      }),
                    )}
                  >
                    <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                    <XAxis dataKey="level" stroke="#94a3b8" />
                    <YAxis stroke="#94a3b8" />
                    <Tooltip
                      contentStyle={{
                        backgroundColor: "#0f172a",
                        border: "1px solid #334155",
                      }}
                    />
                    <Bar dataKey="count" fill="#3b82f6" />
                  </BarChart>
                </ResponsiveContainer>
              </div>

              <div className="analytics-card">
                <h3>Model Performance</h3>
                <div className="model-info">
                  <div className="info-row">
                    <span>Model Version:</span>
                    <span className="mono">{analytics.model_version}</span>
                  </div>
                  <div className="info-row">
                    <span>Total Students:</span>
                    <span>{analytics.total_students}</span>
                  </div>
                  <div className="info-row">
                    <span>Last Updated:</span>
                    <span>
                      {new Date(analytics.last_updated).toLocaleString()}
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Student Detail Sidebar */}
      {selectedStudent && (
        <div
          className="sidebar-overlay"
          onClick={() => setSelectedStudent(null)}
        >
          <div className="sidebar" onClick={(e) => e.stopPropagation()}>
            <button
              className="close-btn"
              onClick={() => setSelectedStudent(null)}
            >
              ×
            </button>

            <h2>Student Details</h2>
            <p className="mono">{selectedStudent.student_id}</p>

            <div className="detail-section">
              <h3>Risk Assessment</h3>
              <div className="metric-tiles">
                <div className="metric-tile">
                  <div className="metric-label">Sleep</div>
                  <div className="metric-value">
                    {((selectedStudent?.latest_risk?.sleep_score || 0) * 100).toFixed(0)}
                    %
                  </div>
                  <div
                    className={`trend ${selectedStudent?.trends?.sleep_trend || 'stable'}`}
                  >
                    {selectedStudent?.trends?.sleep_trend || 'stable'}
                  </div>
                </div>
                <div className="metric-tile">
                  <div className="metric-label">Isolation</div>
                  <div className="metric-value">
                    {(
                      (selectedStudent?.latest_risk?.isolation_score || 0) * 100
                    ).toFixed(0)}
                    %
                  </div>
                  <div
                    className={`trend ${selectedStudent?.trends?.isolation_trend || 'stable'}`}
                  >
                    {selectedStudent?.trends?.isolation_trend || 'stable'}
                  </div>
                </div>
                <div className="metric-tile">
                  <div className="metric-label">Academic</div>
                  <div className="metric-value">
                    {((selectedStudent?.latest_risk?.drift_score || 0) * 100).toFixed(0)}
                    %
                  </div>
                  <div
                    className={`trend ${selectedStudent?.trends?.academic_trend || 'stable'}`}
                  >
                    {selectedStudent?.trends?.academic_trend || 'stable'}
                  </div>
                </div>
              </div>
            </div>

            <div className="detail-section">
              <h3>Behavioral Signals</h3>
              <ul className="signals-list">
                {(selectedStudent?.behavioral_signals || []).map((signal, idx) => (
                  <li key={idx} className={`signal ${signal.severity}`}>
                    <span className="signal-dot"></span>
                    {signal.message}
                  </li>
                ))}
              </ul>
            </div>

            <div className="detail-section">
              <h3>7-Day History</h3>
              {selectedStudent?.behavioral_history && selectedStudent.behavioral_history.length > 0 ? (
                <ResponsiveContainer width="100%" height={150}>
                  <LineChart data={selectedStudent.behavioral_history}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                  <XAxis dataKey="date" stroke="#94a3b8" hide />
                  <YAxis stroke="#94a3b8" />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: "#0f172a",
                      border: "1px solid #334155",
                    }}
                  />
                  <Line
                    type="monotone"
                    dataKey="dorm_ratio"
                    stroke="#3b82f6"
                    strokeWidth={2}
                  />
                </LineChart>
              </ResponsiveContainer>
              ) : (
                <p style={{ color: '#64748b', textAlign: 'center', padding: '1rem' }}>
                  No behavioral history available
                </p>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Privacy Footer */}
      <footer className="privacy-footer">
        <div className="footer-content">
          <div className="footer-left">
            <Shield size={18} />
            <span className="footer-brand">AURA v1.0</span>
            <span className="footer-divider">|</span>
            <span>Privacy-First Student Wellness Intelligence</span>
          </div>
          <div className="footer-center">
            <span className="footer-badge">🔒 FERPA Compliant</span>
            <span className="footer-badge">🔐 End-to-End Encrypted</span>
            <span className="footer-badge">🛡️ Zero PII in ML Pipeline</span>
          </div>
          <div className="footer-right">
            <span>© 2026 AURA Project</span>
            <span className="footer-divider">|</span>
            <span>All student data pseudonymized</span>
          </div>
        </div>
      </footer>

      {/* Notifications Panel */}
      {notifications.length > 0 && (
        <div className="notifications-panel">
          <h3>
            <Bell size={16} />
            Recent Updates
          </h3>
          {notifications.map((notif, idx) => (
            <div key={idx} className="notification-item">
              <span className="notification-message">{notif.message}</span>
              <span className="notification-time">
                {notif.time.toLocaleTimeString()}
              </span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default AuraDashboard;
