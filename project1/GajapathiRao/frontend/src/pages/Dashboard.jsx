import LocationSelector from "../components/LocationSelector";

function Dashboard() {

    function handleLocationChange(location) {
        console.log("Selected location:", location);
    }

    return (
        <main className="dashboard">

            <div className="dashboard__welcome">
                <div>
                    <h2>Weather Overview</h2>
                    <p>
                        Monitor weather data across all configured locations.
                    </p>
                </div>

                <LocationSelector
                    onLocationChange={handleLocationChange}
                />
            </div>

            <div className="dashboard__cards">
                <div className="weather-card">
                    <span>Locations</span>
                    <strong>8</strong>
                </div>

                <div className="weather-card">
                    <span>Hourly Records</span>
                    <strong>3,264</strong>
                </div>

                <div className="weather-card">
                    <span>Historical Records</span>
                    <strong>70,080</strong>
                </div>

                <div className="weather-card">
                    <span>ETL Status</span>
                    <strong>SUCCESS</strong>
                </div>
            </div>

        </main>
    );
}

export default Dashboard;