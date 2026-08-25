import pandas as pd
import streamlit as st
import plotly.express as px

from srcipts.data_reterival import (
    create_connection,
    get_filter_options,
    get_kpis,
    get_sales_by_year,
    get_monthly_sales,
    get_payment_sales,
    get_division_sales,
    get_top_products,
    get_product_quantity,
    get_district_sales,
    get_district_transactions,
    get_top_product,
    get_top_division,
    get_top_district,
    get_leading_payment,
)




st.set_page_config(
    page_title="Sales Intelligence Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)




st.markdown(
    """
    <style>

    .stApp {
        background: #f6f8fc;
    }

    header {
        visibility: hidden;
    }

    [data-testid="stDecoration"] {
        display: none;
    }

    .block-container {
        max-width: 1500px;
        padding-top: 1.2rem;
        padding-bottom: 2rem;
    }

    .dashboard-header {
        background: linear-gradient(
            135deg,
            #163d8f 0%,
            #315fd4 55%,
            #5b4acb 100%
        );

        display: flex;
        align-items: center;
        flex-direction: column;

        padding: 24px 30px;
        border-radius: 10px;
        margin-bottom: 18px;
        margin-top: 0px;

        color: white;

        box-shadow:
            0 8px 24px rgba(31, 70, 150, 0.18);
    }

    .dashboard-title {
        font-size: 36px;
        font-weight: 800;
        line-height: 1.1;
        margin: 0;
        letter-spacing: -0.5px;
    }

    .dashboard-subtitle {
        font-size: 15px;
        margin-top: 8px;
        opacity: 0.92;
    }

    [data-testid="stMetricLabel"] p,
    [data-testid="stMetricValue"] div {
        color: black !important;
    }

    .section-title {
        font-size: 23px;
        font-weight: 750;
        color: black;
        margin: 20px 0 10px 0;
    }

    .section-caption {
        color: black;
        font-size: 13px;
        margin-bottom: 12px;
    }

    div[data-testid="stMetric"] {
        background: white;
        border: 1px solid #e4e9f2;
        border-radius: 14px;
        padding: 17px 18px;
        min-height: 105px;
        box-shadow: 0 3px 12px rgba(20, 40, 80, 0.06);
    }

    div[data-testid="stMetricLabel"] {
        color: black;
        font-size: 13px;
        font-weight: 650;
    }

    div[data-testid="stMetricValue"] {
        color: black;
        font-size: 25px;
        font-weight: 800;
    }

    section[data-testid="stSidebar"] {
        background: #ffffff;
        border-right: 1px solid #e4e9f2;
        color: black;
    }

    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3 {
        color: #172b4d;
    }

    div[data-testid="stVerticalBlockBorderWrapper"] {
        background: white;
        border: 1px solid #e4e9f2;
        border-radius: 14px;
        box-shadow: 0 3px 12px rgba(20, 40, 80, 0.045);
    }

    div[data-testid="stAlert"] {
        border-radius: 12px;
        color: #172b4d;
    }

    div[data-testid="stTabs"] {
        background: #ffffff;
        padding: 10px 16px 0px 16px;
        border-radius: 12px 12px 0 0;
        border: 1px solid #e4e9f2;
        border-bottom: none;
        margin-bottom: -1px;
        color: #4a5568;
    }

    button[data-baseweb="tab"] {
        font-weight: 700 !important;
        font-size: 15px !important;
        color: #4a5568 !important;
        padding: 10px 20px !important;
        transition: all 0.2s ease;
    }

    button[data-baseweb="tab"][aria-selected="true"] {
        color: #315fd4 !important;
        border-bottom: 3px solid #315fd4 !important;
    }

    div[data-testid="stTabPanel"] {
        background: white;
        border: 1px solid #e4e9f2;
        border-radius: 0 0 14px 14px;
        padding: 24px;
        box-shadow: 0 3px 12px rgba(20, 40, 80, 0.045);
    }

    div[data-testid="stDataFrame"] {
        border-radius: 12px;
        overflow: hidden;
    }

    div[data-testid="stDataFrame"] canvas,
    div[data-testid="stDataFrame"] div,
    div[data-testid="stDataFrame"] span {
        color: #000000 !important;
    }

    div[data-testid="stAlert"] div {
        color: #000000 !important;
    }

    .insight-card {
        background: white;
        border: 1px solid #e4e9f2;
        border-radius: 14px;
        padding: 14px 16px;
        min-height: 88px;
        box-shadow: 0 3px 12px rgba(20, 40, 80, 0.045);
    }

    .insight-label {
        color: black;
        font-size: 12px;
        font-weight: 650;
        text-transform: uppercase;
        letter-spacing: 0.4px;
    }

    .insight-value {
        color: #172b4d;
        font-size: 18px;
        font-weight: 800;
        margin-top: 5px;
    }

    .insight-note {
        color: #667085;
        font-size: 12px;
        margin-top: 3px;
    }

    </style>
    """,
    unsafe_allow_html=True,
)




def format_currency(value):
    """Format large sales values in a compact dashboard-friendly form."""

    value = float(value)

    if abs(value) >= 1_000_000_000:
        return f"${value / 1_000_000_000:.2f}B"

    if abs(value) >= 1_000_000:
        return f"${value / 1_000_000:.2f}M"

    if abs(value) >= 1_000:
        return f"${value / 1_000:.1f}K"

    return f"${value:,.0f}"


def make_chart(fig, height=330):
    """Apply common Plotly styling."""

    fig.update_layout(
        template="plotly_white",
        height=height,
        margin=dict(l=20, r=20, t=55, b=45),

        font=dict(
            family="Arial",
            color="#172b4d",
            size=13,
        ),

        title=dict(
            x=0,
            xanchor="left",
            font=dict(
                size=17,
                color="#172b4d",
            ),
        ),

        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.01,
            xanchor="right",
            x=1,
            font=dict(
                color="#172b4d",
                size=12,
            ),
        ),

        paper_bgcolor="white",
        plot_bgcolor="white",
    )

    fig.update_xaxes(
        showgrid=False,
        showline=True,
        linecolor="#d9e0ec",
        linewidth=1,

        title_font=dict(
            color="#172b4d",
            size=13,
        ),

        tickfont=dict(
            color="#172b4d",
            size=11,
        ),

        automargin=True,
    )

    fig.update_yaxes(
        showgrid=True,
        gridcolor="#edf1f7",
        zeroline=False,
        showline=False,

        title_font=dict(
            color="#172b4d",
            size=13,
        ),

        tickfont=dict(
            color="#172b4d",
            size=11,
        ),

        automargin=True,
    )

    return fig


