import sys
from pathlib import Path

import streamlit as st


PROJECT_ROOT = Path(__file__).resolve().parents[1]

sys.path.insert(
    0,
    str(PROJECT_ROOT / "src")
)

sys.path.insert(
    0,
    str(PROJECT_ROOT)
)


from database import create_connection

from data_retrieval import (
    get_filter_options,
    get_kpis,
    get_monthly_bookings,
    get_hotel_analysis,
    get_top_countries,
    get_customer_type_analysis,
    get_repeated_guest_analysis,
    get_market_segment_analysis,
    get_room_type_analysis
)

from visualization import (
    monthly_booking_chart,
    hotel_booking_chart,
    hotel_cancellation_chart,
    top_country_chart,
    customer_type_chart,
    market_segment_chart,
    room_type_chart,
    repeated_guest_chart
)


st.set_page_config(
    page_title="Hotel Booking Analytics",
    page_icon="",
    layout="wide"
)


@st.cache_resource
def get_connection():

    return create_connection()


connection = get_connection()


@st.cache_data
def load_filter_options():

    return get_filter_options(connection)


filters = load_filter_options()


st.sidebar.title("Hotel Analytics")

st.sidebar.write(
    "Use the filters below to explore the booking data."
)

st.sidebar.divider()


selected_hotel = st.sidebar.selectbox(
    "Select Hotel",
    ["All Hotels"] + filters["hotels"]
)


selected_year = st.sidebar.selectbox(
    "Select Arrival Year",
    ["All Years"] + filters["years"]
)


selected_month = st.sidebar.selectbox(
    "Select Arrival Month",
    ["All Months"] + filters["months"]
)


selected_customer = st.sidebar.selectbox(
    "Select Customer Type",
    ["All Customer Types"] + filters["customer_types"]
)


selected_segment = st.sidebar.selectbox(
    "Select Market Segment",
    ["All Market Segments"] + filters["market_segments"]
)


selected_status = st.sidebar.selectbox(
    "Select Booking Status",
    ["All Booking Status"] + filters["booking_status"]
)


@st.cache_data
def load_kpis(
    hotel,
    year,
    month,
    customer_type,
    market_segment,
    booking_status
):

    return get_kpis(
        connection,
        hotel,
        year,
        month,
        customer_type,
        market_segment,
        booking_status
    )


kpis = load_kpis(
    selected_hotel,
    selected_year,
    selected_month,
    selected_customer,
    selected_segment,
    selected_status
)


st.title(
    "Hotel Booking Analytics Dashboard"
)

st.write(
    "Analyze hotel performance, customer behavior and booking trends."
)


col1, col2, col3, col4, col5 = st.columns(5)


with col1:

    st.metric(
        "Total Bookings",
        f"{kpis['total_bookings']:,.0f}"
    )


with col2:

    st.metric(
        "Total Guests",
        f"{kpis['total_guests']:,.0f}"
    )


with col3:

    st.metric(
        "Estimated Revenue",
        f"${kpis['total_revenue']:,.0f}"
    )


with col4:

    st.metric(
        "Average ADR",
        f"${kpis['average_adr']:.2f}"
    )


with col5:

    st.metric(
        "Cancellation Rate",
        f"{kpis['cancellation_rate']:.1f}%"
    )


st.divider()


overview_tab, hotel_tab, customer_tab, booking_tab = st.tabs(
    [
        "Overview",
        "Hotels",
        "Customers",
        "Bookings"
    ]
)


def get_filter_arguments():

    return {
        "hotel": selected_hotel,
        "year": selected_year,
        "month": selected_month,
        "customer_type": selected_customer,
        "market_segment": selected_segment,
        "booking_status": selected_status
    }


filter_args = get_filter_arguments()


with overview_tab:

    st.header("Overall Performance")


    monthly_data = get_monthly_bookings(
        connection,
        **filter_args
    )


    hotel_data = get_hotel_analysis(
        connection,
        **filter_args
    )


    if monthly_data.empty and hotel_data.empty:

        st.warning(
            "No bookings found for the selected filters."
        )

    else:

        col1, col2 = st.columns(2)


        with col1:

            if not monthly_data.empty:

                fig = monthly_booking_chart(
                    monthly_data
                )

                st.pyplot(
                    fig,
                    use_container_width=True
                )


        with col2:

            if not hotel_data.empty:

                fig = hotel_booking_chart(
                    hotel_data
                )

                st.pyplot(
                    fig,
                    use_container_width=True
                )


        st.subheader("Hotel Summary")

        st.dataframe(
            hotel_data.round(2),
            use_container_width=True,
            hide_index=True
        )


with hotel_tab:

    st.header("Hotel Performance")


    hotel_data = get_hotel_analysis(
        connection,
        **filter_args
    )


    if not hotel_data.empty:

        col1, col2 = st.columns(2)


        with col1:

            fig = hotel_booking_chart(
                hotel_data
            )

            st.pyplot(
                fig,
                use_container_width=True
            )


        with col2:

            fig = hotel_cancellation_chart(
                hotel_data
            )

            st.pyplot(
                fig,
                use_container_width=True
            )


        st.subheader(
            "Hotel Performance Data"
        )


        st.dataframe(
            hotel_data.round(2),
            use_container_width=True,
            hide_index=True
        )

    else:

        st.warning(
            "No hotel data found."
        )


with customer_tab:

    st.header("Customer Analysis")


    customer_data = get_customer_type_analysis(
        connection,
        **filter_args
    )


    country_data = get_top_countries(
        connection,
        **filter_args
    )


    repeated_data = get_repeated_guest_analysis(
        connection,
        **filter_args
    )


    col1, col2 = st.columns(2)


    with col1:

        if not customer_data.empty:

            fig = customer_type_chart(
                customer_data
            )

            st.pyplot(
                fig,
                use_container_width=True
            )


    with col2:

        if not repeated_data.empty:

            fig = repeated_guest_chart(
                repeated_data
            )

            st.pyplot(
                fig,
                use_container_width=True
            )


    st.subheader(
        "Top 10 Countries"
    )


    if not country_data.empty:

        fig = top_country_chart(
            country_data
        )

        st.pyplot(
            fig,
            use_container_width=True
        )


    st.subheader(
        "Customer Type Data"
    )


    st.dataframe(
        customer_data.round(2),
        use_container_width=True,
        hide_index=True
    )


    st.subheader(
        "Country Data"
    )


    st.dataframe(
        country_data.head(20),
        use_container_width=True,
        hide_index=True
    )


with booking_tab:

    st.header("Booking Analysis")


    segment_data = get_market_segment_analysis(
        connection,
        **filter_args
    )


    room_data = get_room_type_analysis(
        connection,
        **filter_args
    )


    col1, col2 = st.columns(2)


    with col1:

        if not segment_data.empty:

            fig = market_segment_chart(
                segment_data
            )

            st.pyplot(
                fig,
                use_container_width=True
            )


    with col2:

        if not room_data.empty:

            fig = room_type_chart(
                room_data
            )

            st.pyplot(
                fig,
                use_container_width=True
            )


    st.subheader(
        "Market Segment Data"
    )


    st.dataframe(
        segment_data.round(2),
        use_container_width=True,
        hide_index=True
    )


    st.subheader(
        "Room Type Data"
    )


    st.dataframe(
        room_data.round(2),
        use_container_width=True,
        hide_index=True
    )


st.sidebar.divider()


st.sidebar.write(
    "Data source: PostgreSQL"
)

st.sidebar.write(
    "Hotel Booking Analytics"
)