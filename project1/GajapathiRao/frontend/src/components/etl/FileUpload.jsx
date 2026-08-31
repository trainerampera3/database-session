import { useRef } from "react";
import "../../styles/etlpage.scss";

function FileUpload({
    onUpload,
    loading,
}) {

    const fileInputRef = useRef(null);


    function handleFileChange(event) {

        const file = event.target.files?.[0];

        if (!file) {
            return;
        }

        onUpload(file);
    }


    return (
        <div className="upload-section">

            <input
                ref={fileInputRef}
                type="file"
                accept=".csv"
                onChange={handleFileChange}
                hidden
            />

            <button
                type="button"
                onClick={() =>
                    fileInputRef.current?.click()
                }
                disabled={loading}
            >
                {loading
                    ? "Uploading..."
                    : "Upload CSV"
                }
            </button>

            <p>
                Upload a CSV file to start
                preprocessing.
            </p>

        </div>
    );
}


export default FileUpload;