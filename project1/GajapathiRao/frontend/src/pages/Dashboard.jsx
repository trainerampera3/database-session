import { useEffect, useMemo, useState } from "react";

import PacmanLoader from "react-spinners/PacmanLoader";

import LocationSelector from "../components/LocationSelector";
import DateRangeSelector from "../components/DateRangeSelector";
import KPICards from "../components/KPICards";
import WeatherChart from "../components/WeatherChart";

import {
    getCurrentWeather,
    getLocations,
    getWeatherHistory,
    getETLLogs,
} from "../services/api";


function Dashboard() {
    const [locations, setLocations] = useState([]);
    const [weatherData, setWeatherData] = useState([]);
    const [etlLogs, setETLLogs] = useState([]);

    const [locationId, setLocationId] = useState("");

    const [startDate, setStartDate] = useState(
        "2026-08-01"
    );

    const [endDate, setEndDate] = useState(
        "2026-08-28"
    );

    const [loading, setLoading] = useState(true);
    const [historyLoading, setHistoryLoading] = useState(false);

    const [error, setError] = useState("");



    useEffect(() => {
        async function loadDashboard() {
            try {
                setLoading(true);
                setError("");

                const [
                    locationsResponse,
                    currentWeatherResponse,
                    logsResponse,
                ] = await Promise.all([
                    getLocations(),
                    getCurrentWeather(),
                    getETLLogs(),
                ]);

                setLocations(
                    Array.isArray(locationsResponse)
                        ? locationsResponse
                        : []
                );

                setWeatherData(
                    Array.isArray(currentWeatherResponse)
                        ? currentWeatherResponse
                        : []
                );

                setETLLogs(
                    logsResponse?.data || []
                );

            } catch (err) {
                console.error(
                    "Dashboard loading failed:",
                    err
                );

                setError(
                    "Unable to load dashboard data."
                );
            } finally {
                setLoading(false);
            }
        }

        loadDashboard();
    }, []);


    // --------------------------------
    // History data
    // --------------------------------

    async function loadHistory() {
        if (!startDate || !endDate) {
            return;
        }

        try {
            setHistoryLoading(true);
            setError("");

            const result = await getWeatherHistory(
                startDate,
                endDate,
                locationId || null,
                100
            );

            /*
             Expected API could return:

             [
                 {...},
                 {...}
             ]

             OR

             {
                 count: ...,
                 data: [...]
             }
            */

            const historyData = Array.isArray(result)
                ? result
                : result?.data || [];

            setWeatherData(historyData);

        } catch (err) {
            console.error(
                "History loading failed:",
                err
            );

            setError(
                "Unable to load weather history."
            );

            setWeatherData([]);
        } finally {
            setHistoryLoading(false);
        }
    }


    // --------------------------------
    // Filter current data by location
    // --------------------------------

    const filteredWeather = useMemo(() => {
        if (!locationId) {
            return weatherData;
        }

        const selectedLocation = locations.find(
            (location) =>
                String(location.location_id) ===
                String(locationId)
        );

        if (!selectedLocation) {
            return weatherData;
        }

        return weatherData.filter(
            (item) =>
                item.city === selectedLocation.city
        );
    }, [
        weatherData,
        locationId,
        locations,
    ]);


    // --------------------------------
    // Latest ETL log
    // --------------------------------

    const latestLog = etlLogs.length
        ? etlLogs[0]
        : null;


    if (loading) {
        return (
            <main className="dashboard">
                <div className="empty-state">
                    <PacmanLoader color="#71d7f3" />
                </div>
            </main>
        );
    }


    return (
        <main className="dashboard" id="overview">

            {/* Error */}
            {error && (
                <div className="alert alert--error">
                    {error}
                </div>
            )}


            {/* Filters */}
            <section className="dashboard__filters">

                <LocationSelector
                    value={locationId}
                    onChange={setLocationId}
                />

                <DateRangeSelector
                    startDate={startDate}
                    endDate={endDate}
                    onStartDateChange={setStartDate}
                    onEndDateChange={setEndDate}
                />

                <button
                    className="btn btn--primary"
                    onClick={loadHistory}
                    disabled={historyLoading}
                >
                    {historyLoading
                        ? "Loading..."
                        : "Apply Filters"}
                </button>

            </section>


            {/* KPI Cards */}
            <section>
                <KPICards
                    weatherData={filteredWeather}
                    locationsCount={locations.length}
                />
            </section>


            {/* Weather Chart */}
            <section id="weather">
                <WeatherChart
                    data={filteredWeather}
                />
            </section>


            {/* Bottom grid */}
            <section className="dashboard-grid">

                {/* ETL Status */}
                <div
                    className="panel"
                    id="etl-logs"
                >
                    <div className="panel__header">
                        <div>
                            <h2>ETL Pipeline</h2>

                            <p>
                                Latest batch execution
                            </p>
                        </div>
                    </div>

                    {latestLog ? (
                        <div className="etl-summary">

                            <div className="etl-row">
                                <span>Pipeline</span>

                                <strong>
                                    {latestLog.pipeline_name}
                                </strong>
                            </div>

                            <div className="etl-row">
                                <span>Status</span>

                                <strong
                                    className={
                                        latestLog.status ===
                                        "SUCCESS"
                                            ? "success"
                                            : "failed"
                                    }
                                >
                                    {latestLog.status}
                                </strong>
                            </div>

                            <div className="etl-row">
                                <span>Records Processed</span>

                                <strong>
                                    {latestLog.records_processed}
                                </strong>
                            </div>

                            <div className="etl-row">
                                <span>Started</span>

                                <strong>
                                    {new Date(
                                        latestLog.started_at
                                    ).toLocaleString()}
                                </strong>
                            </div>

                        </div>
                    ) : (
                        <p>No ETL logs available.</p>
                    )}
                </div>


                {/* Query Tool */}
                <div
                    className="panel"
                    id="query"
                >
                    <div className="panel__header">
                        <div>
                            <h2>Query Tool</h2>

                            <p>
                                Explore weather data
                            </p>
                        </div>
                    </div>

                    <div className="query-box">

                        <textarea
                            placeholder="Enter your SQL query..."
                        />

                        <button className="btn btn--primary">
                            Run Query
                        </button>

                    </div>
                </div>

            </section>


            {/* Batch logs table */}
            <section className="panel">

                <div className="panel__header">
                    <div>
                        <h2>Batch Logs</h2>

                        <p>
                            Recent ETL executions
                        </p>
                    </div>
                </div>

                <div className="table-wrapper">

                    <table className="logs-table">

                        <thead>
                            <tr>
                                <th>Run ID</th>
                                <th>Pipeline</th>
                                <th>Started</th>
                                <th>Completed</th>
                                <th>Status</th>
                                <th>Records</th>
                            </tr>
                        </thead>

                        <tbody>

                            {etlLogs.map((log) => (
                                <tr key={log.run_id}>

                                    <td>
                                        #{log.run_id}
                                    </td>

                                    <td>
                                        {log.pipeline_name}
                                    </td>

                                    <td>
                                        {new Date(
                                            log.started_at
                                        ).toLocaleString()}
                                    </td>

                                    <td>
                                        {new Date(
                                            log.completed_at
                                        ).toLocaleString()}
                                    </td>

                                    <td>
                                        <span
                                            className={
                                                log.status ===
                                                "SUCCESS"
                                                    ? "badge badge--success"
                                                    : "badge badge--failed"
                                            }
                                        >
                                            {log.status}
                                        </span>
                                    </td>

                                    <td>
                                        {log.records_processed}
                                    </td>

                                </tr>
                            ))}

                        </tbody>

                    </table>

                </div>

            </section>

        </main>
    );
}

export default Dashboard;