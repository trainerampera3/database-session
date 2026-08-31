function ETLProcess({ currentStep }) {

    const steps = [
        "Upload",
        "Profile",
        "Clean",
        "Transform",
        "Validate",
        "Migrate",
    ];


    return (

        <div className="etl-process">

            {steps.map((step, index) => {

                const stepNumber = index + 1;

                const completed =
                    stepNumber < currentStep;

                const active =
                    stepNumber === currentStep;


                return (

                    <div
                        className="process-item"
                        key={step}
                    >

                        <div
                            className={`process-step ${
                                completed
                                    ? "completed"
                                    : ""
                            } ${
                                active
                                    ? "active"
                                    : ""
                            }`}
                        >

                            <div className="step-circle">

                                {completed
                                    ? "✓"
                                    : stepNumber
                                }

                            </div>


                            <span>
                                {step}
                            </span>

                        </div>


                        {index <
                            steps.length - 1 && (

                            <div
                                className={`step-line ${
                                    completed
                                        ? "completed"
                                        : ""
                                }`}
                            />

                        )}

                    </div>

                );

            })}

        </div>

    );
}


export default ETLProcess;