function Header() {
    return (
        <header className="header">
            <div>
                <h1>Dashboard</h1>
                <p>Weather ETL monitoring and analytics</p>
            </div>

            <div className="header__status">
                <span className="header__status-dot"></span>
                System Operational
            </div>
        </header>
    );
}

export default Header;