def ordered_month_values(series):
    """
    Keep calendar month order when the dataset contains
    numeric months or month names.
    """

    values = series.dropna().unique().tolist()

    month_names = [
        "January",
        "February",
        "March",
        "April",
        "May",
        "June",
        "July",
        "August",
        "September",
        "October",
        "November",
        "December",
    ]

    short_month_names = [
        "Jan",
        "Feb",
        "Mar",
        "Apr",
        "May",
        "Jun",
        "Jul",
        "Aug",
        "Sep",
        "Oct",
        "Nov",
        "Dec",
    ]

    if all(isinstance(v, (int, float)) for v in values):
        return sorted(values)

    lookup = {
        name.lower(): index
        for index, name in enumerate(month_names)
    }

    lookup.update(
        {
            name.lower(): index
            for index, name in enumerate(short_month_names)
        }
    )

    return sorted(
        values,
        key=lambda value: lookup.get(str(value).lower(), 99),
    )


def show_table(title, dataframe, rows=10):
    """Display a small sample table."""

    with st.expander(title):
        st.dataframe(
            dataframe.head(rows),
            use_container_width=True,
            hide_index=True,
        )



def get_table_quality(connection):
    """
    Retrieve data-quality information directly from PostgreSQL.

    IMPORTANT:
    The full fact_table is NOT loaded into Pandas.
    """

    tables = {
        "Payment": "trans_dim",
        "Time": "time_dim",
        "Store": "store_dim",
        "Item": "item_dim",
        "Customer": "customer_dim",
        "Fact": "fact_table",
    }

    rows = []

    for display_name, table_name in tables.items():

        query = f"""
            SELECT
                COUNT(*) AS rows,
                COUNT(*) - COUNT(DISTINCT row_hash) AS duplicate_rows,
                SUM(missing_cells) AS missing_cells
            FROM (
                SELECT
                    md5(
                        row_to_json(t)::text
                    ) AS row_hash,

                    (
                        SELECT COUNT(*)
                        FROM jsonb_each_text(
                            to_jsonb(t)
                        )
                        WHERE value IS NULL
                    ) AS missing_cells

                FROM {table_name} t
            ) x
        """

        result = pd.read_sql_query(
            query,
            connection,
        ).iloc[0]

        # Number of columns is obtained separately.
        column_query = """
            SELECT COUNT(*) AS column_count
            FROM information_schema.columns
            WHERE table_schema = 'public'
              AND table_name = %s
        """

        column_result = pd.read_sql_query(
            column_query,
            connection,
            params=[table_name],
        ).iloc[0]

        rows.append(
            {
                "Dataset": display_name,
                "Rows": int(result["rows"]),
                "Columns": int(column_result["column_count"]),
                "Duplicate Rows": int(result["duplicate_rows"]),
                "Missing Cells": int(result["missing_cells"]),
            }
        )

    return pd.DataFrame(rows)


