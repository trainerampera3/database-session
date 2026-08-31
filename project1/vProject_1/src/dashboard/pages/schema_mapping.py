from pathlib import Path
import re
import pandas as pd
import streamlit as st

MAPPING_VERSION = 4

TARGET_TABLES = {
    "companies": "companies",
    "startup_funding": "startup_funding",
    "state_policies": "state_policies",
    "office_market": "office_market",
}

SOURCE_ALIASES = {
    "companies": {
        "date_of_registration": "registration_date",
        "authorized_capital": "authorized_cap",
        "paid_up_capital": "paidup_capital",
        "principal_business_activity_as_per_cin": "business_activity",
        "email": "email_addr",
    },
    "startup_funding": {
        "startup": "startup_name",
        "company_name": "startup_name",
        "industry_vertical": "sector",
        "investment_type": "funding_stage",
        "amount_usd": "funding_amount",
        "amount_usd_numeric": "funding_amount",
        "date": "funding_date",
        "investors": "investor_name",
        "investor": "investor_name",
    },
    "state_policies": {
        "policy": "policy_name",
        "industry_vertical": "sector",
        "description": "incentive_description",
        "policy_period": "effective_from",
    },
    "office_market": {
        "market_area": "locality",
        "office_grade": "property_type",
        "data_period": "market_date",
    },
}


