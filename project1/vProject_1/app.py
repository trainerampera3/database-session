import streamlit as st
from pathlib import Path
from textwrap import dedent
import re
import pandas as pd

from src.dashboard.pages.data_upload import render_data_upload
from src.dashboard.pages.data_analysis import render_data_analysis
from src.dashboard.pages.data_cleaning import render_data_cleaning
from src.dashboard.pages.schema_mapping import render_schema_mapping
from src.dashboard.pages.migration import (
    render_migration,
    render_migration_complete
)
from src.dashboard.pages.batch_log import render_batch_log
from connection import get_connection
from src.dashboard.pages.data_retrieval import (
    get_market_kpis,
    get_companies_by_state,
    get_company_registration_trend,
    get_office_market_by_city,
    get_startup_funding_by_city,
    get_policy_summary,
    get_policies_by_state,
    get_states,
    get_cities,
    get_city_office_market,
    get_city_startup_funding,
    get_state_policies,
    get_company_status_distribution,
    get_company_industry_distribution,
    # requirement-based location analysis
    get_requirement_sectors,
    get_requirement_location_analysis,
)

st.set_page_config(
    page_title="India Business Location Intelligence",
    layout="wide",
    initial_sidebar_state="collapsed"
)

BASE_DIR = Path(__file__).resolve().parent

# initialize values that need to stay available between streamlit reruns
if "main_section" not in st.session_state:
    st.session_state.main_section = "Business Dashboard"
if "dashboard_page" not in st.session_state:
    st.session_state.dashboard_page = "Overview"
if "management_page" not in st.session_state:
    st.session_state.management_page = "Upload Data"
if "upload_stage" not in st.session_state:
    st.session_state.upload_stage = 1
if "uploaded_files" not in st.session_state:
    st.session_state.uploaded_files = []
if "analyses" not in st.session_state:
    st.session_state.analyses = {}
if "cleaning_options" not in st.session_state:
    st.session_state.cleaning_options = {}
if "cleaned_files" not in st.session_state:
    st.session_state.cleaned_files = {}
if "column_mappings" not in st.session_state:
    st.session_state.column_mappings = {}
if "dataset_tables" not in st.session_state:
    st.session_state.dataset_tables = {}
if "schema_created" not in st.session_state:
    st.session_state.schema_created = False
if "analysis_done" not in st.session_state:
    st.session_state.analysis_done = False
if "cleaning_done" not in st.session_state:
    st.session_state.cleaning_done = False
if "mapping_done" not in st.session_state:
    st.session_state.mapping_done = False
if "migration_done" not in st.session_state:
    st.session_state.migration_done = False
if "migration_results" not in st.session_state:
    st.session_state.migration_results = []
if "dashboard_query" not in st.session_state:
    st.session_state.dashboard_query = ""
if "dashboard_query_result" not in st.session_state:
    st.session_state.dashboard_query_result = None

# load the dashboard css if the file exists
style_path = BASE_DIR / "static" / "style.css"

if style_path.exists():
    with open(style_path, encoding="utf-8") as file:
        st.markdown(
            f"<style>{file.read()}</style>",
            unsafe_allow_html=True
        )


def render_html(html):
    """render custom html content."""
    st.html(dedent(html))


def format_number(value):
    """format numeric values with commas."""
    if pd.isna(value):
        return "—"

    return f"{int(value):,}"


def format_currency(value):
    """format funding values into indian currency units."""
    if pd.isna(value):
        return "—"

    value = float(value)

    if abs(value) >= 10_000_000:
        return f"₹{value / 10_000_000:.1f} Cr"

    if abs(value) >= 100_000:
        return f"₹{value / 100_000:.1f} L"

    return f"₹{value:,.0f}"


