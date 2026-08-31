from pathlib import Path
import time

import pandas as pd
import streamlit as st

from services.batch_loader import (
    BATCH_SIZE,
    create_stored_procedures,
    migrate_csv_in_batches,
)

TARGET_TABLES = {
    "companies": "companies",
    "startup_funding": "startup_funding",
    "state_policies": "state_policies",
    "office_market": "office_market",
}

# Normalize cleaned-file information from current or legacy session state.
def normalize_cleaned_info(file_name, info, analysis):
    base_dir = Path(__file__).resolve().parents[1]
    cleaned_dir = base_dir / "data" / "cleaned"
    cleaned_dir.mkdir(parents=True, exist_ok=True)
    dataset_type = analysis.get("dataset_type")

    if isinstance(info, dict) and info.get("path"):
        path = Path(info["path"])
        if path.exists():
            return {**info, "path": str(path)}

    if hasattr(info, "getvalue") or hasattr(info, "read"):
        path = cleaned_dir / file_name
        if hasattr(info, "getvalue"):
            data = info.getvalue()
        else:
            info.seek(0)
            data = info.read()
        path.write_bytes(data)
        rows = max(
            sum(1 for _ in path.open("r", encoding="utf-8", errors="replace")) - 1,
            0,
        )
        return {
            "path": str(path),
            "rows": rows,
            "target_table": TARGET_TABLES.get(dataset_type),
            "dataset_type": dataset_type,
        }

    return None

# Normalize mapping session data.
def normalize_mapping(config):
    if isinstance(config, dict) and "mapping" in config:
        return config["mapping"], config.get("target_table")
    return config if isinstance(config, dict) else {}, None

# Count rows without loading the whole CSV.
def count_csv_rows(path):
    total = 0
    for chunk in pd.read_csv(
        path,
        chunksize=BATCH_SIZE,
        usecols=[0],
        low_memory=False,
        dtype=object,
    ):
        total += len(chunk)
    return total

# Clear target tables for a full reload.
def clear_target_tables(connection):
    with connection.cursor() as cursor:
        cursor.execute(
            """
            TRUNCATE TABLE
                business_location.companies,
                business_location.startup_funding,
                business_location.state_policies,
                business_location.office_market
            RESTART IDENTITY CASCADE
            """
        )
    connection.commit()