def get_foreign_key_validation(connection):
    """
    Validate foreign keys inside PostgreSQL.

    This avoids loading the 1M-row fact table into Python.
    """

    queries = {
        "Payment": """
            SELECT COUNT(*) AS invalid_keys
            FROM fact_table f
            LEFT JOIN trans_dim d
                ON f.payment_key = d.payment_key
            WHERE d.payment_key IS NULL
        """,

        "Customer": """
            SELECT COUNT(*) AS invalid_keys
            FROM fact_table f
            LEFT JOIN customer_dim d
                ON f.coustomer_key = d.coustomer_key
            WHERE d.coustomer_key IS NULL
        """,

        "Time": """
            SELECT COUNT(*) AS invalid_keys
            FROM fact_table f
            LEFT JOIN time_dim d
                ON f.time_key = d.time_key
            WHERE d.time_key IS NULL
        """,

        "Item": """
            SELECT COUNT(*) AS invalid_keys
            FROM fact_table f
            LEFT JOIN item_dim d
                ON f.item_key = d.item_key
            WHERE d.item_key IS NULL
        """,

        "Store": """
            SELECT COUNT(*) AS invalid_keys
            FROM fact_table f
            LEFT JOIN store_dim d
                ON f.store_key = d.store_key
            WHERE d.store_key IS NULL
        """,
    }

    rows = []

    for name, query in queries.items():

        result = pd.read_sql_query(
            query,
            connection,
        ).iloc[0]

        invalid_count = int(result["invalid_keys"])

        fact_key = {
            "Payment": "payment_key",
            "Customer": "coustomer_key",
            "Time": "time_key",
            "Item": "item_key",
            "Store": "store_key",
        }[name]

        rows.append(
            {
                "Relationship": name,
                "Fact Key": fact_key,
                "Invalid Keys": invalid_count,
                "Status": (
                    "Valid"
                    if invalid_count == 0
                    else "Issues Found"
                ),
            }
        )

    return pd.DataFrame(rows)


def get_dimension_samples(connection):
    """Retrieve only small dimension samples."""

    queries = {
        "Payment Dimension": """
            SELECT *
            FROM trans_dim
            LIMIT 10
        """,

        "Time Dimension": """
            SELECT *
            FROM time_dim
            LIMIT 10
        """,

        "Store Dimension": """
            SELECT *
            FROM store_dim
            LIMIT 10
        """,

        "Item Dimension": """
            SELECT *
            FROM item_dim
            LIMIT 10
        """,

        "Customer Dimension": """
            SELECT *
            FROM customer_dim
            LIMIT 10
        """,

        "Fact Table": """
            SELECT *
            FROM fact_table
            LIMIT 10
        """,
    }

    result = {}

    for name, query in queries.items():
        result[name] = pd.read_sql_query(
            query,
            connection,
        )

    return result