def render_kpi(label, value, description=""):
    """render a kpi card."""
    render_html(
        f"""
        <div class="kpi-card">
            <div class="kpi-label">
                {label}
            </div>
            <div class="kpi-value">
                {value}
            </div>
            <div class="kpi-description">
                {description}
            </div>
        </div>
        """
    )


def render_requirement_analysis(connection):
    """render the requirement-based location analysis."""
    render_html(
        """
        <div class="section-label">
            BUSINESS REQUIREMENTS
        </div>
        <div class="chart-description">
            Select your business requirements to see locations
            that best match them.
        </div>
        """
    )

    # get the available business sectors from the database
    sector_df = get_requirement_sectors(connection)

    sectors = ["Any"]

    if not sector_df.empty:
        sectors += (
            sector_df["sector"]
            .dropna()
            .astype(str)
            .drop_duplicates()
            .tolist()
        )

    sector_col, size_col, office_col = st.columns(3)

    with sector_col:
        selected_sector = st.selectbox(
            "Business Sector",
            sectors,
            key="requirement_sector"
        )

    with size_col:
        selected_company_size = st.selectbox(
            "Company Size",
            [
                "Any",
                "Small",
                "Medium",
                "Large"
            ],
            key="requirement_company_size"
        )

    with office_col:
        selected_office_requirement = st.selectbox(
            "Office Requirement",
            [
                "Any",
                "Budget",
                "Standard",
                "Premium"
            ],
            key="requirement_office"
        )

    apply_filters = st.button(
        "Find Suitable Locations",
        type="primary",
        key="apply_requirement_filters"
    )

    current_filters = {
        "sector": selected_sector,
        "company_size": selected_company_size,
        "office": selected_office_requirement
    }

    previous_filters = st.session_state.get(
        "requirement_filter_state"
    )

    # run the analysis when the user applies filters or changes a filter
    if (
        apply_filters
        or previous_filters != current_filters
        or "requirement_results" not in st.session_state
    ):
        results = get_requirement_location_analysis(
            connection,
            selected_sector,
            selected_company_size,
            selected_office_requirement
        )

        st.session_state.requirement_results = results
        st.session_state.requirement_filter_state = current_filters

    results = st.session_state.get(
        "requirement_results",
        pd.DataFrame()
    )

    render_html(
        """
        <div class="section-label">
            LOCATION OVERVIEW
        </div>
        """
    )

    if results.empty:
        st.info(
            "No locations match the selected requirements."
        )
        return

    best_locations = len(results)

    avg_office_cost = (
        results["avg_office_cost"].mean()
    )

    total_companies = (
        results["company_count"].sum()
    )

    kpi1, kpi2, kpi3 = st.columns(3)

    with kpi1:
        render_kpi(
            "Best Locations",
            format_number(best_locations),
            "Matching locations"
        )

    with kpi2:
        render_kpi(
            "Avg Office Cost",
            f"₹{avg_office_cost:,.0f}",
            "Average rent / sqft"
        )

    with kpi3:
        render_kpi(
            "Companies",
            format_number(total_companies),
            "Across matching locations"
        )

    render_html(
        """
        <div class="section-label">
            CITY COMPARISON
        </div>
        <div class="chart-description">
            Location comparison based on the selected requirements.
        </div>
        """
    )

    display = results.copy()

    display["Funding"] = display[
        "total_funding"
    ].apply(format_currency)

    display["Office Cost"] = display[
        "avg_office_cost"
    ].apply(
        lambda value: (
            f"₹{value:,.0f}"
            if pd.notna(value)
            else "—"
        )
    )

    display = display.rename(
        columns={
            "city": "City",
            "state": "State",
            "company_count": "Companies",
            "incentive_count": "Incentives"
        }
    )

    display = display[
        [
            "City",
            "State",
            "Office Cost",
            "Companies",
            "Funding",
            "Incentives"
        ]
    ]

    st.dataframe(
        display,
        use_container_width=True,
        hide_index=True
    )