# Render the migration stage.
def render_migration(connection):
    cleaned_files = st.session_state.get("cleaned_files", {})
    mappings = st.session_state.get("column_mappings", {})

    if not cleaned_files:
        st.warning("No cleaned files are available for migration.")
        return

    st.markdown("## Migration")

    rows = []

    for file_name, raw_info in list(cleaned_files.items()):
        analysis = st.session_state.get("analyses", {}).get(file_name, {})
        info = normalize_cleaned_info(file_name, raw_info, analysis)

        if info is None:
            st.error(f"Invalid cleaned-file entry for {file_name}. Run cleaning again.")
            continue

        st.session_state.cleaned_files[file_name] = info
        path = Path(info["path"])

        if not path.exists():
            st.error(f"Cleaned file not found: {path}")
            continue

        mapping, mapped_target = normalize_mapping(
            mappings.get(file_name, {})
        )
        target_table = mapped_target or info.get("target_table")
        row_count = info.get("rows")

        if row_count is None:
            row_count = count_csv_rows(path)

        rows.append(
            {
                "source_file": file_name,
                "cleaned_file": path.name,
                "target_table": target_table or "Not mapped",
                "rows": row_count,
                "path": str(path),
                "mapping": mapping,
            }
        )

    st.markdown("### Datasets ready for migration")
    st.dataframe(
        pd.DataFrame(
            [
                {
                    "Source file": row["source_file"],
                    "Cleaned file": row["cleaned_file"],
                    "Target table": row["target_table"],
                    "Rows": f"{row['rows']:,}",
                    "Status": (
                        "Ready"
                        if Path(row["path"]).exists()
                        and row["target_table"] != "Not mapped"
                        else "Not ready"
                    ),
                }
                for row in rows
            ]
        ),
        use_container_width=True,
        hide_index=True,
    )

    st.caption(
        f"Cleaned CSV files are processed in {BATCH_SIZE:,}-row batches through PostgreSQL stored procedures."
    )

    if st.session_state.get("migration_done"):
        render_migration_complete()
        return

    fresh_load = st.checkbox(
        "Fresh migration: clear existing rows before loading",
        value=True,
        help=(
            "Use this for your current project so previous partial migrations "
            "do not cause rows to appear as rejected by the unique indexes."
        ),
    )

    if fresh_load:
        st.caption(
            "Existing rows in the four business_location target tables will be removed before this migration."
        )
    else:
        st.caption(
            "Existing rows are kept; rows already present will be skipped by ON CONFLICT DO NOTHING."
        )

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Back to mapping", use_container_width=True):
            st.session_state.upload_stage = 4
            st.rerun()

    with col2:
        start = st.button(
            "Start migration",
            type="primary",
            use_container_width=True,
        )

    if not start:
        return

    invalid = []
    for row in rows:
        if not Path(row["path"]).exists():
            invalid.append(row["source_file"])
        elif row["target_table"] == "Not mapped":
            invalid.append(row["source_file"])
        elif not isinstance(row["mapping"], dict) or not row["mapping"]:
            invalid.append(row["source_file"])

    if invalid:
        st.error(
            "These datasets are not ready: " + ", ".join(invalid)
        )
        return

    try:
        if fresh_load:
            clear_target_tables(connection)

        create_stored_procedures(connection)
    except Exception as error:
        connection.rollback()
        st.error(f"Migration setup failed: {error}")
        return

    results = []
    activity_log = []
    migration_started = time.perf_counter()
    progress = st.progress(0)
    status = st.empty()

    for index, row in enumerate(rows, start=1):
        status.write(
            f"Migrating {row['source_file']} → {row['target_table']}"
        )

        file_started = time.perf_counter()

        try:
            result = migrate_csv_in_batches(
                connection,
                row["path"],
                row["source_file"],
                row["target_table"],
                row["mapping"],
                BATCH_SIZE,
            )
        except Exception as error:
            connection.rollback()
            result = {
                "source_file": row["source_file"],
                "target_table": row["target_table"],
                "batches": 0,
                "rows_processed": 0,
                "rows_inserted": 0,
                "rows_rejected": row["rows"],
                "invalid_rows": row["rows"],
                "status": "Failed",
                "error": str(error),
            }

        results.append(result)

        elapsed = max(int(round(time.perf_counter() - migration_started)), 0)
        file_elapsed = max(int(round(time.perf_counter() - file_started)), 0)
        activity_log.append(
            {
                "elapsed": elapsed,
                "source_file": row["source_file"],
                "target_table": row["target_table"],
                "rows_processed": result.get("rows_processed", 0),
                "rows_inserted": result.get("rows_inserted", 0),
                "rows_rejected": result.get("rows_rejected", 0),
                "duration": file_elapsed,
                "status": result.get("status", "Completed"),
            }
        )

        progress.progress(index / len(rows))

    status.empty()
    st.session_state.migration_results = results
    st.session_state.migration_activity_log = activity_log
    st.session_state.migration_duration = max(int(round(time.perf_counter() - migration_started)), 0)
    st.session_state.migration_done = True
    # Keep the migration stage visible so the completion report renders in place.
    st.session_state.upload_stage = 5
    st.rerun()

