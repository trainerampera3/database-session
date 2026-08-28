function Header() {
    return (
        <header className="header">
            <div>
                <h1 className="header__title">
                    Weather Intelligence Dashboard
                </h1>

                <p className="header__subtitle">
                    Real-time weather monitoring and ETL pipeline insights
                </p>
            </div>

            <div className="header__status">
                <span className="status-dot"></span>

                API Connected
            </div>
        </header>
    );
}

export default Header;