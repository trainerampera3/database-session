import streamlit as st
import pandas as pd
import psycopg as pg
import plotly.express as px






st.set_page_config(
    page_title="Gym Analytics Dashboard",
    layout="wide"
)



conn = pg.connect(
    user = 'jayanth',
    dbname='dashboard',
    password='admin@123',
    port=5433,
    host='localhost'
)



def load_data():

    query = """
        SELECT
            c.cust_id,
            c.fullname,
            c.age,
            c.gender,
            c.joindate,
            c.expirydate,
            c.renewal_status,

            b.branch_name,

            g.goal_name,

            t.trainer_name,

            p.plan_type,

            d.diet_name

        FROM customer c

        LEFT JOIN branch b
            ON c.branch_id = b.branch_id

        LEFT JOIN goals g
            ON c.goal_id = g.goal_id

        LEFT JOIN trainers t
            ON c.trainer_id = t.trainer_id

        LEFT JOIN plans p
            ON c.plan_id = p.plan_id

        LEFT JOIN dietplan d
            ON c.diet_id = d.diet_id
    """

    return pd.read_sql(query, conn)


df = load_data()


st.sidebar.divider()

st.sidebar.subheader("Filters")


branches = sorted(
    df["branch_name"].dropna().unique().tolist()
)

branch = st.sidebar.selectbox(
    "Branch",
    ["All"] + branches
)

genders = sorted(
    df["gender"].dropna().unique().tolist()
)

gender = st.sidebar.selectbox(
    "Gender",
    ["All"] + genders
)


plans = sorted(
    df["plan_type"].dropna().unique().tolist()
)

plan = st.sidebar.selectbox(
    "Membership Plan",
    ["All"] + plans
)



goals = sorted(
    df["goal_name"].dropna().unique().tolist()
)

goal = st.sidebar.selectbox(
    "Fitness Goal",
    ["All"] + goals
)



diets = sorted(
    df["diet_name"].dropna().unique().tolist()
)

diet = st.sidebar.selectbox(
    "Diet Plan",
    ["All"] + diets
)



filtered_df = df.copy()


if branch != "All":

    filtered_df = filtered_df[filtered_df["branch_name"] == branch]


if gender != "All":

    filtered_df = filtered_df[filtered_df["gender"] == gender]


if plan != "All":

    filtered_df = filtered_df[filtered_df["plan_type"] == plan]


if goal != "All":

    filtered_df = filtered_df[filtered_df["goal_name"] == goal]


if diet != "All":

    filtered_df = filtered_df[filtered_df["diet_name"] == diet]




st.header("Customer Analytics Dashboard")

st.caption("Gym membership and customer analytics")

st.divider()



active_filters = []

if branch != "All":
    active_filters.append(f"Branch: {branch}")

if gender != "All":
    active_filters.append(f"Gender: {gender}")

if plan != "All":
    active_filters.append(f"Plan: {plan}")

if goal != "All":
    active_filters.append(f"Goal: {goal}")

if diet != "All":
    active_filters.append(f"Diet: {diet}")


if active_filters:

    st.info(
        " | ".join(active_filters)
    )



col1, col2, col3, col4 = st.columns(4)


with col1:

    st.metric(
        "Total Members",
        f"{len(filtered_df):,}"
    )


with col2:

    active_members = filtered_df[
        "renewal_status"
    ].astype(str).str.lower().eq("active").sum()

    st.metric(
        "Active Members",
        f"{active_members:,}"
    )


with col3:

    avg_age = filtered_df["age"].mean()

    st.metric(
        "Average Age",
        f"{avg_age:.1f}"
        if pd.notna(avg_age)
        else "0"
    )


with col4:

    renewal_rate = (
        active_members / len(filtered_df) * 100
        if len(filtered_df) > 0
        else 0
    )

    st.metric(
        "Active Rate",
        f"{renewal_rate:.1f}%"
    )


st.divider()



if filtered_df.empty:

    st.warning("No customers match the selected filters.")
    st.stop()



col1, col2 = st.columns(2)


with col1:

    st.subheader("Gender Distribution")

    gender_df = (filtered_df.groupby("gender").size().reset_index(name="member_count"))

    fig = px.pie(
        gender_df,
        names="gender",
        values="member_count",
        hole=0.4,
        title="Members by Gender"
    )

    fig.update_traces(textinfo="percent+label")

    st.plotly_chart(fig,use_container_width=True)




with col2:

    st.subheader("Members by Age Group")

    filtered_df["AgeGroup"] = pd.cut(
        filtered_df["age"],
        bins=[17, 25, 35, 45, 55, 100],
        labels=[
            "18-25",
            "26-35",
            "36-45",
            "46-55",
            "56+"
        ]
    )

    age_df = (
        filtered_df.groupby("AgeGroup",observed=True).size().reset_index(name="member_count"))

    fig = px.bar(
        age_df,
        x="AgeGroup",
        y="member_count",
        text="member_count",
        title="Members by Age Group"
    )

    fig.update_traces(
        textposition="outside"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )


st.divider()


col1, col2 = st.columns(2)



with col1:

    st.subheader("Fitness Goal Distribution")

    goal_df = (
        filtered_df.groupby("goal_name").size().reset_index(name="member_count").sort_values("member_count",ascending=False)
    )

    fig = px.bar(
        goal_df,
        x="goal_name",
        y="member_count",
        text="member_count",
        title="Members by Fitness Goal"
    )

    fig.update_traces(
        textposition="outside"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )



with col2:

    st.subheader("Membership Plan Distribution")

    plan_df = (
        filtered_df.groupby("plan_type").size().reset_index(name="member_count"))

    fig = px.pie(
        plan_df,
        names="plan_type",
        values="member_count",
        hole=0.4,
        title="Members by Plan"
    )

    fig.update_traces(
        textinfo="percent+label"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )


st.divider()



col1, col2 = st.columns(2)




with col1:

    st.subheader("Diet Plan Distribution")

    diet_df = (
        filtered_df.groupby("diet_name").size().reset_index(name="member_count"))

    fig = px.bar(
        diet_df,
        x="diet_name",
        y="member_count",
        text="member_count",
        title="Members by Diet Plan"
    )

    fig.update_traces(
        textposition="outside"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )



with col2:

    st.subheader("Trainer Distribution")

    trainer_df = (
        filtered_df.groupby("trainer_name").size().reset_index(name="member_count").sort_values("member_count",ascending=False)
    )

    fig = px.bar(
        trainer_df,
        x="trainer_name",
        y="member_count",
        text="member_count",
        title="Members Assigned to Trainers"
    )

    fig.update_traces(
        textposition="outside"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )


st.divider()




st.subheader("Branch Performance")

branch_df = (
    filtered_df.groupby("branch_name").size().reset_index(name="member_count").sort_values("member_count",ascending=False)
)

fig = px.bar(
    branch_df,
    x="branch_name",
    y="member_count",
    text="member_count",
    title="Members by Branch"
)

fig.update_traces(
    textposition="outside"
)

st.plotly_chart(
    fig,
    use_container_width=True
)



with st.expander("View Customer Data"):

    st.dataframe(
        filtered_df,
        use_container_width=True,
        hide_index=True
    )