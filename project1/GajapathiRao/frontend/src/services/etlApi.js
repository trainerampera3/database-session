const API_BASE_URL = "http://127.0.0.1:8000/etl";


export async function uploadCSV(file) {

    const formData = new FormData();

    formData.append("file", file);

    const response = await fetch(
        `${API_BASE_URL}/upload`,
        {
            method: "POST",
            body: formData,
        }
    );

    const data = await response.json();

    if (!response.ok) {

        throw new Error(
            data.detail || "Upload failed."
        );
    }

    return data;
}


export async function cleanData(
    jobId,
    missingAction,
    removeDuplicates
) {

    const response = await fetch(
        `${API_BASE_URL}/${jobId}/clean`,
        {
            method: "POST",

            headers: {
                "Content-Type": "application/json",
            },

            body: JSON.stringify({
                missing_action: missingAction,
                remove_duplicates: removeDuplicates,
            }),
        }
    );

    const data = await response.json();

    if (!response.ok) {

        throw new Error(
            data.detail || "Cleaning failed."
        );
    }

    return data;
}


export async function transformData(
    jobId,
    renameMap,
    removeColumns,
    typeMap
) {

    const response = await fetch(
        `${API_BASE_URL}/${jobId}/transform`,
        {
            method: "POST",

            headers: {
                "Content-Type": "application/json",
            },

            body: JSON.stringify({
                rename_map: renameMap,
                remove_columns: removeColumns,
                type_map: typeMap,
            }),
        }
    );

    const data = await response.json();

    if (!response.ok) {

        throw new Error(
            data.detail || "Transformation failed."
        );
    }

    return data;
}



export async function validateData(jobId) {

    const response = await fetch(
        `${API_BASE_URL}/${jobId}/validate`,
        {
            method: "POST",

            headers: {
                "Content-Type": "application/json",
            },
        }
    );

    const data = await response.json();

    if (!response.ok) {
        throw new Error(
            data.detail || "Validation failed."
        );
    }

    return data;
}
export async function migrateData(
    jobId,
    tableName
) {

    const response = await fetch(
        `${API_BASE_URL}/${jobId}/migrate`,
        {
            method: "POST",

            headers: {
                "Content-Type": "application/json",
            },

            body: JSON.stringify({
                table_name: tableName,
            }),
        }
    );

    const data = await response.json();

    if (!response.ok) {

        throw new Error(
            data.detail || "Migration failed."
        );
    }

    return data;
}