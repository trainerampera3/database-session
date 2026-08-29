function KPICards({
    weatherData,
    locationsCount,
}) {
    const data = Array.isArray(weatherData)
        ? weatherData
        : [];

    const average = (values) => {
        if (!values.length) return 0;

        return (
            values.reduce((sum, value) => sum + value, 0) /
            values.length
        );
    };

    const temperatures = data
        .map((item) => Number(item.temperature))
        .filter((value) => !Number.isNaN(value));

    const humidities = data
        .map((item) => Number(item.humidity))
        .filter((value) => !Number.isNaN(value));

    const windSpeeds = data
        .map((item) => Number(item.wind_speed))
        .filter((value) => !Number.isNaN(value));

    const avgTemperature = average(temperatures);
    const avgHumidity = average(humidities);
    const avgWind = average(windSpeeds);

    const cards = [
        {
            title: "Average Temperature",
            value: `${avgTemperature.toFixed(1)}°C`,
            icon: "🌡",
        },
        {
            title: "Average Humidity",
            value: `${avgHumidity.toFixed(1)}%`,
            icon: "💧",
        },
        {
            title: "Average Wind Speed",
            value: `${avgWind.toFixed(1)} km/h`,
            icon: "💨",
        },
        {
            title: "Cities Monitored",
            value: locationsCount,
            icon: "📍",
        },
    ];

    return (
        <div className="kpi-grid">
            {cards.map((card) => (
                <div className="kpi-card" key={card.title}>
                    <div className="kpi-card__top">
                        <span className="kpi-card__title">
                            {card.title}
                        </span>

                        <span className="kpi-card__icon">
                            {card.icon}
                        </span>
                    </div>

                    <div className="kpi-card__value">
                        {card.value}
                    </div>
                </div>
            ))}
        </div>
    );
}

export default KPICards;