render_html(
    """
    <div class="business-navbar">
        <div class="business-brand">
            <div class="brand-main">
                AMPERA
            </div>
            <div class="brand-sub">
                LOCATION INTELLIGENCE
            </div>
        </div>
    </div>
    """
)

nav_left, nav_right, spacer = st.columns(
    [1.7, 1.5, 6.8]
)

with nav_left:
    if st.button(
        "Business Dashboard",
        key="business_dashboard_nav",
        use_container_width=True
    ):
        st.session_state.main_section = "Business Dashboard"
        st.rerun()

with nav_right:
    if st.button(
        "Data Management",
        key="data_management_nav",
        use_container_width=True
    ):
        st.session_state.main_section = "Data Management"
        st.rerun()

render_html(
    '<div class="main-nav-divider"></div>'
)

if st.session_state.main_section == "Business Dashboard":
    dashboard_columns = st.columns(4)

    dashboard_pages = [
        "Overview",
        "City Analysis",
        "Business Ecosystem",
        "Incentives"
    ]

    for index, page_name in enumerate(dashboard_pages):
        with dashboard_columns[index]:
            if st.button(
                page_name,
                key=f"dashboard_{index}",
                use_container_width=True
            ):
                st.session_state.dashboard_page = page_name
                st.rerun()

    render_html(
        '<div class="nav-divider"></div>'
    )

    connection = get_connection()

    try:
        if st.session_state.dashboard_page == "Overview":
            render_html(
                """
                <div class="hero">
                    <div class="eyebrow">
                        INDIA BUSINESS INTELLIGENCE
                    </div>
                    <div class="hero-title">
                        Business Location Intelligence
                    </div>
                    <div class="hero-description">
                        Evaluate Indian locations using
                        business ecosystem, office-market,
                        startup and policy indicators.
                    </div>
                </div>
                """
            )

            render_html(
                """
                <div class="section-label">
                    LOCATION FILTERS
                </div>
                """
            )

            states_df = get_states(connection)

            states = ["All states"]

            if not states_df.empty:
                states += (
                    states_df["state"]
                    .dropna()
                    .astype(str)
                    .tolist()
                )

            filter_col1, filter_col2 = st.columns(2)

            with filter_col1:
                selected_state = st.selectbox(
                    "State",
                    states,
                    key="overview_state"
                )

            with filter_col2:
                if selected_state == "All states":
                    cities_df = get_cities(connection)
                else:
                    cities_df = get_cities(
                        connection,
                        selected_state
                    )

                cities = ["All cities"]

                if not cities_df.empty:
                    cities += (
                        cities_df["city"]
                        .dropna()
                        .astype(str)
                        .tolist()
                    )

                selected_city = st.selectbox(
                    "City",
                    cities,
                    key="overview_city"
                )

            render_html(
                """
                <div class="section-label">
                    MARKET OVERVIEW
                </div>
                """
            )

            kpis = get_market_kpis(connection)

            if not kpis.empty:
                row = kpis.iloc[0]

                col1, col2, col3, col4 = st.columns(4)

                with col1:
                    render_kpi(
                        "Registered companies",
                        format_number(
                            row["total_companies"]
                        ),
                        "Companies in database"
                    )

                with col2:
                    render_kpi(
                        "Active companies",
                        format_number(
                            row["active_companies"]
                        ),
                        "Currently active"
                    )

                with col3:
                    render_kpi(
                        "Business states",
                        format_number(
                            row["company_states"]
                        ),
                        "States represented"
                    )

                with col4:
                    render_kpi(
                        "Startup funding",
                        format_currency(
                            row["total_funding"]
                        ),
                        "Recorded funding"
                    )

            left, right = st.columns(2)

            with left:
                render_html(
                    """
                    <div class="chart-heading">
                        Company ecosystem
                    </div>
                    <div class="chart-description">
                        Registered companies by state
                    </div>
                    """
                )

                companies = get_companies_by_state(connection)

                if not companies.empty:
                    if selected_state != "All states":
                        companies = companies[
                            companies["state"]
                            .astype(str)
                            .str.lower()
                            .eq(selected_state.lower())
                        ]

                    companies = (
                        companies
                        .sort_values(
                            "company_count",
                            ascending=False
                        )
                        .head(15)
                    )

                    if not companies.empty:
                        st.bar_chart(
                            companies,
                            x="state",
                            y="company_count",
                            x_label="State",
                            y_label="Number of companies",
                            height=330
                        )
                    else:
                        st.info(
                            "No company data available "
                            "for this state."
                        )

            with right:
                render_html(
                    """
                    <div class="chart-heading">
                        Office market
                    </div>
                    <div class="chart-description">
                        Average office rent by city
                    </div>
                    """
                )

                office = get_office_market_by_city(connection)

                if not office.empty:
                    if selected_state != "All states":
                        office = office[
                            office["state"]
                            .astype(str)
                            .str.lower()
                            .eq(selected_state.lower())
                        ]

                    office = (
                        office
                        .sort_values(
                            "avg_rent_per_sqft"
                        )
                        .head(15)
                    )

                    if not office.empty:
                        st.bar_chart(
                            office,
                            x="city",
                            y="avg_rent_per_sqft",
                            x_label="City",
                            y_label="Average rent per sq ft",
                            height=330
                        )
                    else:
                        st.info(
                            "No office-market data "
                            "available for this state."
                        )

            left, right = st.columns(2)

            with left:
                render_html(
                    """
                    <div class="chart-heading">
                        Company registrations
                    </div>
                    <div class="chart-description">
                        Registration activity over time
                    </div>
                    """
                )

                trend = get_company_registration_trend(connection)

                if not trend.empty:
                    st.line_chart(
                        trend,
                        x="year",
                        y="company_count",
                        x_label="Year",
                        y_label="Number of registrations",
                        height=300
                    )

            with right:
                render_html(
                    """
                    <div class="chart-heading">
                        Startup ecosystem
                    </div>
                    <div class="chart-description">
                        Startup funding by city
                    </div>
                    """
                )

                funding = get_startup_funding_by_city(connection)

                if not funding.empty:
                    if selected_state != "All states":
                        funding = funding[
                            funding["state"]
                            .astype(str)
                            .str.lower()
                            .eq(selected_state.lower())
                        ]

                    funding = (
                        funding
                        .sort_values(
                            "total_funding",
                            ascending=False
                        )
                        .head(15)
                    )

                    if not funding.empty:
                        st.bar_chart(
                            funding,
                            x="city",
                            y="total_funding",
                            x_label="City",
                            y_label="Total funding (₹)",
                            height=300
                        )
                    else:
                        st.info(
                            "No startup funding data "
                            "available for this state."
                        )

            render_html(
                """
                <div class="section-label">
                    LOCATION COMPARISON
                </div>
                """
            )

            office = get_office_market_by_city(connection)
            funding = get_startup_funding_by_city(connection)

            if not office.empty:
                comparison = office[
                    [
                        "city",
                        "state",
                        "avg_rent_per_sqft",
                        "avg_vacancy_rate"
                    ]
                ].copy()

                if not funding.empty:
                    comparison = comparison.merge(
                        funding[
                            [
                                "city",
                                "startup_count",
                                "total_funding"
                            ]
                        ],
                        on="city",
                        how="left"
                    )

                comparison = comparison.rename(
                    columns={
                        "city": "City",
                        "state": "State",
                        "avg_rent_per_sqft": "Avg rent / sqft",
                        "avg_vacancy_rate": "Vacancy %",
                        "startup_count": "Startups",
                        "total_funding": "Startup funding"
                    }
                )

                if selected_state != "All states":
                    comparison = comparison[
                        comparison["State"]
                        .astype(str)
                        .str.lower()
                        .eq(selected_state.lower())
                    ]

                if selected_city != "All cities":
                    comparison = comparison[
                        comparison["City"]
                        .astype(str)
                        .str.lower()
                        .eq(selected_city.lower())
                    ]

                if not comparison.empty:
                    st.dataframe(
                        comparison.head(15),
                        use_container_width=True,
                        hide_index=True
                    )
                else:
                    st.info(
                        "No comparison data available "
                        "for the selected location."
                    )

            render_requirement_analysis(connection)

            # show the query result saved from the query editor
            if (
                st.session_state.dashboard_query_result is not None
                and not st.session_state.dashboard_query_result.empty
            ):
                render_html(
                    """
                    <div class="section-label">
                        QUERY RESULT ADDED FROM QUERY EDITOR
                    </div>
                    """
                )

                render_html(
                    """
                    <div class="content-card">
                        <div class="content-title">
                            Saved query
                        </div>
                        <div class="content-subtitle">
                            The result remains available until this page is refreshed.
                        </div>
                    </div>
                    """
                )

                st.code(
                    st.session_state.dashboard_query,
                    language="sql"
                )

                st.dataframe(
                    st.session_state.dashboard_query_result,
                    use_container_width=True,
                    hide_index=True,
                    height=420
                )

                render_html(
                    '<div class="nav-divider"></div>'
                )

        elif st.session_state.dashboard_page == "City Analysis":
            render_html(
                """
                <div class="page-title">
                    City analysis
                </div>
                <div class="page-description">
                    Examine office-market and startup
                    indicators for an individual city.
                </div>
                """
            )

            cities_df = get_cities(connection)

            if cities_df.empty:
                st.warning("No cities are available.")
            else:
                city = st.selectbox(
                    "Select city",
                    cities_df["city"]
                    .dropna()
                    .astype(str)
                    .tolist(),
                    key="city_analysis_city"
                )

                office = get_city_office_market(
                    connection,
                    city
                )

                funding = get_city_startup_funding(
                    connection,
                    city
                )

                col1, col2, col3 = st.columns(3)

                with col1:
                    render_kpi(
                        "Office records",
                        format_number(len(office)),
                        "Market records"
                    )

                with col2:
                    startup_count = 0

                    if not funding.empty:
                        startup_count = (
                            funding["startup_name"]
                            .nunique()
                        )

                    render_kpi(
                        "Startups",
                        format_number(startup_count),
                        "Recorded startups"
                    )

                with col3:
                    total_funding = 0

                    if not funding.empty:
                        total_funding = (
                            funding["funding_amount"].sum()
                        )

                    render_kpi(
                        "Funding",
                        format_currency(total_funding),
                        "Recorded funding"
                    )

                render_html(
                    """
                    <div class="section-label">
                        OFFICE MARKET
                    </div>
                    """
                )

                if not office.empty:
                    display = office.rename(
                        columns={
                            "locality": "Locality",
                            "property_type": "Property type",
                            "rent_per_sqft": "Rent / sqft",
                            "rent_per_sqm": "Rent / sqm",
                            "vacancy_rate": "Vacancy %",
                            "availability": "Availability",
                            "market_date": "Market date"
                        }
                    )

                    st.dataframe(
                        display,
                        use_container_width=True,
                        hide_index=True
                    )
                else:
                    st.info(
                        "No office-market records "
                        "available for this city."
                    )

                render_html(
                    """
                    <div class="section-label">
                        STARTUP ECOSYSTEM
                    </div>
                    """
                )

                if not funding.empty:
                    sector_funding = (
                        funding
                        .groupby(
                            "sector",
                            dropna=True
                        )["funding_amount"]
                        .sum()
                        .sort_values(
                            ascending=False
                        )
                    )

                    if not sector_funding.empty:
                        sector_funding_df = (
                            sector_funding
                            .rename("funding_amount")
                            .reset_index()
                        )

                        st.bar_chart(
                            sector_funding_df,
                            x="sector",
                            y="funding_amount",
                            x_label="Sector",
                            y_label="Funding amount (₹)",
                            height=320
                        )
                else:
                    st.info(
                        "No startup funding records "
                        "available for this city."
                    )

                render_html(
                    """
                    <div class="section-label">
                        GOVERNMENT SUPPORT
                    </div>
                    """
                )

                if not office.empty:
                    state = office.iloc[0]["state"]

                    policies = get_state_policies(
                        connection,
                        state
                    )

                    if not policies.empty:
                        st.dataframe(
                            policies,
                            use_container_width=True,
                            hide_index=True
                        )
                    else:
                        st.info(
                            "No policy records available "
                            "for this state."
                        )

        elif st.session_state.dashboard_page == "Business Ecosystem":
            render_html(
                """
                <div class="page-title">
                    Business ecosystem
                </div>
                <div class="page-description">
                    Understand the scale, status and
                    industrial composition of registered
                    businesses.
                </div>
                """
            )

            left, right = st.columns(2)

            with left:
                status = get_company_status_distribution(connection)

                if not status.empty:
                    render_html(
                        """
                        <div class="chart-heading">
                            Company status
                        </div>
                        <div class="chart-description">
                            Distribution by company status
                        </div>
                        """
                    )

                    st.bar_chart(
                        status,
                        x="company_status",
                        y="company_count",
                        x_label="Company status",
                        y_label="Number of companies",
                        height=350
                    )

            with right:
                industry = get_company_industry_distribution(
                    connection
                )

                if not industry.empty:
                    render_html(
                        """
                        <div class="chart-heading">
                            Industrial classification
                        </div>
                        <div class="chart-description">
                            Most represented industrial classifications
                        </div>
                        """
                    )

                    st.bar_chart(
                        industry,
                        x="industrial_class",
                        y="company_count",
                        x_label="Industrial classification",
                        y_label="Number of companies",
                        height=350
                    )

        elif st.session_state.dashboard_page == "Incentives":
            render_html(
                """
                <div class="page-title">
                    Government incentives
                </div>
                <div class="page-description">
                    Explore state policies, sectors,
                    incentive types and business benefits.
                </div>
                """
            )

            summary = get_policy_summary(connection)

            if not summary.empty:
                row = summary.iloc[0]
                cols = st.columns(4)

                with cols[0]:
                    render_kpi(
                        "Policies",
                        format_number(
                            row["total_policies"]
                        )
                    )

                with cols[1]:
                    render_kpi(
                        "States",
                        format_number(
                            row["states_covered"]
                        )
                    )

                with cols[2]:
                    render_kpi(
                        "Sectors",
                        format_number(
                            row["sectors_covered"]
                        )
                    )

                with cols[3]:
                    render_kpi(
                        "Incentive types",
                        format_number(
                            row["incentive_types"]
                        )
                    )

            policies = get_policies_by_state(connection)

            if not policies.empty:
                render_html(
                    """
                    <div class="section-label">
                        POLICIES BY STATE
                    </div>
                    """
                )

                policies_chart = policies.head(15)

                st.bar_chart(
                    policies_chart,
                    x="state",
                    y="policy_count",
                    x_label="State",
                    y_label="Number of policies",
                    height=380
                )

                selected_policy_state = st.selectbox(
                    "View state policies",
                    policies["state"]
                    .dropna()
                    .astype(str)
                    .tolist(),
                    key="policy_state"
                )

                state_policies = get_state_policies(
                    connection,
                    selected_policy_state
                )

                if not state_policies.empty:
                    st.dataframe(
                        state_policies,
                        use_container_width=True,
                        hide_index=True
                    )
                else:
                    st.info(
                        "No policy records available "
                        "for this state."
                    )

    finally:
        connection.close()

