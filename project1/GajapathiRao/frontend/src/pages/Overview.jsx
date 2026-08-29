import React from "react";

import { useEffect, useState } from "react";

import PacmanLoader from "react-spinners/PacmanLoader";

import {
    MdThermostat,
    MdWaterDrop,
    MdAir,
    MdLocationCity
} from "react-icons/md";

import {
    getCurrentWeather,
    getETLLogs
} from "../services/api";

import MetricCard from "../components/MetricCard";


function Overview() {

    const [weather, setWeather] = useState([]);

    const [logs, setLogs] = useState([]);

    const [loading, setLoading] = useState(true);


    useEffect(() => {

        async function loadDashboard() {

            try {

                const [
                    weatherData,
                    logsData
                ] = await Promise.all([

                    getCurrentWeather(),

                    getETLLogs()

                ]);


                setWeather(
                    Array.isArray(weatherData)
                        ? weatherData
                        : []
                );


                setLogs(
                    logsData?.data || []
                );

            } catch (error) {

                console.error(
                    "Dashboard loading failed:",
                    error
                );

            } finally {

                setLoading(false);

            }

        }

        loadDashboard();

    }, []);


    const latestWeather = weather.reduce(
        (latest, item) => {

            if (!latest[item.city]) {

                latest[item.city] = item;

            }

            else if (
                new Date(item.observed_at)
                >
                new Date(
                    latest[item.city]
                    .observed_at
                )
            ) {

                latest[item.city] = item;

            }

            return latest;

        },
        {}
    );


    const cityWeather =
        Object.values(latestWeather);


    const latestLog =
        logs.length > 0
            ? logs[0]
            : null;


    const averageTemperature =
        cityWeather.length
            ? (
                cityWeather.reduce(
                    (sum, item) =>
                        sum + item.temperature,
                    0
                ) / cityWeather.length
            ).toFixed(1)
            : "--";


    const averageHumidity =
        cityWeather.length
            ? (
                cityWeather.reduce(
                    (sum, item) =>
                        sum + item.humidity,
                    0
                ) / cityWeather.length
            ).toFixed(0)
            : "--";


    return (

        <section className="page">

            <div className="page__heading">

                <div>

                    <h2>
                        Overview
                    </h2>

                    <p>
                        Monitor your weather data
                        platform and ETL pipeline.
                    </p>

                </div>

            </div>


            {/* KPI Cards */}

            <div className="metrics-grid">

                <MetricCard
                    title="Cities Monitored"
                    value={cityWeather.length}
                    icon={<MdLocationCity />}
                    description="Active locations"
                />


                <MetricCard
                    title="Average Temperature"
                    value={averageTemperature}
                    unit="°C"
                    icon={<MdThermostat />}
                    description="Across monitored cities"
                />


                <MetricCard
                    title="Average Humidity"
                    value={averageHumidity}
                    unit="%"
                    icon={<MdWaterDrop />}
                    description="Current observations"
                />


                <MetricCard
                    title="Records Processed"
                    value={
                        latestLog
                            ?.records_processed
                            ?.toLocaleString() || "0"
                    }
                    icon={<MdAir />}
                    description="Latest ETL batch"
                />

            </div>


            {/* Current Weather */}

            <div className="section-heading">

                <h3>
                    Current Weather
                </h3>

                <span>
                    Latest observations
                </span>

            </div>


            {loading ? (

                <div className="empty-state">
                    <PacmanLoader color="#71d7f3" />
                </div>

            ) : (

                <div className="weather-grid">

                    {cityWeather.map((item) => (

                        <div
                            className="weather-card"
                            key={item.city}
                        >

                            <div className="weather-card__header">

                                <div>

                                    <h3>
                                        {item.city}
                                    </h3>

                                    <span>
                                        {item.state}
                                    </span>

                                </div>

                            </div>


                            <div className="weather-card__temperature">

                                <MdThermostat />

                                <strong>
                                    {item.temperature}
                                </strong>

                                <span>
                                    °C
                                </span>

                            </div>


                            <div className="weather-card__metrics">

                                <div>

                                    <MdWaterDrop />

                                    <span>
                                        Humidity
                                    </span>

                                    <strong>
                                        {item.humidity}%
                                    </strong>

                                </div>


                                <div>

                                    <MdAir />

                                    <span>
                                        Wind
                                    </span>

                                    <strong>
                                        {item.wind_speed}
                                        {" "}
                                        km/h
                                    </strong>

                                </div>

                            </div>

                        </div>

                    ))}

                </div>

            )}

        </section>

    );
}

export default Overview;