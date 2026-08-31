import { useState } from "react";

import FileUpload from "../components/etl/FileUpload";
import DatasetProfile from "../components/etl/DatasetProfile";
import DataPreview from "../components/etl/DataPreview";
import ETLProcess from "../components/etl/EtlProcess";
import CleaningPanel from "../components/etl/CleaningPanel";
import TransformationPanel from "../components/etl/TransformationPanel";
import ValidationPanel from "../components/etl/ValidationPanel";
import MigrationPanel from "../components/etl/MigrationPanel";

import {
    uploadCSV,
    cleanData,
    transformData,
    validateData,
    migrateData,
} from "../services/etlApi";

import "../styles/etl.scss";


function ETLPage() {

    const [loading, setLoading] =
        useState(false);

    const [cleaningLoading, setCleaningLoading] =
        useState(false);

    const [transformLoading, setTransformLoading] =
        useState(false);

    const [validationLoading, setValidationLoading] =
        useState(false);

    const [migrationLoading, setMigrationLoading] =
        useState(false);


    const [error, setError] =
        useState("");


    const [jobId, setJobId] =
        useState(null);

    const [filename, setFilename] =
        useState("");


    const [profile, setProfile] =
        useState(null);

    const [preview, setPreview] =
        useState([]);


    const [cleanedProfile, setCleanedProfile] =
        useState(null);

    const [cleanedPreview, setCleanedPreview] =
        useState([]);


    const [transformedProfile, setTransformedProfile] =
        useState(null);

    const [transformedPreview, setTransformedPreview] =
        useState([]);


    const [validation, setValidation] =
        useState(null);


    const [migrated, setMigrated] =
        useState(false);


    const [currentStep, setCurrentStep] =
        useState(1);


    // =========================================
    // UPLOAD
    // =========================================

    async function handleUpload(file) {

        setLoading(true);

        setError("");

        try {

            const result =
                await uploadCSV(file);


            setJobId(
                result.job_id
            );

            setFilename(
                result.filename
            );

            setProfile(
                result.profile
            );

            setPreview(
                result.preview
            );


            setCurrentStep(3);

        } catch (error) {

            setError(
                error.message
            );

        } finally {

            setLoading(false);
        }
    }


    // =========================================
    // CLEAN
    // =========================================

    async function handleClean(
        missingAction,
        removeDuplicates
    ) {

        setCleaningLoading(true);

        setError("");

        try {

            const result =
                await cleanData(
                    jobId,
                    missingAction,
                    removeDuplicates
                );


            setCleanedProfile(
                result.profile
            );

            setCleanedPreview(
                result.preview
            );


            setCurrentStep(4);

        } catch (error) {

            setError(
                error.message
            );

        } finally {

            setCleaningLoading(false);
        }
    }


    // =========================================
    // TRANSFORM
    // =========================================

    async function handleTransform(
        renameMap,
        removeColumns,
        typeMap
    ) {

        setTransformLoading(true);

        setError("");

        try {

            const result =
                await transformData(
                    jobId,
                    renameMap,
                    removeColumns,
                    typeMap
                );


            setTransformedProfile(
                result.profile
            );

            setTransformedPreview(
                result.preview
            );


            setCurrentStep(5);

        } catch (error) {

            setError(
                error.message
            );

        } finally {

            setTransformLoading(false);
        }
    }


    // =========================================
    // VALIDATE
    // =========================================

    async function handleValidate() {

        setValidationLoading(true);

        setError("");

        try {

            const result =
                await validateData(
                    jobId
                );


            setValidation(
                result
            );


            if (result.valid) {

                setCurrentStep(6);

            }

        } catch (error) {

            setError(
                error.message
            );

        } finally {

            setValidationLoading(false);
        }
    }


    // =========================================
    // MIGRATE
    // =========================================

    async function handleMigrate(
        tableName
    ) {

        setMigrationLoading(true);

        setError("");

        try {

            await migrateData(
                jobId,
                tableName
            );


            setMigrated(true);

            setCurrentStep(7);

        } catch (error) {

            setError(
                error.message
            );

        } finally {

            setMigrationLoading(false);
        }
    }


    // =========================================
    // COLUMNS FOR TRANSFORMATION
    // =========================================

    const transformationColumns =
        transformedProfile?.column_details
            ?.map((column) => column.name)
        ||
        cleanedProfile?.column_details
            ?.map((column) => column.name)
        ||
        profile?.column_details
            ?.map((column) => column.name)
        ||
        [];


    return (

        <div className="etl-page">


            {/* =====================================
                HEADER
            ===================================== */}

            <div className="etl-header">

                <h1>
                    ETL Data Preprocessing
                </h1>

                <p>
                    Upload, profile, clean, transform,
                    validate and migrate your dataset.
                </p>

            </div>


            {/* =====================================
                PROCESS
            ===================================== */}

            <ETLProcess
                currentStep={currentStep}
            />


            {/* =====================================
                UPLOAD
            ===================================== */}

            <FileUpload
                onUpload={handleUpload}
                loading={loading}
            />


            {/* =====================================
                ERROR
            ===================================== */}

            {error && (

                <div className="error-message">
                    {error}
                </div>

            )}


            {/* =====================================
                FILE
            ===================================== */}

            {filename && (

                <div className="file-info">

                    <strong>
                        Uploaded File:
                    </strong>

                    <span>
                        {filename}
                    </span>

                </div>

            )}


            {/* =====================================
                PROFILE
            ===================================== */}

            {profile && (

                <>

                    <DatasetProfile
                        profile={profile}
                    />


                    <DataPreview
                        data={preview}
                        title="Original Data Preview"
                    />

                </>

            )}


            {/* =====================================
                CLEAN
            ===================================== */}

            {jobId && !cleanedProfile && (

                <CleaningPanel
                    onClean={handleClean}
                    loading={cleaningLoading}
                />

            )}


            {/* =====================================
                CLEANED DATA
            ===================================== */}

            {cleanedProfile && (

                <>

                    <div className="result-label">
                        Cleaning Result
                    </div>


                    <DatasetProfile
                        profile={cleanedProfile}
                    />


                    <DataPreview
                        data={cleanedPreview}
                        title="Cleaned Data Preview"
                    />

                </>

            )}


            {/* =====================================
                TRANSFORM
            ===================================== */}

            {cleanedProfile &&
                !transformedProfile && (

                <TransformationPanel
                    columns={
                        transformationColumns
                    }
                    onTransform={
                        handleTransform
                    }
                    loading={
                        transformLoading
                    }
                />

            )}


            {/* =====================================
                TRANSFORMED DATA
            ===================================== */}

            {transformedProfile && (

                <>

                    <div className="result-label">
                        Transformation Result
                    </div>


                    <DatasetProfile
                        profile={
                            transformedProfile
                        }
                    />


                    <DataPreview
                        data={
                            transformedPreview
                        }
                        title="Transformed Data Preview"
                    />

                </>

            )}


            {/* =====================================
                VALIDATE
            ===================================== */}

            {transformedProfile &&
                !validation && (

                <ValidationPanel
                    validation={
                        validation
                    }
                    onValidate={
                        handleValidate
                    }
                    loading={
                        validationLoading
                    }
                />

            )}


            {/* =====================================
                MIGRATE
            ===================================== */}

            {validation?.valid && (

                <MigrationPanel
                    onMigrate={
                        handleMigrate
                    }
                    loading={
                        migrationLoading
                    }
                    migrated={
                        migrated
                    }
                />

            )}

        </div>
    );
}


export default ETLPage;