def get_filtered_export(connection, filters):
    """
    Retrieve only the currently filtered transaction set.

    IMPORTANT:
    This function is called only when the user requests an export.
    It does NOT run automatically for every dashboard operation.
    """

    conditions = []
    params = []

    years = filters.get("years")
    quarters = filters.get("quarters")
    months = filters.get("months")
    divisions = filters.get("divisions")
    districts = filters.get("districts")
    payment_types = filters.get("payment_types")
    products = filters.get("products")

    if years:
        conditions.append("t.year = ANY(%s)")
        params.append(years)

    if quarters:
        conditions.append("t.quarter = ANY(%s)")
        params.append(quarters)

    if months:
        conditions.append("t.month = ANY(%s)")
        params.append(months)

    if divisions:
        conditions.append("s.division = ANY(%s)")
        params.append(divisions)

    if districts:
        conditions.append("s.district = ANY(%s)")
        params.append(districts)

    if payment_types:
        conditions.append("p.trans_type = ANY(%s)")
        params.append(payment_types)

    if products:
        conditions.append("i.item_name = ANY(%s)")
        params.append(products)

    where_sql = ""

    if conditions:
        where_sql = " AND " + " AND ".join(conditions)

    query = f"""
        SELECT
            f.payment_key,
            f.coustomer_key,
            f.time_key,
            f.item_key,
            f.store_key,
            f.quantity,
            f.unit,
            f.unit_price,
            f.total_price,

            t.date,
            t.hour,
            t.day,
            t.week,
            t.month,
            t.quarter,
            t.year,

            s.division,
            s.district,
            s.upazila,

            p.trans_type,
            p.bank_name,

            i.item_name,
            i."desc",
            i.man_country,
            i.supplier

        FROM fact_table f

        JOIN time_dim t
            ON f.time_key = t.time_key

        JOIN store_dim s
            ON f.store_key = s.store_key

        JOIN trans_dim p
            ON f.payment_key = p.payment_key

        JOIN item_dim i
            ON f.item_key = i.item_key

        WHERE 1 = 1
        {where_sql}
    """

    return pd.read_sql_query(
        query,
        connection,
        params=params,
    )




connection = create_connection()

if connection is None:
    st.error("Could not connect to PostgreSQL.")
    st.stop()




st.markdown(
    """
    <div class="dashboard-header">
        <div class="dashboard-title">
            Sales Intelligence Dashboard
        </div>

        <div class="dashboard-subtitle">
            Interactive business analytics • Explore sales,
            customers, products, regions and transaction performance
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)



st.sidebar.title("Dashboard Filters")



filter_options = get_filter_options(connection)

years = filter_options["years"]
quarters = filter_options["quarters"]
months = filter_options["months"]
divisions = filter_options["divisions"]
districts = filter_options["districts"]
payment_types = filter_options["payment_types"]
products = filter_options["products"]




filter_keys = [
    "selected_years",
    "selected_quarters",
    "selected_months",
    "selected_divisions",
    "selected_districts",
    "selected_payment_types",
    "selected_products",
]

if st.sidebar.button(
    "↺ Reset All Filters",
    use_container_width=True,
):
    for key in filter_keys:
        st.session_state.pop(key, None)

    st.rerun()




with st.sidebar.expander(
    "Time Filters",
    expanded=True,
):

    selected_years = st.multiselect(
        "Year",
        years,
        default=years,
        key="selected_years",
    )

    selected_quarters = st.multiselect(
        "Quarter",
        quarters,
        default=quarters,
        key="selected_quarters",
    )

    selected_months = st.multiselect(
        "Month",
        months,
        default=months,
        key="selected_months",
    )




with st.sidebar.expander(
    " Geography",
    expanded=False,
):

    selected_divisions = st.multiselect(
        "Division",
        divisions,
        default=divisions,
        key="selected_divisions",
    )

    selected_districts = st.multiselect(
        "District",
        districts,
        default=districts,
        key="selected_districts",
    )




with st.sidebar.expander(
    "Transaction & Product",
    expanded=False,
):

    selected_payment_types = st.multiselect(
        "Payment Type",
        payment_types,
        default=payment_types,
        key="selected_payment_types",
    )

    selected_products = st.multiselect(
        "Product",
        products,
        default=products,
        key="selected_products",
    )


st.sidebar.divider()




filters = {
    "years": selected_years,
    "quarters": selected_quarters,
    "months": selected_months,
    "divisions": selected_divisions,
    "districts": selected_districts,
    "payment_types": selected_payment_types,
    "products": selected_products,
}




if (
    not selected_years
    or not selected_quarters
    or not selected_months
    or not selected_divisions
    or not selected_districts
    or not selected_payment_types
    or not selected_products
):

    st.warning(
        "No transactions match the current filters. "
        "Please select at least one value in every filter."
    )

    connection.close()
    st.stop()




st.markdown(
    '<div class="section-title">Business Overview</div>',
    unsafe_allow_html=True,
)


# PostgreSQL performs all aggregation.
# No 1M-row DataFrame is created.

kpis = get_kpis(
    connection,
    **filters,
)

total_sales = float(
    kpis["total_sales"]
)

total_transactions = int(
    kpis["total_transactions"]
)

total_quantity = int(
    kpis["total_quantity"]
)

total_customers = int(
    kpis["total_customers"]
)


if total_transactions == 0:

    st.warning(
        "No transactions match the current filters. "
        "Please broaden your selection from the sidebar."
    )

    connection.close()
    st.stop()


avg_transaction = (
    total_sales / total_transactions
)



kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)


with kpi1:
    st.metric(
        " Total Sales",
        format_currency(total_sales),
    )


with kpi2:
    st.metric(
        "Transactions",
        f"{total_transactions:,}",
    )


with kpi3:
    st.metric(
        " Quantity Sold",
        f"{total_quantity:,.0f}",
    )


with kpi4:
    st.metric(
        " Unique Customers",
        f"{total_customers:,}",
    )


with kpi5:
    st.metric(
        "Avg. Transaction",
        format_currency(avg_transaction),
    )




top_product, top_product_sales = get_top_product(
    connection,
    **filters,
)

top_division, top_division_sales = get_top_division(
    connection,
    **filters,
)

top_district, top_district_sales = get_top_district(
    connection,
    **filters,
)

leading_payment, payment_share = get_leading_payment(
    connection,
    **filters,
)


ins1, ins2, ins3, ins4 = st.columns(4)




with ins1:

    st.markdown(
        f"""
        <div class="insight-card">
            <div class="insight-label">
                Top Product
            </div>

            <div class="insight-value">
                {top_product}
            </div>

            <div class="insight-note">
                {format_currency(top_product_sales)}
                sales
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )




