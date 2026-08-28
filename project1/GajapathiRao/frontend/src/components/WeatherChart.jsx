import {
    ResponsiveContainer,
    LineChart,
    Line,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    Legend,
} from "recharts";

function WeatherChart({ data }) {
    if (!data || data.length === 0) {
        return (
            <div className="chart-empty">
                No weather data available.
            </div>
        );
    }

    const chartData = [...data]
        .sort(
            (a, b) =>
                new Date(a.observed_at) -
                new Date(b.observed_at)
        )
        .map((item) => ({
            time: new Date(item.observed_at).toLocaleTimeString(
                [],
                {
                    hour: "2-digit",
                    minute: "2-digit",
                }
            ),
            temperature: Number(item.temperature),
            humidity: Number(item.humidity),
            wind_speed: Number(item.wind_speed),
        }));

    return (
        <div className="chart-card">
            <div className="chart-card__header">
                <div>
                    <h2>Weather Trend</h2>

                    <p>
                        Temperature, humidity and wind speed
                    </p>
                </div>
            </div>

            <div className="chart-container">
                <ResponsiveContainer width="100%" height={360}>
                    <LineChart data={chartData}>
                        <CartesianGrid strokeDasharray="3 3" />

                        <XAxis dataKey="time" />

                        <YAxis />

                        <Tooltip />

                        <Legend />

                        <Line
                            type="monotone"
                            dataKey="temperature"
                            name="Temperature (°C)"
                            strokeWidth={2}
                            dot={false}
                        />

                        <Line
                            type="monotone"
                            dataKey="humidity"
                            name="Humidity (%)"
                            strokeWidth={2}
                            dot={false}
                        />

                        <Line
                            type="monotone"
                            dataKey="wind_speed"
                            name="Wind Speed (km/h)"
                            strokeWidth={2}
                            dot={false}
                        />
                    </LineChart>
                </ResponsiveContainer>
            </div>
        </div>
    );
}

export default WeatherChart;