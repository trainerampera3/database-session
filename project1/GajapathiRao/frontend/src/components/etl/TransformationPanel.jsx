import { useState } from "react";

import "../../styles/etlpage.scss";
function TransformationPanel({
    columns,
    onTransform,
    loading,
}) {

    const [renameMap, setRenameMap] =
        useState({});

    const [removeColumns, setRemoveColumns] =
        useState([]);

    const [typeMap, setTypeMap] =
        useState({});


    function handleRename(
        column,
        value
    ) {

        setRenameMap((previous) => ({
            ...previous,
            [column]: value,
        }));
    }


    function handleRemove(
        column,
        checked
    ) {

        setRemoveColumns((previous) => {

            if (checked) {

                return [
                    ...previous,
                    column,
                ];
            }

            return previous.filter(
                (item) => item !== column
            );

        });
    }


    function handleType(
        column,
        value
    ) {

        setTypeMap((previous) => ({
            ...previous,
            [column]: value,
        }));
    }


    function handleSubmit(event) {

        event.preventDefault();

        const cleanedRenameMap = {};

        Object.entries(renameMap).forEach(
            ([column, value]) => {

                if (
                    value &&
                    value.trim() !== "" &&
                    value !== column
                ) {

                    cleanedRenameMap[column] =
                        value.trim();
                }

            }
        );


        const cleanedTypeMap = {};

        Object.entries(typeMap).forEach(
            ([column, value]) => {

                if (value) {
                    cleanedTypeMap[column] =
                        value;
                }

            }
        );


        onTransform(
            cleanedRenameMap,
            removeColumns,
            cleanedTypeMap
        );
    }


    return (
        <section className="etl-card transformation-panel">

            <div className="section-heading">

                <div className="section-title">

                    <span className="section-number">
                        04
                    </span>

                    <div>

                        <h2>
                            Data Transformation
                        </h2>

                        <p>
                            Rename, remove and convert
                            columns.
                        </p>

                    </div>

                </div>

                <span className="current-badge">
                    Current Step
                </span>

            </div>


            <form onSubmit={handleSubmit}>

                <div className="transform-table">

                    <div className="transform-header">

                        <span>
                            Column
                        </span>

                        <span>
                            Rename To
                        </span>

                        <span>
                            Data Type
                        </span>

                        <span>
                            Remove
                        </span>

                    </div>


                    {columns.map((column) => (

                        <div
                            className="transform-row"
                            key={column}
                        >

                            <strong>
                                {column}
                            </strong>


                            <input
                                type="text"
                                placeholder={column}
                                value={
                                    renameMap[column] ||
                                    ""
                                }
                                onChange={(event) =>
                                    handleRename(
                                        column,
                                        event.target.value
                                    )
                                }
                            />


                            <select
                                value={
                                    typeMap[column] ||
                                    ""
                                }
                                onChange={(event) =>
                                    handleType(
                                        column,
                                        event.target.value
                                    )
                                }
                            >

                                <option value="">
                                    Keep Original
                                </option>

                                <option value="integer">
                                    Integer
                                </option>

                                <option value="float">
                                    Float
                                </option>

                                <option value="string">
                                    String
                                </option>

                                <option value="date">
                                    Date
                                </option>

                            </select>


                            <input
                                type="checkbox"
                                checked={
                                    removeColumns.includes(
                                        column
                                    )
                                }
                                onChange={(event) =>
                                    handleRemove(
                                        column,
                                        event.target.checked
                                    )
                                }
                            />

                        </div>

                    ))}

                </div>


                <button
                    type="submit"
                    disabled={loading}
                    className="primary-button"
                >

                    {loading
                        ? "Transforming..."
                        : "Apply Transformation"}

                </button>

            </form>

        </section>
    );
}


export default TransformationPanel;