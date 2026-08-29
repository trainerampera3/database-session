import React from "react";

import { useEffect, useState } from "react";

import { getLocations } from "../services/api";


function LocationSelector({ value, onChange }) {

    const [locations, setLocations] = useState([]);

    const [loading, setLoading] = useState(true);

    const [error, setError] = useState("");


    useEffect(() => {

        async function loadLocations() {

            try {

                setLoading(true);

                const data = await getLocations();

                console.log(
                    "Locations API response:",
                    data
                );

                setLocations(
                    Array.isArray(data)
                        ? data
                        : []
                );

            } catch (err) {

                console.error(
                    "Location loading failed:",
                    err
                );

                setError(
                    "Unable to load locations"
                );

                setLocations([]);

            } finally {

                setLoading(false);

            }

        }

        loadLocations();

    }, []);


    return (

        <div className="location-selector">

            <label>
                Location
            </label>


            <select
                value={value || ""}
                onChange={(event) =>
                    onChange(event.target.value)
                }
                disabled={loading}
            >

                <option value="">
                    {loading
                        ? "Loading locations..."
                        : "Select a city"}
                </option>


                {locations.map((location) => (

                    <option
                        key={location.location_id}
                        value={location.location_id}
                    >

                        {location.city}, {location.state}

                    </option>

                ))}

            </select>


            {error && (
                <small className="form-error">
                    {error}
                </small>
            )}

        </div>

    );
}

export default LocationSelector;