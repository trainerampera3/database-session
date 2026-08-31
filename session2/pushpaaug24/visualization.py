import matplotlib.pyplot as plt



def monthly_booking_chart(data):

    fig, ax = plt.subplots(figsize=(10, 5))

    ax.plot(
        data["month_year"],
        data["bookings"],
        marker="o"
    )

    ax.set_title(
        "Monthly Booking Trend"
    )

    ax.set_xlabel(
        "Month"
    )

    ax.set_ylabel(
        "Number of Bookings"
    )

    ax.tick_params(
        axis="x",
        rotation=45
    )

    fig.tight_layout()

    return fig



def hotel_booking_chart(data):

    fig, ax = plt.subplots(figsize=(8, 5))

    ax.bar(
        data["hotel"],
        data["bookings"]
    )

    ax.set_title(
        "Bookings by Hotel"
    )

    ax.set_xlabel(
        "Hotel"
    )

    ax.set_ylabel(
        "Bookings"
    )

    fig.tight_layout()

    return fig



def hotel_cancellation_chart(data):

    fig, ax = plt.subplots(figsize=(8, 5))

    ax.bar(
        data["hotel"],
        data["cancellation_rate"]
    )

    ax.set_title(
        "Cancellation Rate by Hotel"
    )

    ax.set_xlabel(
        "Hotel"
    )

    ax.set_ylabel(
        "Cancellation Rate (%)"
    )

    fig.tight_layout()

    return fig




def top_country_chart(data):

    data = (
        data
        .sort_values(
            "bookings",
            ascending=False
        )
        .head(10)
        .sort_values(
            "bookings"
        )
    )

    fig, ax = plt.subplots(figsize=(9, 6))

    ax.barh(
        data["country"],
        data["bookings"]
    )

    ax.set_title(
        "Top 10 Countries by Bookings"
    )

    ax.set_xlabel(
        "Bookings"
    )

    ax.set_ylabel(
        "Country"
    )

    fig.tight_layout()

    return fig




def customer_type_chart(data):

    fig, ax = plt.subplots(figsize=(8, 5))

    ax.bar(
        data["customer_type"],
        data["bookings"]
    )

    ax.set_title(
        "Bookings by Customer Type"
    )

    ax.set_xlabel(
        "Customer Type"
    )

    ax.set_ylabel(
        "Bookings"
    )

    ax.tick_params(
        axis="x",
        rotation=30
    )

    fig.tight_layout()

    return fig




def market_segment_chart(data):

    data = data.sort_values(
        "bookings"
    )

    fig, ax = plt.subplots(figsize=(9, 6))

    ax.barh(
        data["market_segment"],
        data["bookings"]
    )

    ax.set_title(
        "Bookings by Market Segment"
    )

    ax.set_xlabel(
        "Bookings"
    )

    ax.set_ylabel(
        "Market Segment"
    )

    fig.tight_layout()

    return fig



def room_type_chart(data):

    fig, ax = plt.subplots(figsize=(8, 5))

    ax.bar(
        data["reserved_room_type"],
        data["bookings"]
    )

    ax.set_title(
        "Bookings by Room Type"
    )

    ax.set_xlabel(
        "Reserved Room Type"
    )

    ax.set_ylabel(
        "Bookings"
    )

    fig.tight_layout()

    return fig





def repeated_guest_chart(data):

    fig, ax = plt.subplots(figsize=(7, 6))

    ax.pie(
        data["bookings"],
        labels=data["guest_category"],
        autopct="%1.1f%%"
    )

    ax.set_title(
        "New Guests vs Repeated Guests"
    )

    return fig




# def lead_time_chart(df):

#     fig, ax = plt.subplots(figsize=(9, 5))

#     ax.hist(
#         df["lead_time"],
#         bins=30
#     )

#     ax.set_title(
#         "Booking Lead Time Distribution"
#     )

#     ax.set_xlabel(
#         "Lead Time (Days)"
#     )

#     ax.set_ylabel(
#         "Number of Bookings"
#     )

#     fig.tight_layout()

#     return fig