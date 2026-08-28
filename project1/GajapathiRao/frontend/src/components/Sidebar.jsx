function Sidebar() {
    return (
        <aside className="sidebar">
            <div className="sidebar__logo">
                <h2>Weather ETL</h2>
                <span>Data Platform</span>
            </div>

            <nav className="sidebar__nav">
                <button className="sidebar__item sidebar__item--active">
                    Dashboard
                </button>

                <button className="sidebar__item">
                    Live Weather
                </button>

                <button className="sidebar__item">
                    History
                </button>

                <button className="sidebar__item">
                    Query Tool
                </button>

                <button className="sidebar__item">
                    Batch Logs
                </button>

                <button className="sidebar__item">
                    Data Quality
                </button>
            </nav>
        </aside>
    );
}

export default Sidebar;