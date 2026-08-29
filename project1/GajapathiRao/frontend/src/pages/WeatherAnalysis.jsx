import React, { useEffect, useState } from "react";

import {
    LineChart,
    Line,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    ResponsiveContainer,
} from "recharts";

import {
    getWeatherHistory,
} from "../services/api";

import LocationSelector from "../components/LocationSelector";

function WeatherAnalysis() {

    const [locationId, setLocationId] =
        useState("");

    const [startDate, setStartDate] =
        useState("2025-01-01");

    const [endDate, setEndDate] =
        useState("2025-12-31");

    const [history, setHistory] =
        useState([]);

    const [loading, setLoading] =
        useState(false);

    const [error, setError] =
        useState("");

    async function loadHistory() {

        // Validate dates
        if (!startDate || !endDate) {

            setError(
                "Please select both start date and end date."
            );

            return;
        }

        if (startDate > endDate) {

            setError(
                "Start date cannot be later than end date."
            );

            return;
        }

        try {

            setLoading(true);

            setError("");

            const data =
                await getWeatherHistory(
                    startDate,
                    endDate,
                    locationId || null,
                    1000
                );

            setHistory(
                Array.isArray(data)
                    ? data
                    : data?.data || []
            );

        } catch (error) {

            console.error(
                "History loading failed:",
                error
            );

            setHistory([]);

            setError(
                error.message ||
                "Failed to load historical weather data."
            );

        } finally {

            setLoading(false);

        }

    }

  
    useEffect(() => {

        loadHistory();

    }, [
        locationId,
        startDate,
        endDate
    ]);

    const chartData = history.map(
        (item) => ({

            date:
                item.observed_at ||
                item.date,

            temperature:
                item.temperature,

            humidity:
                item.humidity,

        })
    );

    return (

        <section className="page weather-analysis-page">

            

            <div className="page__heading">

                <div>

                    <h2>
                        Weather Analysis
                    </h2>

                    <p>
                        Analyze historical weather observations.
                    </p>

                </div>

            </div>

            
            <div className="analysis-filters">

               

                <div className="form-group">

                    <label>
                        Start Date
                    </label>

                    <input
                        type="date"
                        value={startDate}
                        onChange={(event) =>
                            setStartDate(
                                event.target.value
                            )
                        }
                    />

                </div>


                <div className="form-group">

                    <label>
                        End Date
                    </label>

                    <input
                        type="date"
                        value={endDate}
                        onChange={(event) =>
                            setEndDate(
                                event.target.value
                            )
                        }
                    />

                </div>

                {/* Location */}

                <div className="form-group">

                    {/* <label>
                        Location
                    </label> */}

                    <LocationSelector
                        value={locationId}
                        onChange={setLocationId}
                    />

                </div>

                {/* Search Button */}

                <div className="form-group">

                    <label>
                        &nbsp;
                    </label>

                    <button
                        className="primary-button"
                        onClick={loadHistory}
                        disabled={loading}
                    >

                        {loading
                            ? "Loading..."
                            : "Apply Filters"}

                    </button>

                </div>

            </div>

            {/* ========================= */}
            {/* ERROR */}
            {/* ========================= */}

            {error && (

                <div className="query-error">

                    <strong>
                        Error
                    </strong>

                    <p>
                        {error}
                    </p>

                </div>

            )}


            <div className="analysis-card">

                <div className="analysis-card__header">

                    <div>

                        <h3>
                            Temperature Trend
                        </h3>

                        <span>
                            {startDate}
                            {" "}
                            →{" "}
                            {endDate}
                        </span>

                    </div>

                    <div className="analysis-card__records">

                        {history.length} records

                    </div>

                </div>

                {/* ========================= */}
                {/* CHART */}
                {/* ========================= */}

                {loading ? (

                    <div className="empty-state">

                        Loading historical weather...

                    </div>

                ) : chartData.length === 0 ? (

                    <div className="empty-state">

                        No historical data available
                        for the selected filters.

                    </div>

                ) : (

                    <div className="chart-container">

                        <ResponsiveContainer
                            width="100%"
                            height={420}
                        >

                            <LineChart
                                data={chartData}
                                margin={{
                                    top: 20,
                                    right: 30,
                                    left: 10,
                                    bottom: 20,
                                }}
                            >

                                <CartesianGrid
                                    strokeDasharray="3 3"
                                />

                                <XAxis
                                    dataKey="date"
                                    tick={{ fontSize: 11 }}
                                />

                                <YAxis
                                    tick={{ fontSize: 11 }}
                                    label={{
                                        value: "Temperature °C",
                                        angle: -90,
                                        position: "insideLeft",
                                    }}
                                />

                                <Tooltip />

                                <Line
                                    type="monotone"
                                    dataKey="temperature"
                                    name="Temperature"
                                    strokeWidth={2}
                                    dot={false}
                                />

                            </LineChart>

                        </ResponsiveContainer>

                    </div>

                )}

            </div>

        </section>

    );
}

export default WeatherAnalysis;