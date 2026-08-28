import { useEffect, useState } from "react";
import { getLocations } from "../services/api";

function LocationSelector({ onLocationChange }) {
    const [locations, setLocations] = useState([]);
    const [selectedLocation, setSelectedLocation] = useState("");

    useEffect(() => {
        async function loadLocations() {
            try {
                const response = await getLocations();

                console.log("Locations API response:", response);

                const locationData = response.data || [];

                setLocations(locationData);

                if (locationData.length > 0) {
                    setSelectedLocation(locationData[0].location_id);
                    onLocationChange(locationData[0]);
                }
            } catch (error) {
                console.error("Location loading failed:", error);
            }
        }

        loadLocations();
    }, []);

    function handleChange(event) {
        const locationId = Number(event.target.value);

        const location = locations.find(
            (item) => item.location_id === locationId
        );

        setSelectedLocation(locationId);
        onLocationChange(location);
    }

    return (
        <div className="location-selector">
            <label htmlFor="location">
                Location
            </label>

            <select
                id="location"
                value={selectedLocation}
                onChange={handleChange}
            >
                {locations.map((location) => (
                    <option
                        key={location.location_id}
                        value={location.location_id}
                    >
                        {location.city}
                    </option>
                ))}
            </select>
        </div>
    );
}

export default LocationSelector;