# Render the migration result report.
def render_migration_report(results):
    if not results:
        st.warning("No migration results are available.")
        return

    batches = sum(result.get("batches", 0) for result in results)
    processed = sum(result.get("rows_processed", 0) for result in results)
    inserted = sum(result.get("rows_inserted", 0) for result in results)
    rejected = sum(result.get("rows_rejected", 0) for result in results)
    rate = inserted / processed * 100 if processed else 0

    st.markdown(
        """
        <style>
        .migration-complete-card, .load-report-card {
            background: #20212c;
            border: 1px solid #373846;
            border-radius: 10px;
            padding: 16px 18px;
            margin-top: 12px;
        }
        .migration-complete-head {
            display: flex;
            align-items: flex-start;
            justify-content: space-between;
            gap: 20px;
        }
        .migration-complete-title {
            color: #f2f2f7;
            font-size: 19px;
            font-weight: 600;
        }
        .migration-complete-subtitle {
            color: #8d8da0;
            font-size: 13px;
            margin-top: 2px;
        }
        .migration-complete-status {
            color: #a9a4d8;
            font-size: 13px;
            padding-top: 4px;
        }
        .migration-progress {
            width: 100%;
            height: 6px;
            background: #343545;
            border-radius: 8px;
            overflow: hidden;
            margin: 18px 0 14px;
        }
        .migration-progress-fill {
            width: 100%;
            height: 100%;
            background: #9a8de6;
        }
        .migration-log {
            margin: 0;
            padding: 0;
            background: transparent;
            border: 0;
            color: #a8a8ba;
            font-size: 12px;
            line-height: 1.95;
            white-space: pre-wrap;
            font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
        }
        .load-report-title {
            color: #f2f2f7;
            font-size: 18px;
            font-weight: 600;
            margin-bottom: 16px;
        }
        .load-report-grid {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 20px;
        }
        .load-report-grid span {
            display: block;
            color: #8d8da0;
            font-size: 12px;
            margin-bottom: 5px;
        }
        .load-report-grid strong {
            color: #f0f0f5;
            font-size: 17px;
            font-weight: 500;
        }
        @media (max-width: 800px) {
            .load-report-grid {
                grid-template-columns: repeat(2, 1fr);
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("## Migration complete")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Batches", f"{batches:,}")
    c2.metric("Rows processed", f"{processed:,}")
    c3.metric("Rows inserted", f"{inserted:,}")
    c4.metric("Rows rejected", f"{rejected:,}")

    st.metric("Overall success rate", f"{rate:.2f}%")

    report = []
    for result in results:
        processed_rows = result.get("rows_processed", 0)
        inserted_rows = result.get("rows_inserted", 0)
        rejected_rows = result.get("rows_rejected", 0)

        report.append(
            {
                "Source file": result.get("source_file"),
                "Target table": result.get("target_table"),
                "Batches": result.get("batches", 0),
                "Rows processed": processed_rows,
                "Rows inserted": inserted_rows,
                "Rows rejected": rejected_rows,
                "Status": (
                    "Succeeded"
                    if rejected_rows == 0
                    else "Partial"
                    if inserted_rows > 0
                    else "Failed"
                ),
                "Error": result.get("error"),
            }
        )

    st.markdown("### Migration results")
    st.dataframe(
        pd.DataFrame(report),
        use_container_width=True,
        hide_index=True,
    )

    # Show the post-migration activity log without changing the existing result table.
    st.markdown("### Processing activity")

    activity_log = st.session_state.get("migration_activity_log", [])
    total_duration = st.session_state.get("migration_duration", 0)
    total_files = len(results)
    successful_files = sum(
        1
        for result in results
        if result.get("rows_inserted", 0) > 0 and not result.get("error")
    )

    log_lines = [f"00:00  Starting migration of {total_files} dataset(s)"]
    for item in activity_log:
        elapsed = item.get("elapsed", 0)
        minutes, seconds = divmod(elapsed, 60)
        stamp = f"{minutes:02d}:{seconds:02d}"
        log_lines.append(
            f"{stamp}  {item['source_file']} → {item['target_table']} · "
            f"{item['rows_processed']:,} rows processed · "
            f"{item['rows_inserted']:,} inserted · "
            f"{item['rows_rejected']:,} rejected"
        )

    minutes, seconds = divmod(total_duration, 60)
    final_stamp = f"{minutes:02d}:{seconds:02d}"
    log_lines.append(
        f"{final_stamp}  Load committed · "
        f"{successful_files}/{total_files} dataset(s) completed"
    )
    log_text = "\n".join(log_lines)

    st.markdown(
        f"""
        <div class="migration-complete-card">
            <div class="migration-complete-head">
                <div>
                    <div class="migration-complete-title">Migration complete</div>
                    <div class="migration-complete-subtitle">
                        {successful_files} of {total_files} dataset(s) are live in the warehouse and available on your dashboards
                    </div>
                </div>
                <div class="migration-complete-status">Complete</div>
            </div>
            <div class="migration-progress"><div class="migration-progress-fill"></div></div>
            <pre class="migration-log">{log_text}</pre>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        f"""
        <div class="load-report-card">
            <div class="load-report-title">Load report</div>
            <div class="load-report-grid">
                <div><span>Rows written</span><strong>{inserted:,}</strong></div>
                <div><span>Rows rejected</span><strong>{rejected:,}</strong></div>
                <div><span>Duration</span><strong>{total_duration} s</strong></div>
                <div><span>Datasets migrated</span><strong>{total_files}</strong></div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.caption(f"Load committed {total_duration} s after migration started")

    back_col, dashboard_col = st.columns([1, 1])

    with back_col:
        if st.button(
            "Back",
            key="migration_back_to_mapping",
            use_container_width=True,
        ):
            st.session_state.page = "Upload data"
            st.session_state.upload_stage = 4
            st.session_state.migration_done = False
            st.rerun()

    with dashboard_col:

        if st.button(
            "View in dashboard",
            key="migration_view_dashboard",
            use_container_width=True,
        ):

            st.session_state.main_section = "Business Dashboard"
            st.session_state.dashboard_page = "Overview"

            st.rerun()

# Render the completed migration screen.
def render_migration_complete(connection=None):
    render_migration_report(
        st.session_state.get("migration_results", [])
    )