def get_target_columns(connection, table):
    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT column_name, data_type
            FROM information_schema.columns
            WHERE table_schema = 'business_location'
              AND table_name = %s
              AND column_name NOT IN (
                  'company_id', 'funding_id', 'policy_id', 'office_id'
              )
            ORDER BY ordinal_position
            """,
            (table,),
        )
        return [
            {"name": row[0], "type": row[1]}
            for row in cursor.fetchall()
        ]


def infer_target_table(file_name, analysis):
    dataset_type = analysis.get("dataset_type")

    if dataset_type in TARGET_TABLES:
        return TARGET_TABLES[dataset_type]

    name = file_name.lower()

    if "registered" in name or "company" in name:
        return "companies"
    if "startup" in name or "funding" in name:
        return "startup_funding"
    if "policy" in name or "incentive" in name:
        return "state_policies"
    if "office" in name or "market" in name:
        return "office_market"

    raise ValueError(f"Cannot determine target table for {file_name}")


def normalize_name(value):
    return re.sub(r"[^a-z0-9]", "", str(value).lower())


def build_mapping(source_columns, target_columns, dataset_type):
    target_names = [column["name"] for column in target_columns]
    target_set = set(target_names)
    aliases = SOURCE_ALIASES.get(dataset_type, {})

    mapping = {}
    used_targets = set()

    # Exact cleaned-column matches always win.
    for source in source_columns:
        if source in target_set and source not in used_targets:
            mapping[source] = source
            used_targets.add(source)
        else:
            mapping[source] = "Do not map"

    # Aliases are used only when the exact target is not already used.
    for source in source_columns:
        if mapping[source] != "Do not map":
            continue

        target = aliases.get(source)
        if target in target_set and target not in used_targets:
            mapping[source] = target
            used_targets.add(target)
            continue

        normalized_source = normalize_name(source)

        for target in target_names:
            if target in used_targets:
                continue

            if normalize_name(target) == normalized_source:
                mapping[source] = target
                used_targets.add(target)
                break

    return mapping


def match_label(source, target):
    if target == "Do not map":
        return "Skipped"
    if source == target:
        return "Exact"
    return "Alias"


def normalize_cleaned_info(file_name, info, dataset_type):
    base_dir = Path(__file__).resolve().parents[1]
    cleaned_dir = base_dir / "data" / "cleaned"
    cleaned_dir.mkdir(parents=True, exist_ok=True)

    if isinstance(info, dict):
        path_value = info.get("path")

        if path_value:
            path = Path(path_value)
            if path.exists():
                return {
                    **info,
                    "path": str(path),
                }

    if isinstance(info, (str, Path)):
        path = Path(info)
        if path.exists():
            return {
                "path": str(path),
                "dataset_type": dataset_type,
                "target_table": TARGET_TABLES.get(dataset_type),
            }

    if hasattr(info, "getvalue") or hasattr(info, "read"):
        path = cleaned_dir / file_name

        if hasattr(info, "getvalue"):
            data = info.getvalue()
        else:
            info.seek(0)
            data = info.read()

        path.write_bytes(data)

        with path.open(
            "r",
            encoding="utf-8",
            errors="replace",
        ) as source:
            rows = max(sum(1 for _ in source) - 1, 0)

        return {
            "path": str(path),
            "rows": rows,
            "target_table": TARGET_TABLES.get(dataset_type),
            "dataset_type": dataset_type,
        }

    return None


def validate_mapping(file_name, mapping):
    usage = {}
    errors = []

    for source, target in mapping.items():
        if target == "Do not map":
            continue

        usage.setdefault(target, []).append(source)

    for target, sources in usage.items():
        if len(sources) > 1:
            errors.append(
                f"{file_name}: target column '{target}' is mapped more than once."
            )

    return errors


def render_schema_mapping(connection):
    cleaned_files = st.session_state.get("cleaned_files", {})
    analyses = st.session_state.get("analyses", {})

    if not cleaned_files:
        st.warning("No cleaned files are available.")
        return

    st.markdown("## Schema mapping")
    st.caption("Cleaned columns are matched to the database schema.")

    if "column_mappings" not in st.session_state:
        st.session_state.column_mappings = {}

    for file_name, raw_info in list(cleaned_files.items()):
        analysis = analyses.get(file_name, {})
        dataset_type = analysis.get("dataset_type")

        info = normalize_cleaned_info(
            file_name,
            raw_info,
            dataset_type,
        )

        if info is None:
            st.error(
                f"Invalid cleaned-file entry for {file_name}. Run cleaning again."
            )
            continue

        st.session_state.cleaned_files[file_name] = info
        path = Path(info["path"])

        if not path.exists():
            st.error(f"Cleaned file not found: {path}")
            continue

        target_table = info.get("target_table") or infer_target_table(
            file_name,
            analysis,
        )

        preview = pd.read_csv(
            path,
            nrows=1,
            dtype=object,
            low_memory=False,
        )

        source_columns = [
            str(column).strip()
            for column in preview.columns
            if str(column).strip()
            and not str(column).strip().lower().startswith("unnamed:")
        ]

        target_columns = get_target_columns(
            connection,
            target_table,
        )

        target_types = {
            column["name"]: column["type"]
            for column in target_columns
        }
        target_names = list(target_types)

        stored = st.session_state.column_mappings.get(file_name)
        stored_mapping = (
            stored.get("mapping")
            if isinstance(stored, dict)
            else None
        )
        stored_version = (
            stored.get("version")
            if isinstance(stored, dict)
            else None
        )

        if (
            stored_version != MAPPING_VERSION
            or not isinstance(stored_mapping, dict)
            or set(stored_mapping.keys()) != set(source_columns)
            or validate_mapping(file_name, stored_mapping)
        ):
            mapping = build_mapping(
                source_columns,
                target_columns,
                dataset_type,
            )
        else:
            mapping = stored_mapping

        rows = []

        for source in source_columns:
            target = mapping.get(
                source,
                "Do not map",
            )

            rows.append(
                {
                    "Source column": source,
                    "Target column": target,
                    "Target type": target_types.get(target, ""),
                    "Match": match_label(source, target),
                }
            )

        with st.expander(
            f"{file_name} → {target_table}",
            expanded=True,
        ):
            st.write(
                f"Cleaned rows: {info.get('rows', 0):,}"
            )

            edited = st.data_editor(
                pd.DataFrame(rows),
                hide_index=True,
                use_container_width=True,
                disabled=[
                    "Source column",
                    "Target type",
                    "Match",
                ],
                column_config={
                    "Source column": st.column_config.TextColumn(
                        "Source column"
                    ),
                    "Target column": st.column_config.SelectboxColumn(
                        "Target column",
                        options=["Do not map"] + target_names,
                        required=True,
                    ),
                    "Target type": st.column_config.TextColumn(
                        "Target type"
                    ),
                    "Match": st.column_config.TextColumn(
                        "Match"
                    ),
                },
                key=f"mapping_table_{file_name}_v{MAPPING_VERSION}",
            )

            current_mapping = {
                str(row["Source column"]): str(row["Target column"])
                for _, row in edited.iterrows()
            }

            st.session_state.column_mappings[file_name] = {
                "version": MAPPING_VERSION,
                "target_table": target_table,
                "mapping": current_mapping,
            }

    if st.button(
        "Save mapping and continue",
        type="primary",
        use_container_width=True,
    ):
        errors = []

        for file_name, config in st.session_state.column_mappings.items():
            mapping = (
                config.get("mapping", {})
                if isinstance(config, dict)
                else {}
            )
            errors.extend(
                validate_mapping(
                    file_name,
                    mapping,
                )
            )

        if errors:
            for error in errors:
                st.error(error)
            return

        st.session_state.mapping_done = True
        st.session_state.upload_stage = 5
        st.rerun()
