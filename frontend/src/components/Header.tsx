export default function Header() {
  return (
    <header className="header">
      <div className="logo">
        <img src="/logo.svg" alt="CRAG Logo" />
        <h1>CRAG</h1>
      </div>
      <div className="header-actions">
        <div className="status-badge">
          <span className="status-dot"></span>
          <span>System Active</span>
        </div>
      </div>
    </header>
  )
}
