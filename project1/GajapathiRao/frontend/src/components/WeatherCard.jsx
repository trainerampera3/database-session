import React from "react";

import {
    MdThermostat,
    MdWaterDrop,
    MdAir
} from "react-icons/md";


function WeatherCard({ weather }) {

    if (!weather) {
        return null;
    }


    return (

        <div className="weather-card">

            <div className="weather-card__header">

                <div>

                    <h3>
                        {weather.city}
                    </h3>

                    <span>
                        {weather.state}
                    </span>

                </div>

                <div className="weather-card__time">

                    {weather.observed_at
                        ?.replace("T", " ")}

                </div>

            </div>


            <div className="weather-card__temperature">

                <MdThermostat />

                <strong>
                    {weather.temperature}
                </strong>

                <span>°C</span>

            </div>


            <div className="weather-card__metrics">

                <div>

                    <MdWaterDrop />

                    <span>
                        Humidity
                    </span>

                    <strong>
                        {weather.humidity}%
                    </strong>

                </div>


                <div>

                    <MdAir />

                    <span>
                        Wind
                    </span>

                    <strong>
                        {weather.wind_speed} km/h
                    </strong>

                </div>

            </div>

        </div>

    );
}

export default WeatherCard;