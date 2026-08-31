import { useState } from "react";
import "../../styles/etlpage.scss";

function CleaningPanel({
    onClean,
    loading,
}) {

    const [missingAction, setMissingAction] =
        useState("none");

    const [removeDuplicates, setRemoveDuplicates] =
        useState(false);


    function handleSubmit(event) {

        event.preventDefault();

        onClean(
            missingAction,
            removeDuplicates
        );
    }


    return (

        <section className="cleaning-panel">

            <div className="section-heading">

                <div>

                    <span className="section-number">
                        03
                    </span>

                    <div>

                        <h2>
                            Data Cleaning
                        </h2>

                        <p>
                            Handle missing values and
                            duplicate records.
                        </p>

                    </div>

                </div>

                <span className="current-badge">
                    Current Step
                </span>

            </div>


            <form onSubmit={handleSubmit}>

                <div className="form-group">

                    <label>
                        Missing Value Action
                    </label>

                    <select
                        value={missingAction}
                        onChange={(event) =>
                            setMissingAction(
                                event.target.value
                            )
                        }
                    >

                        <option value="none">
                            Do Nothing
                        </option>

                        <option value="drop">
                            Drop Rows
                        </option>

                        <option value="mean">
                            Fill Numeric Values with Mean
                        </option>

                        <option value="median">
                            Fill Numeric Values with Median
                        </option>

                        <option value="zero">
                            Fill Numeric Values with Zero
                        </option>

                    </select>

                </div>


                <label className="checkbox-group">

                    <input
                        type="checkbox"
                        checked={removeDuplicates}
                        onChange={(event) =>
                            setRemoveDuplicates(
                                event.target.checked
                            )
                        }
                    />

                    <span>
                        Remove duplicate rows
                    </span>

                </label>


                <button
                    type="submit"
                    disabled={loading}
                    className="primary-button"
                >

                    {loading
                        ? "Cleaning..."
                        : "Apply Cleaning"
                    }

                </button>

            </form>

        </section>

    );
}


export default CleaningPanel;