elif st.session_state.main_section == "Data Management":
    render_html(
        """
        <div class="page-title">
            Data management
        </div>
        <div class="page-description">
            Manage data ingestion, cleaning, schema mapping,
            migration and batch processing.
        </div>
        """
    )

    upload_col, query_col, log_col = st.columns(3)

    with upload_col:
        if st.button(
            "Upload Data",
            key="management_upload",
            use_container_width=True
        ):
            st.session_state.management_page = "Upload Data"
            st.rerun()

    with query_col:
        if st.button(
            "Query Editor",
            key="management_query",
            use_container_width=True
        ):
            st.session_state.management_page = "Query Editor"
            st.rerun()

    with log_col:
        if st.button(
            "Batch Log",
            key="management_log",
            use_container_width=True
        ):
            st.session_state.management_page = "Batch Log"
            st.rerun()

    render_html(
        '<div class="management-divider"></div>'
    )

    if st.session_state.management_page == "Upload Data":
        stages = [
            ("01", "Upload"),
            ("02", "Analyse"),
            ("03", "Clean"),
            ("04", "Map Columns"),
            ("05", "Migrate")
        ]

        stage_columns = st.columns(len(stages))

        for index, (number, name) in enumerate(stages):
            with stage_columns[index]:
                current_stage = st.session_state.upload_stage

                if current_stage > index + 1:
                    status = "Completed"
                elif current_stage == index + 1:
                    status = "Current"
                else:
                    status = "Pending"

                render_html(
                    f"""
                    <div class="stage-card">
                        <div class="stage-number">
                            {number}
                        </div>
                        <div class="stage-name">
                            {name}
                        </div>
                        <div class="stage-status">
                            {status}
                        </div>
                    </div>
                    """
                )

        if st.session_state.upload_stage == 1:
            render_data_upload()

        elif st.session_state.upload_stage == 2:
            render_data_analysis()

        elif st.session_state.upload_stage == 3:
            render_data_cleaning()

        elif st.session_state.upload_stage == 4:
            connection = get_connection()

            try:
                render_schema_mapping(connection)
            finally:
                connection.close()

        elif st.session_state.upload_stage == 5:
            connection = get_connection()

            try:
                render_migration(connection)
            finally:
                connection.close()

        elif st.session_state.upload_stage == 6:
            render_migration_complete()

    elif st.session_state.management_page == "Query Editor":
        render_html(
            """
            <div class="page-title">
                Query editor
            </div>
            <div class="page-description">
                Run read-only SQL queries against the project database.
            </div>
            """
        )

        connection = get_connection()

        try:
            # load the database tables and columns for reference
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT
                        table_name,
                        column_name,
                        data_type
                    FROM information_schema.columns
                    WHERE table_schema = 'business_location'
                    ORDER BY
                        table_name,
                        ordinal_position
                    """
                )

                schema_rows = cursor.fetchall()

            schema = {}

            for table_name, column_name, data_type in schema_rows:
                if table_name not in schema:
                    schema[table_name] = []

                schema[table_name].append(
                    {
                        "Column": column_name,
                        "Data type": data_type
                    }
                )

            render_html(
                """
                <div class="section-label">
                    DATABASE REFERENCE
                </div>
                """
            )

            for table_name, columns in schema.items():
                with st.expander(
                    f"business_location.{table_name}",
                    expanded=False
                ):
                    st.dataframe(
                        pd.DataFrame(columns),
                        use_container_width=True,
                        hide_index=True
                    )

            render_html(
                """
                <div class="section-label">
                    SQL QUERY
                </div>
                """
            )

            # keep the sql text easy to read inside the editor
            st.markdown(
                """
                <style>
                div[data-testid="stTextArea"] textarea {
                    color: #111827 !important;
                    background-color: #ffffff !important;
                    caret-color: #111827 !important;
                    font-family: monospace !important;
                    font-size: 15px !important;
                    line-height: 1.5 !important;
                }
                </style>
                """,
                unsafe_allow_html=True
            )

            query = st.text_area(
                "SQL query",
                value=(
                    "SELECT *\n"
                    "FROM business_location.companies\n"
                    "LIMIT 10;"
                ),
                height=260,
                key="sql_query_editor",
                label_visibility="collapsed",
                placeholder="Write a SELECT query here..."
            )

            run_query = st.button(
                "Run Query",
                type="primary",
                use_container_width=False,
                key="run_sql_query"
            )

            def validate_read_only_query(sql):
                """allow only one select or with statement."""

                if not sql or not sql.strip():
                    return (
                        False,
                        "Enter a SQL query first."
                    )

                # remove comments before checking the query
                cleaned = re.sub(
                    r"/\*.*?\*/",
                    "",
                    sql,
                    flags=re.DOTALL
                )

                cleaned = re.sub(
                    r"--[^\n]*",
                    "",
                    cleaned
                ).strip()

                if cleaned.endswith(";"):
                    cleaned = cleaned[:-1].rstrip()

                if ";" in cleaned:
                    return (
                        False,
                        "Only one SQL statement can be executed at a time."
                    )

                first_keyword = re.match(
                    r"^\s*([A-Za-z]+)",
                    cleaned
                )

                if not first_keyword:
                    return (
                        False,
                        "Enter a valid SELECT query."
                    )

                keyword = first_keyword.group(1).upper()

                if keyword not in {"SELECT", "WITH"}:
                    return (
                        False,
                        "Only read-only SELECT or WITH queries are allowed."
                    )

                blocked = re.search(
                    r"\b("
                    r"INSERT|UPDATE|DELETE|DROP|ALTER|TRUNCATE|"
                    r"CREATE|GRANT|REVOKE|CALL|DO|COPY|VACUUM|"
                    r"ANALYZE|REFRESH|MERGE"
                    r")\b",
                    cleaned,
                    flags=re.IGNORECASE
                )

                if blocked:
                    return (
                        False,
                        f"'{blocked.group(1).upper()}' operations are not allowed."
                    )

                return True, ""

            if run_query:
                valid, message = validate_read_only_query(query)

                if not valid:
                    st.error(message)
                else:
                    try:
                        with connection.cursor() as cursor:
                            cursor.execute(
                                "SET TRANSACTION READ ONLY"
                            )

                            cursor.execute(query)

                            rows = cursor.fetchall()

                            columns = [
                                description.name
                                for description in cursor.description
                            ]

                        result = pd.DataFrame(
                            rows,
                            columns=columns
                        )

                        connection.rollback()

                        st.success(
                            f"Query executed successfully — "
                            f"{len(result):,} row(s) returned."
                        )

                        render_html(
                            """
                            <div class="section-label">
                                QUERY RESULT
                            </div>
                            """
                        )

                        if result.empty:
                            st.info(
                                "The query executed successfully "
                                "but returned no rows."
                            )
                        else:
                            st.dataframe(
                                result,
                                use_container_width=True,
                                hide_index=True,
                                height=500
                            )

                            # keep the result in session state so the dashboard can use it
                            st.session_state.dashboard_query = query
                            st.session_state.dashboard_query_result = result.copy()

                            add_to_dashboard = st.button(
                                "Add to Dashboard",
                                type="primary",
                                key="add_query_to_dashboard"
                            )

                            if add_to_dashboard:
                                st.session_state.main_section = (
                                    "Business Dashboard"
                                )

                                st.session_state.dashboard_page = (
                                    "Overview"
                                )

                                st.rerun()

                    except Exception as error:
                        connection.rollback()

                        st.error(
                            f"Query failed: {error}"
                        )

        finally:
            connection.close()

    elif st.session_state.management_page == "Batch Log":
        connection = get_connection()

        try:
            render_batch_log(connection)
        finally:
            connection.close()

