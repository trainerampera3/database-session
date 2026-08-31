import React, { useState } from "react";
import { executeQuery } from "../services/api";

function QueryTool() {
    const [query, setQuery] = useState(
        `SELECT
    l.city,
    l.state,
    wh.observed_at,
    wh.temperature,
    wh.humidity,
    wh.wind_speed
FROM weather_historical wh
JOIN location l
    ON wh.location_id = l.location_id
LIMIT 20;`
    );

    const [results, setResults] = useState([]);
    const [columns, setColumns] = useState([]);

    const [loading, setLoading] = useState(false);
    const [error, setError] = useState("");
    const [executionTime, setExecutionTime] = useState(null);

    async function handleExecute() {
        if (!query.trim()) {
            setError("Please enter a SQL query.");
            return;
        }

        setLoading(true);
        setError("");
        setResults([]);
        setColumns([]);
        setExecutionTime(null);

        const start = performance.now();

        try {
            const response = await executeQuery(query);

            const data = response?.data || [];

            setResults(data);

            if (data.length > 0) {
                setColumns(Object.keys(data[0]));
            }

            const end = performance.now();

            setExecutionTime(
                ((end - start) / 1000).toFixed(2)
            );

        } catch (err) {
            console.error("Query failed:", err);

            setError(
                err?.message ||
                "Failed to execute query."
            );
        } finally {
            setLoading(false);
        }
    }

    function clearQuery() {
        setQuery("");
        setResults([]);
        setColumns([]);
        setError("");
        setExecutionTime(null);
    }

    function loadExample() {
        setQuery(
            `SELECT
    l.city,
    l.state,
    COUNT(*) AS records
FROM weather_historical wh
JOIN location l
    ON wh.location_id = l.location_id
GROUP BY l.city, l.state
ORDER BY records DESC;`
        );
    }

    return (
        <section className="page query-tool-page">

            {/* Page Header */}
            <div className="page__heading">

                <div>
                    <h2>Query Tool</h2>

                    <p>
                        Execute SQL queries against the Weather ETL database.
                    </p>
                </div>

            </div>


            {/* Query Editor */}
            <div className="query-editor-card">

                <div className="query-editor-card__header">

                    <div>
                        <h3>SQL Query</h3>

                        <span>
                            PostgreSQL
                        </span>
                    </div>

                    <button
                        className="example-button"
                        onClick={loadExample}
                    >
                        Load Example
                    </button>

                </div>


                <div className="query-editor">

                    <textarea
                        value={query}
                        onChange={(event) =>
                            setQuery(event.target.value)
                        }
                        placeholder="Enter your SQL query..."
                        spellCheck="false"
                    />

                </div>


                {/* Actions */}
                <div className="query-editor-card__footer">

                    <div className="query-hint">
                        <span>⌘</span>
                        Write a SQL SELECT query
                    </div>


                    <div className="query-actions">

                        <button
                            className="secondary-button"
                            onClick={clearQuery}
                        >
                            Clear
                        </button>


                        <button
                            className="primary-button"
                            onClick={handleExecute}
                            disabled={loading}
                        >
                            {loading
                                ? "Executing..."
                                : "▶ Execute Query"}
                        </button>

                    </div>

                </div>

            </div>


            {/* Error */}
            {error && (

                <div className="query-error">

                    <strong>Query Error</strong>

                    <p>{error}</p>

                </div>

            )}


            {/* Results */}
            <div className="table-card query-results-card">

                <div className="table-card__header">

                    <div>
                        <h3>Query Results</h3>

                        {executionTime && (
                            <small>
                                Executed in {executionTime}s
                            </small>
                        )}
                    </div>


                    <span>
                        {results.length} records
                    </span>

                </div>


                <div className="table-wrapper">

                    {results.length === 0 ? (

                        <div className="empty-query">

                            <div className="empty-query__icon">
                                ⌕
                            </div>

                            <h4>
                                No results yet
                            </h4>

                            <p>
                                Write a SQL query above and click
                                <strong> Execute Query </strong>
                                to see the results.
                            </p>

                        </div>

                    ) : (

                        <table>

                            <thead>

                                <tr>

                                    {columns.map((column) => (

                                        <th key={column}>
                                            {column}
                                        </th>

                                    ))}

                                </tr>

                            </thead>


                            <tbody>

                                {results.map((row, rowIndex) => (

                                    <tr key={rowIndex}>

                                        {columns.map((column) => (

                                            <td key={column}>

                                                {row[column] === null
                                                    ? "NULL"
                                                    : String(row[column])}

                                            </td>

                                        ))}

                                    </tr>

                                ))}

                            </tbody>

                        </table>

                    )}

                </div>

            </div>

        </section>
    );
}

export default QueryTool;