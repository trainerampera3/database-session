const API_BASE_URL = "http://127.0.0.1:8000";


async function request(endpoint) {

    const response =
        await fetch(
            `${API_BASE_URL}${endpoint}`
        );


    if (!response.ok) {

        throw new Error(
            `API request failed: ${response.status} ${response.statusText}`
        );

    }


    return response.json();

}


export async function getLocations() {

    return request("/locations");

}


export async function getCurrentWeather() {

    return request("/weather/current");

}


export async function getWeatherHistory(
    startDate,
    endDate,
    locationId = null,
    limit = 100
) {

    const params =
        new URLSearchParams();


    params.append(
        "start_date",
        startDate
    );

    params.append(
        "end_date",
        endDate
    );

    params.append(
        "limit",
        limit
    );

    params.append(
        "offset",
        "0"
    );


    if (locationId) {

        params.append(
            "location_id",
            locationId
        );

    }


    return request(
        `/weather/history?${params.toString()}`
    );

}


export async function getETLLogs() {

    return request("/etl/logs");

}

export async function executeQuery(query) {

    const response = await fetch(
        `${API_BASE_URL}/query`,
        {
            method: "POST",

            headers: {
                "Content-Type": "application/json",
            },

            body: JSON.stringify({
                query: query,
            }),
        }
    );


    const data = await response.json();


    if (!response.ok) {

        throw new Error(
            data.detail ||
            "Query execution failed"
        );

    }


    return data;
}