import { Stats } from '../types'

interface SidebarProps {
  stats: Stats
}

export default function Sidebar({ stats }: SidebarProps) {
  return (
    <aside className="sidebar">
      <div className="sidebar-card">
        <h3>Session Statistics</h3>
        <div className="stats-grid">
          <div className="stat-item">
            <div className="stat-value">{stats.totalQueries}</div>
            <div className="stat-label">Total Queries</div>
          </div>
          <div className="stat-item">
            <div className="stat-value">{stats.webSearchUsed}</div>
            <div className="stat-label">Web Searches</div>
          </div>
          <div className="stat-item">
            <div className="stat-value">{(stats.avgConfidence * 100).toFixed(0)}%</div>
            <div className="stat-label">Avg Confidence</div>
          </div>
          <div className="stat-item">
            <div className="stat-value">{stats.avgProcessingTime.toFixed(0)}ms</div>
            <div className="stat-label">Avg Response</div>
          </div>
        </div>
      </div>
      
      <div className="sidebar-card">
        <h3>How It Works</h3>
        <div style={{ fontSize: '0.875rem', color: 'var(--text-secondary)', lineHeight: 1.6 }}>
          <p style={{ marginBottom: '0.75rem' }}>
            <strong style={{ color: 'var(--text-primary)' }}>1. Retrieve:</strong> Finds relevant documents from your knowledge base.
          </p>
          <p style={{ marginBottom: '0.75rem' }}>
            <strong style={{ color: 'var(--text-primary)' }}>2. Grade:</strong> Assesses document quality using AI.
          </p>
          <p style={{ marginBottom: '0.75rem' }}>
            <strong style={{ color: 'var(--text-primary)' }}>3. Correct:</strong> Falls back to web search if needed.
          </p>
          <p>
            <strong style={{ color: 'var(--text-primary)' }}>4. Generate:</strong> Produces sourced answers.
          </p>
        </div>
      </div>
      
      <div className="sidebar-card">
        <h3>Quick Tips</h3>
        <ul style={{ 
          fontSize: '0.875rem', 
          color: 'var(--text-secondary)', 
          lineHeight: 1.8,
          paddingLeft: '1rem'
        }}>
          <li>Be specific in your questions</li>
          <li>Ask about specific documents</li>
          <li>Request comparisons or summaries</li>
          <li>Press Enter to send quickly</li>
        </ul>
      </div>
    </aside>
  )
}
