import { useState } from "react";


function MigrationPanel({
    onMigrate,
    loading,
    migrated,
}) {

    const [tableName, setTableName] =
        useState("etl_data");


    function handleSubmit(event) {

        event.preventDefault();

        if (!tableName.trim()) {
            return;
        }

        onMigrate(
            tableName.trim()
        );
    }


    return (
        <section className="etl-card migration-panel">

            <div className="section-heading">

                <div className="section-title">

                    <span className="section-number">
                        06
                    </span>

                    <div>

                        <h2>
                            PostgreSQL Migration
                        </h2>

                        <p>
                            Store the validated dataset
                            in PostgreSQL.
                        </p>

                    </div>

                </div>

                <span className="database-badge">
                    PostgreSQL
                </span>

            </div>


            {!migrated && (

                <form onSubmit={handleSubmit}>

                    <div className="form-group">

                        <label>
                            PostgreSQL Table Name
                        </label>

                        <input
                            type="text"
                            value={tableName}
                            onChange={(event) =>
                                setTableName(
                                    event.target.value
                                )
                            }
                            placeholder="etl_data"
                        />

                    </div>


                    <button
                        type="submit"
                        className="primary-button"
                        disabled={loading}
                    >

                        {loading
                            ? "Migrating..."
                            : "Migrate to PostgreSQL"}

                    </button>

                </form>

            )}


            {migrated && (

                <div className="validation-success">

                    <strong>
                        ✓ Migration Completed
                    </strong>

                    <p>
                        Your validated dataset has
                        been successfully stored in
                        PostgreSQL.
                    </p>

                </div>

            )}

        </section>
    );
}


export default MigrationPanel;