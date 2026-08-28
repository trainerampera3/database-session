import { useEffect, useState } from "react";
import { getLocations } from "../services/api";

function LocationSelector({ value, onChange }) {
    const [locations, setLocations] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        async function loadLocations() {
            try {
                const data = await getLocations();

                console.log("Locations API response:", data);

                setLocations(Array.isArray(data) ? data : []);
            } catch (error) {
                console.error("Location loading failed:", error);
                setLocations([]);
            } finally {
                setLoading(false);
            }
        }

        loadLocations();
    }, []);

    return (
        <div className="filter">
            <label className="filter__label">
                Location
            </label>

            <select
                className="filter__select"
                value={value}
                onChange={(event) => onChange(event.target.value)}
            >
                <option value="">
                    All Locations
                </option>

                {loading ? (
                    <option disabled>
                        Loading...
                    </option>
                ) : (
                    locations.map((location) => (
                        <option
                            key={location.location_id}
                            value={location.location_id}
                        >
                            {location.city}
                        </option>
                    ))
                )}
            </select>
        </div>
    );
}

export default LocationSelector;