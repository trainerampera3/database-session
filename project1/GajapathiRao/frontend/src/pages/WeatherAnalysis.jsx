import React from "react";

import { useEffect, useState } from "react";

import {
    LineChart,
    Line,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    ResponsiveContainer
} from "recharts";

import {
    getWeatherHistory
} from "../services/api";

import LocationSelector from "../components/LocationSelector";


function WeatherAnalysis() {

    const [locationId, setLocationId] =
        useState("");

    const [history, setHistory] =
        useState([]);

    const [loading, setLoading] =
        useState(false);


    async function loadHistory() {

        try {

            setLoading(true);

            const data =
                await getWeatherHistory(
                    "2025-01-01",
                    "2025-12-31",
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

        } finally {

            setLoading(false);

        }

    }


    useEffect(() => {

        loadHistory();

    }, [locationId]);


    const chartData = history.map(
        (item) => ({

            date: item.observed_at
                || item.date,

            temperature:
                item.temperature,

            humidity:
                item.humidity

        })
    );


    return (

        <section className="page">

            <div className="page__heading">

                <div>

                    <h2>
                        Weather Analysis
                    </h2>

                    <p>
                        Analyze historical weather
                        observations.
                    </p>

                </div>


                <LocationSelector
                    value={locationId}
                    onChange={setLocationId}
                />

            </div>


            <div className="analysis-card">

                <div className="analysis-card__header">

                    <div>

                        <h3>
                            2025 Temperature Trend
                        </h3>

                        <span>
                            Historical weather data
                        </span>

                    </div>

                </div>


                {loading ? (

                    <div className="empty-state">
                        Loading history...
                    </div>

                ) : chartData.length === 0 ? (

                    <div className="empty-state">
                        No historical data available.
                    </div>

                ) : (

                    <div className="chart-container">

                        <ResponsiveContainer
                            width="100%"
                            height={420}
                        >

                            <LineChart
                                data={chartData}
                            >

                                <CartesianGrid
                                    strokeDasharray="3 3"
                                />

                                <XAxis
                                    dataKey="date"
                                />

                                <YAxis />

                                <Tooltip />

                                <Line
                                    type="monotone"
                                    dataKey="temperature"
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