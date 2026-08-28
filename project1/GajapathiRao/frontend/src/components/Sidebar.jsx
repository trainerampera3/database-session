function Sidebar() {
    return (
        <aside className="sidebar">
            <div className="sidebar__brand">
                <div className="sidebar__logo">
                    W
                </div>

                <div>
                    <h2>Weather ETL</h2>
                    <span>Analytics Platform</span>
                </div>
            </div>

            <nav className="sidebar__nav">
                <a
                    href="#overview"
                    className="sidebar__link sidebar__link--active"
                >
                    <span>▦</span>
                    Overview
                </a>

                <a
                    href="#weather"
                    className="sidebar__link"
                >
                    <span>☁</span>
                    Weather Analysis
                </a>

                <a
                    href="#query"
                    className="sidebar__link"
                >
                    <span>⌕</span>
                    Query Tool
                </a>

                <a
                    href="#etl-logs"
                    className="sidebar__link"
                >
                    <span>▤</span>
                    Batch Logs
                </a>
            </nav>

            <div className="sidebar__footer">
                <div className="pipeline-status">
                    <span className="status-dot"></span>

                    <div>
                        <strong>ETL Pipeline</strong>
                        <small>Operational</small>
                    </div>
                </div>
            </div>
        </aside>
    );
}

export default Sidebar;