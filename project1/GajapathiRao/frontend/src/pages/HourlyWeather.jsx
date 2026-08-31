import React, { useEffect, useMemo, useState } from "react";

import {
    LineChart,
    Line,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    ResponsiveContainer,
} from "recharts";

import PacmanLoader from "react-spinners/PacmanLoader";

import { getHourlyWeather } from "../services/api";

import {
    MdThermostat,
    MdWaterDrop,
    MdAir,
    MdAccessTime,
} from "react-icons/md";


function HourlyWeather() {

    const [weather, setWeather] = useState([]);
    const [selectedCity, setSelectedCity] = useState("All");
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");


    useEffect(() => {

        async function loadHourlyWeather() {

            try {

                setLoading(true);
                setError("");

                const response =
                    await getHourlyWeather();

                console.log(
                    "API Response:",
                    response
                );

                const data =
                    Array.isArray(response)
                        ? response
                        : response?.data || [];

                console.log(
                    "Processed data:",
                    data
                );

                if (!Array.isArray(data)) {
                    throw new Error(
                        "Data is not an array"
                    );
                }

                setWeather(data);

            } catch (err) {

                console.error(
                    "Hourly weather loading failed:",
                    err
                );

                setError(
                    err.message ||
                    "Unable to load hourly weather data."
                );

                setWeather([]);

            } finally {

                setLoading(false);

            }

        }

        loadHourlyWeather();

    }, []);


    const cities = useMemo(() => {

        const uniqueCities =
            [...new Set(
                weather.map(
                    item => item.city
                )
            )];

        return uniqueCities;

    }, [weather]);


    const filteredWeather = useMemo(() => {

        if (selectedCity === "All") {
            return weather;
        }

        return weather.filter(
            item => item.city === selectedCity
        );

    }, [weather, selectedCity]);


    const chartData = useMemo(() => {

        return filteredWeather
            .map(item => ({
                time: item.observed_at,
                temperature: Number(item.temperature),
                humidity: Number(item.humidity),
                wind_speed: Number(item.wind_speed),
            }))
            .sort(
                (a, b) =>
                    new Date(a.time) -
                    new Date(b.time)
            );

    }, [filteredWeather]);


    const latestWeather =
        chartData.length > 0
            ? chartData[chartData.length - 1]
            : null;


    return (

        <section className="page">


            <div className="page__heading">

                <div>

                    <h2>
                        Hourly Weather
                    </h2>

                    <p>
                        Monitor hourly weather observations
                        across locations.
                    </p>

                </div>


                <div className="hourly-filter">

                    <label>
                        City
                    </label>

                    <select
                        value={selectedCity}
                        onChange={(event) =>
                            setSelectedCity(
                                event.target.value
                            )
                        }
                    >

                        <option value="All">
                            All Cities
                        </option>

                        {cities.map(city => (

                            <option
                                key={city}
                                value={city}
                            >
                                {city}
                            </option>

                        ))}

                    </select>

                </div>

            </div>


    

            {loading && (

                <div className="empty-state">
                    <PacmanLoader color="#71d7f3" />
                </div>

            )}


        

            {!loading && error && (

                <div className="error-state">
                    {error}
                </div>

            )}


           

            {!loading &&
                !error &&
                chartData.length > 0 && (

                <>

                   

                    <div className="metric-grid">

                        <div className="metric-card">

                            <div className="metric-card__icon">
                                <MdThermostat />
                            </div>

                            <div>

                                <span>
                                    Latest Temperature
                                </span>

                                <strong>
                                    {latestWeather.temperature}
                                    °C
                                </strong>

                            </div>

                        </div>


                        <div className="metric-card">

                            <div className="metric-card__icon">
                                <MdWaterDrop />
                            </div>

                            <div>

                                <span>
                                    Humidity
                                </span>

                                <strong>
                                    {latestWeather.humidity}
                                    %
                                </strong>

                            </div>

                        </div>


                        <div className="metric-card">

                            <div className="metric-card__icon">
                                <MdAir />
                            </div>

                            <div>

                                <span>
                                    Wind Speed
                                </span>

                                <strong>
                                    {latestWeather.wind_speed}
                                </strong>

                            </div>

                        </div>


                        <div className="metric-card">

                            <div className="metric-card__icon">
                                <MdAccessTime />
                            </div>

                            <div>

                                <span>
                                    Observations
                                </span>

                                <strong>
                                    {chartData.length}
                                </strong>

                            </div>

                        </div>

                    </div>



                    <div className="analysis-card">

                        <div className="analysis-card__header">

                            <div>

                                <h3>
                                    Temperature Trend
                                </h3>

                                <span>
                                    Hourly temperature observations
                                </span>

                            </div>

                        </div>


                        <div className="chart-container">

                            <ResponsiveContainer
                                width="100%"
                                height={380}
                            >

                                <LineChart
                                    data={chartData}
                                >

                                    <CartesianGrid
                                        strokeDasharray="3 3"
                                    />

                                    <XAxis
                                        dataKey="time"
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

                    </div>


                    {/* HUMIDITY */}

                    <div className="analysis-card">

                        <div className="analysis-card__header">

                            <div>

                                <h3>
                                    Humidity Trend
                                </h3>

                                <span>
                                    Hourly humidity observations
                                </span>

                            </div>

                        </div>


                        <div className="chart-container">

                            <ResponsiveContainer
                                width="100%"
                                height={350}
                            >

                                <LineChart
                                    data={chartData}
                                >

                                    <CartesianGrid
                                        strokeDasharray="3 3"
                                    />

                                    <XAxis
                                        dataKey="time"
                                    />

                                    <YAxis />

                                    <Tooltip />

                                    <Line
                                        type="monotone"
                                        dataKey="humidity"
                                        strokeWidth={2}
                                        dot={false}
                                    />

                                </LineChart>

                            </ResponsiveContainer>

                        </div>

                    </div>


                    {/* WIND */}

                    <div className="analysis-card">

                        <div className="analysis-card__header">

                            <div>

                                <h3>
                                    Wind Speed Trend
                                </h3>

                                <span>
                                    Hourly wind-speed observations
                                </span>

                            </div>

                        </div>


                        <div className="chart-container">

                            <ResponsiveContainer
                                width="100%"
                                height={350}
                            >

                                <LineChart
                                    data={chartData}
                                >

                                    <CartesianGrid
                                        strokeDasharray="3 3"
                                    />

                                    <XAxis
                                        dataKey="time"
                                    />

                                    <YAxis />

                                    <Tooltip />

                                    <Line
                                        type="monotone"
                                        dataKey="wind_speed"
                                        strokeWidth={2}
                                        dot={false}
                                    />

                                </LineChart>

                            </ResponsiveContainer>

                        </div>

                    </div>


                    {/* TABLE */}

                    <div className="table-card">

                        <div className="table-card__header">

                            <h3>
                                Hourly Observations
                            </h3>

                            <span>
                                {chartData.length} records
                            </span>

                        </div>


                        <div className="table-wrapper">

                            <table>

                                <thead>

                                    <tr>

                                        <th>
                                            City
                                        </th>

                                        <th>
                                            State
                                        </th>

                                        <th>
                                            Observed At
                                        </th>

                                        <th>
                                            Temperature
                                        </th>

                                        <th>
                                            Humidity
                                        </th>

                                        <th>
                                            Wind Speed
                                        </th>

                                    </tr>

                                </thead>


                                <tbody>

                                    {filteredWeather
                                        .slice()
                                        .sort(
                                            (a, b) =>
                                                new Date(b.observed_at) -
                                                new Date(a.observed_at)
                                        )
                                        .map(
                                            (item, index) => (

                                                <tr
                                                    key={`${item.city}-${item.observed_at}-${index}`}
                                                >

                                                    <td>
                                                        {item.city}
                                                    </td>

                                                    <td>
                                                        {item.state}
                                                    </td>

                                                    <td>
                                                        {item.observed_at}
                                                    </td>

                                                    <td>
                                                        {item.temperature} °C
                                                    </td>

                                                    <td>
                                                        {item.humidity} %
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

                </>

            )}


            {!loading &&
                !error &&
                chartData.length === 0 && (

                <div className="empty-state">

                    No hourly weather data available.

                </div>

            )}

        </section>

    );

}

export default HourlyWeather;