function ValidationPanel({
    validation,
    onValidate,
    loading,
}) {

    return (
        <section className="etl-card validation-panel">

            <div className="section-heading">

                <div className="section-title">

                    <span className="section-number">
                        05
                    </span>

                    <div>

                        <h2>
                            Data Validation
                        </h2>

                        <p>
                            Verify that the dataset is
                            ready for migration.
                        </p>

                    </div>

                </div>

                <span className="current-badge">
                    Current Step
                </span>

            </div>


            {!validation && (

                <button
                    className="primary-button"
                    onClick={onValidate}
                    disabled={loading}
                >

                    {loading
                        ? "Validating..."
                        : "Run Validation"}

                </button>

            )}


            {validation && (

                <div className={
                    validation.valid
                        ? "validation-success"
                        : "validation-failed"
                }>

                    <strong>

                        {validation.valid
                            ? "✓ Validation Passed"
                            : "✕ Validation Failed"}

                    </strong>


                    {validation.message && (

                        <p>
                            {validation.message}
                        </p>

                    )}


                    {validation.errors &&
                        validation.errors.length > 0 && (

                        <ul>

                            {validation.errors.map(
                                (error, index) => (

                                    <li key={index}>
                                        {error}
                                    </li>

                                )
                            )}

                        </ul>

                    )}

                </div>

            )}

        </section>
    );
}


export default ValidationPanel;