with ins2:

    st.markdown(
        f"""
        <div class="insight-card">
            <div class="insight-label">
                Leading Division
            </div>

            <div class="insight-value">
                {top_division}
            </div>

            <div class="insight-note">
                {format_currency(top_division_sales)}
                sales
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )




with ins3:

    st.markdown(
        f"""
        <div class="insight-card">
            <div class="insight-label">
                Top District
            </div>

            <div class="insight-value">
                {top_district}
            </div>

            <div class="insight-note">
                {format_currency(top_district_sales)}
                sales
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )




with ins4:

    st.markdown(
        f"""
        <div class="insight-card">
            <div class="insight-label">
                Leading Payment Type
            </div>

            <div class="insight-value">
                {leading_payment}
            </div>

            <div class="insight-note">
                {payment_share:.1f}% of filtered sales
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )




overview_tab, product_tab, geography_tab, data_tab = st.tabs(
    [
        "Sales Overview",
        "Product Analytics",
        " Geography & Transactions",
        " Data Quality",
    ]
)




with overview_tab:

    st.markdown(
        '<div class="section-title">Sales Performance</div>',
        unsafe_allow_html=True,
    )


   

    col1, col2 = st.columns(2)



    with col1:

        year_sales = get_sales_by_year(
            connection,
            **filters,
        )

        year_sales = year_sales.sort_values(
            "year"
        )


        fig_year = px.bar(
            year_sales,
            x="year",
            y="total_price",
            title="Sales by Year",
            labels={
                "year": "Year",
                "total_price": "Sales",
            },
        )


        fig_year.update_traces(
            hovertemplate=(
                "Year: %{x}"
                "<br>Sales: %{y:$,.2f}"
                "<extra></extra>"
            )
        )


        st.plotly_chart(
            make_chart(fig_year),
            use_container_width=True,
            config={
                "displayModeBar": False
            },
        )


   

    with col2:

        monthly_sales = get_monthly_sales(
            connection,
            **filters,
        )


        month_order = ordered_month_values(
            monthly_sales["month"]
        )


        monthly_sales["month"] = pd.Categorical(
            monthly_sales["month"],
            categories=month_order,
            ordered=True,
        )


        monthly_sales = monthly_sales.sort_values(
            "month"
        )


        fig_month = px.line(
            monthly_sales,
            x="month",
            y="total_price",
            markers=True,
            title="Monthly Sales Trend",
            labels={
                "month": "Month",
                "total_price": "Sales",
            },
        )


        fig_month.update_traces(
            hovertemplate=(
                "Month: %{x}"
                "<br>Sales: %{y:$,.2f}"
                "<extra></extra>"
            )
        )


        st.plotly_chart(
            make_chart(fig_month),
            use_container_width=True,
            config={
                "displayModeBar": False
            },
        )


   

    col3, col4 = st.columns(2)


   

    with col3:

        payment_sales = get_payment_sales(
            connection,
            **filters,
        )


        payment_sales = payment_sales.sort_values(
            "total_price",
            ascending=False,
        )


        fig_payment = px.pie(
            payment_sales,
            names="trans_type",
            values="total_price",
            hole=0.55,
            title="Sales Mix by Payment Type",
        )


        fig_payment.update_traces(
            textposition="inside",
            textinfo="percent",
            hovertemplate=(
                "%{label}"
                "<br>Sales: %{value:$,.2f}"
                "<extra></extra>"
            ),
        )


        st.plotly_chart(
            make_chart(fig_payment),
            use_container_width=True,
            config={
                "displayModeBar": False
            },
        )


    

    with col4:

        division_sales = get_division_sales(
            connection,
            **filters,
        )


        division_sales = division_sales.sort_values(
            "total_price",
            ascending=True,
        )


        fig_division = px.bar(
            division_sales,
            x="total_price",
            y="division",
            orientation="h",
            title="Sales by Division",
            labels={
                "division": "Division",
                "total_price": "Sales",
            },
        )


        fig_division.update_traces(
            hovertemplate=(
                "%{y}"
                "<br>Sales: %{x:$,.2f}"
                "<extra></extra>"
            )
        )


        st.plotly_chart(
            make_chart(fig_division),
            use_container_width=True,
            config={
                "displayModeBar": False
            },
        )




with product_tab:

    st.markdown(
        '<div class="section-title">Product Performance</div>',
        unsafe_allow_html=True,
    )


    col1, col2 = st.columns(2)


    

    with col1:

        top_products = get_top_products(
            connection,
            **filters,
        )


        top_products = top_products.sort_values(
            "total_price"
        )


        fig_products = px.bar(
            top_products,
            x="total_price",
            y="item_name",
            orientation="h",
            title="Top 10 Products by Sales",
            labels={
                "item_name": "Product",
                "total_price": "Sales",
            },
        )


        fig_products.update_traces(
            hovertemplate=(
                "%{y}"
                "<br>Sales: %{x:$,.2f}"
                "<extra></extra>"
            )
        )


        st.plotly_chart(
            make_chart(fig_products, 370),
            use_container_width=True,
            config={
                "displayModeBar": False
            },
        )


    

    with col2:

        product_quantity = get_product_quantity(
            connection,
            **filters,
        )


        product_quantity = product_quantity.sort_values(
            "quantity"
        )


        fig_quantity = px.bar(
            product_quantity,
            x="quantity",
            y="item_name",
            orientation="h",
            title="Top 10 Products by Quantity",
            labels={
                "item_name": "Product",
                "quantity": "Quantity",
            },
        )


        fig_quantity.update_traces(
            hovertemplate=(
                "%{y}"
                "<br>Quantity: %{x:,.0f}"
                "<extra></extra>"
            )
        )


        st.plotly_chart(
            make_chart(fig_quantity, 370),
            use_container_width=True,
            config={
                "displayModeBar": False
            },
        )




with geography_tab:

    st.markdown(
        '<div class="section-title">'
        'Geography & Transaction Analysis'
        '</div>',
        unsafe_allow_html=True,
    )


    col1, col2 = st.columns(2)


    

    with col1:

        district_sales = get_district_sales(
            connection,
            **filters,
        )


        district_sales = district_sales.sort_values(
            "total_price"
        )


        fig_district = px.bar(
            district_sales,
            x="total_price",
            y="district",
            orientation="h",
            title="Top 10 Districts by Sales",
            labels={
                "district": "District",
                "total_price": "Sales",
            },
        )


        fig_district.update_traces(
            hovertemplate=(
                "%{y}"
                "<br>Sales: %{x:$,.2f}"
                "<extra></extra>"
            )
        )


        st.plotly_chart(
            make_chart(fig_district, 370),
            use_container_width=True,
            config={
                "displayModeBar": False
            },
        )


    

    with col2:

        district_transactions = get_district_transactions(
            connection,
            **filters,
        )


        district_transactions = (
            district_transactions
            .sort_values("transactions")
        )


        fig_transactions = px.bar(
            district_transactions,
            x="transactions",
            y="district",
            orientation="h",
            title="Top 10 Districts by Transactions",
            labels={
                "district": "District",
                "transactions": "Transactions",
            },
        )


        fig_transactions.update_traces(
            hovertemplate=(
                "%{y}"
                "<br>Transactions: %{x:,}"
                "<extra></extra>"
            )
        )


        st.plotly_chart(
            make_chart(fig_transactions, 370),
            use_container_width=True,
            config={
                "displayModeBar": False
            },
        )




with data_tab:

    st.markdown(
        '<div class="section-title">'
        'Data Quality & Dataset Health'
        '</div>',
        unsafe_allow_html=True,
    )


    

    quality_df = get_table_quality(
        connection
    )


    q1, q2, q3 = st.columns(3)


    with q1:

        st.metric(
            "Dimension / Fact Tables",
            len(quality_df),
        )


    with q2:

        st.metric(
            "Duplicate Rows",
            f"{quality_df['Duplicate Rows'].sum():,}",
        )


    with q3:

        st.metric(
            "Missing Cells",
            f"{quality_df['Missing Cells'].sum():,}",
        )


    st.dataframe(
        quality_df,
        use_container_width=True,
        hide_index=True,
    )


    

    st.markdown(
        '<div class="section-title">'
        'Foreign Key Validation'
        '</div>',
        unsafe_allow_html=True,
    )


    fk_df = get_foreign_key_validation(
        connection
    )


    st.dataframe(
        fk_df,
        use_container_width=True,
        hide_index=True,
    )


    for _, row in fk_df.iterrows():

        if row["Invalid Keys"] == 0:

            st.success(
                f"✓ {row['Relationship']}: "
                "all fact-table keys are valid"
            )

        else:

            st.error(
                f"✕ {row['Relationship']}: "
                f"{row['Invalid Keys']:,} "
                "invalid keys found"
            )


   

    st.markdown(
        '<div class="section-title">'
        'Dimension Samples'
        '</div>',
        unsafe_allow_html=True,
    )


    samples = get_dimension_samples(
        connection
    )


    show_table(
        "Payment Dimension",
        samples["Payment Dimension"],
    )

    show_table(
        "Time Dimension",
        samples["Time Dimension"],
    )

    show_table(
        "Store Dimension",
        samples["Store Dimension"],
    )

    show_table(
        "Item Dimension",
        samples["Item Dimension"],
    )

    show_table(
        "Customer Dimension",
        samples["Customer Dimension"],
    )

    show_table(
        "Fact Table",
        samples["Fact Table"],
    )




st.divider()


st.markdown(
    '<div class="section-title">Filtered Data</div>',
    unsafe_allow_html=True,
)


st.caption(
    "The filtered transaction data is queried from PostgreSQL "
    "only when you request the export."
)




if st.button(
    "Prepare Filtered CSV",
    use_container_width=False,
):

    with st.spinner(
        "Retrieving filtered transactions from PostgreSQL..."
    ):

        export_df = get_filtered_export(
            connection,
            filters,
        )


    if export_df.empty:

        st.warning(
            "No transactions match the current filters."
        )

    else:

        st.success(
            f"{len(export_df):,} filtered transactions retrieved."
        )


        csv_data = export_df.to_csv(
            index=False
        ).encode("utf-8")


        st.download_button(
            label="⬇️ Download Filtered CSV",
            data=csv_data,
            file_name="filtered_sales_data.csv",
            mime="text/csv",
        )




connection.close()