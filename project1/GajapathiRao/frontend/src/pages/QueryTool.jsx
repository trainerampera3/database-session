import React from "react";

import { useState } from "react";

import {
    getWeatherHistory
} from "../services/api";


function QueryTool() {

    const [startDate, setStartDate] =
        useState("2025-01-01");

    const [endDate, setEndDate] =
        useState("2025-12-31");

    const [locationId, setLocationId] =
        useState("");

    const [results, setResults] =
        useState([]);

    const [loading, setLoading] =
        useState(false);


    async function executeQuery() {

        try {

            setLoading(true);

            const data =
                await getWeatherHistory(
                    startDate,
                    endDate,
                    locationId || null,
                    100
                );


            setResults(
                Array.isArray(data)
                    ? data
                    : data?.data || []
            );

        } catch (error) {

            console.error(
                "Query failed:",
                error
            );

            setResults([]);

        } finally {

            setLoading(false);

        }

    }


    return (

        <section className="page">

            <div className="page__heading">

                <div>

                    <h2>
                        Query Tool
                    </h2>

                    <p>
                        Query historical weather data.
                    </p>

                </div>

            </div>


            <div className="query-card">

                <div className="query-card__grid">

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


                    <div className="form-group">

                        <label>
                            Location ID
                        </label>

                        <input
                            type="number"
                            placeholder="All locations"
                            value={locationId}
                            onChange={(event) =>
                                setLocationId(
                                    event.target.value
                                )
                            }
                        />

                    </div>


                    <div className="form-group">

                        <label>
                            &nbsp;
                        </label>

                        <button
                            onClick={executeQuery}
                            disabled={loading}
                            className="primary-button"
                        >

                            {loading
                                ? "Running..."
                                : "Run Query"}

                        </button>

                    </div>

                </div>

            </div>


            <div className="table-card">

                <div className="table-card__header">

                    <h3>
                        Query Results
                    </h3>

                    <span>
                        {results.length} records
                    </span>

                </div>


                <div className="table-wrapper">

                    <table>

                        <thead>

                            <tr>

                                <th>City</th>
                                <th>State</th>
                                <th>Date</th>
                                <th>Temperature</th>
                                <th>Humidity</th>
                                <th>Wind</th>

                            </tr>

                        </thead>


                        <tbody>

                            {results.map(
                                (item, index) => (

                                    <tr key={index}>

                                        <td>
                                            {item.city}
                                        </td>

                                        <td>
                                            {item.state}
                                        </td>

                                        <td>
                                            {item.observed_at
                                                || item.date}
                                        </td>

                                        <td>
                                            {item.temperature}
                                            °C
                                        </td>

                                        <td>
                                            {item.humidity}%
                                        </td>

                                        <td>
                                            {item.wind_speed}
                                        </td>

                                    </tr>

                                )
                            )}

                        </tbody>

                    </table>

                </div>

            </div>

        </section>

    );
}

export default QueryTool;