import React from "react";

import { useEffect, useState } from "react";

import {
    MdCheckCircle,
    MdError,
    MdRefresh
} from "react-icons/md";

import { getETLLogs } from "../services/api";


function BatchLogs() {

    const [logs, setLogs] =
        useState([]);

    const [loading, setLoading] =
        useState(true);


    async function loadLogs() {

        try {

            setLoading(true);

            const response =
                await getETLLogs();

            setLogs(
                response?.data || []
            );

        } catch (error) {

            console.error(
                "ETL logs loading failed:",
                error
            );

            setLogs([]);

        } finally {

            setLoading(false);

        }

    }


    useEffect(() => {

        loadLogs();

    }, []);


    return (

        <section className="page">

            <div className="page__heading">

                <div>

                    <h2>
                        Batch Logs
                    </h2>

                    <p>
                        Monitor ETL pipeline executions,
                        failures and processed records.
                    </p>

                </div>


                <button
                    className="secondary-button"
                    onClick={loadLogs}
                >

                    <MdRefresh />

                    Refresh

                </button>

            </div>


            <div className="table-card">

                <div className="table-card__header">

                    <h3>
                        ETL Pipeline Runs
                    </h3>

                    <span>
                        {logs.length} runs
                    </span>

                </div>


                {loading ? (

                    <div className="empty-state">
                        Loading ETL logs...
                    </div>

                ) : (

                    <div className="table-wrapper">

                        <table>

                            <thead>

                                <tr>

                                    <th>
                                        Run ID
                                    </th>

                                    <th>
                                        Pipeline
                                    </th>

                                    <th>
                                        Started
                                    </th>

                                    <th>
                                        Completed
                                    </th>

                                    <th>
                                        Status
                                    </th>

                                    <th>
                                        Records
                                    </th>

                                    <th>
                                        Error
                                    </th>

                                </tr>

                            </thead>


                            <tbody>

                                {logs.map(
                                    (log) => (

                                        <tr
                                            key={log.run_id}
                                        >

                                            <td>
                                                #{log.run_id}
                                            </td>

                                            <td>
                                                {log.pipeline_name}
                                            </td>

                                            <td>
                                                {log.started_at
                                                    ?.replace(
                                                        "T",
                                                        " "
                                                    )}
                                            </td>

                                            <td>
                                                {log.completed_at
                                                    ?.replace(
                                                        "T",
                                                        " "
                                                    )}
                                            </td>

                                            <td>

                                                <span
                                                    className={`status-badge ${
                                                        log.status ===
                                                        "SUCCESS"
                                                            ? "status-badge--success"
                                                            : "status-badge--failed"
                                                    }`}
                                                >

                                                    {log.status ===
                                                    "SUCCESS"
                                                        ? (
                                                            <MdCheckCircle />
                                                        )
                                                        : (
                                                            <MdError />
                                                        )}

                                                    {log.status}

                                                </span>

                                            </td>

                                            <td>
                                                {log.records_processed
                                                    ?.toLocaleString()}
                                            </td>

                                            <td className="error-cell">

                                                {log.error_message
                                                    || "—"}

                                            </td>

                                        </tr>

                                    )
                                )}

                            </tbody>

                        </table>

                    </div>

                )}

            </div>

        </section>

    );
}

export default BatchLogs;