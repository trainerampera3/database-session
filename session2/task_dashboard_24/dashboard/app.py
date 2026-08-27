import streamlit as st
import plotly.express as px
from db_queries import (

    get_overview_filters,
    get_jobs_by_category,
    get_jobs_by_experience,
    get_remote_work,
    get_jobs_by_industry,
    get_jobs_by_country,
    get_posting_trend,

    get_salary_filters,
    get_average_salary_by_experience,
    get_top_salary_roles,
    get_average_salary_by_category,
    get_salary_vs_experience,
    get_salary_by_industry,
    get_ai_salary_premium_by_category,

    get_demand_filters,
    get_demand_by_role,
    get_llm_roles,
    get_demand_growth_by_category,
    get_senior_vs_non_senior,
    get_remote_friendly_vs_non_remote,
)


st.set_page_config(
    page_title="AI Jobs Market Dashboard",
    layout="wide"
)

st.title("AI Jobs Market Dashboard")

# st.caption(
#     "PostgreSQL + psycopg + Streamlit + Plotly"
# )

st.sidebar.title("Job Management")

page = st.sidebar.radio(
    "Select Dashboard",
    [
        "Market Overview",
        "Salary",
        "Demand & Technology"
    ]
)



if page == "Market Overview":

    st.header(" Market Overview")

    st.write(
        "Analyze jobs by category, experience, industry, "
        "country, remote work and posting year."
    )

    st.sidebar.subheader("Filters")

    filter_data = get_overview_filters()

    categories = sorted({
        row["job_category"]
        for row in filter_data
        if row["job_category"] is not None
    })

    experiences = sorted({
        row["experience_level"]
        for row in filter_data
        if row["experience_level"] is not None
    })

    industries = sorted({
        row["industry"]
        for row in filter_data
        if row["industry"] is not None
    })

    countries = sorted({
        row["country"]
        for row in filter_data
        if row["country"] is not None
    })

    remote_types = sorted({
        row["remote_work"]
        for row in filter_data
        if row["remote_work"] is not None
    })

    years = sorted({
        row["posting_year"]
        for row in filter_data
        if row["posting_year"] is not None
    })

    selected_category = st.sidebar.multiselect(
        "Job Category",
        categories
    )

    selected_experience = st.sidebar.multiselect(
        "Experience Level",
        experiences
    )

    selected_industry = st.sidebar.multiselect(
        "Industry",
        industries
    )

    selected_country = st.sidebar.multiselect(
        "Country",
        countries
    )

    selected_remote = st.sidebar.multiselect(
        "Remote Work",
        remote_types
    )

    selected_year = st.sidebar.multiselect(
        "Posting Year",
        years
    )

    filters = {

        "category":
            selected_category
            if selected_category
            else None,

        "experience":
            selected_experience
            if selected_experience
            else None,

        "industry":
            selected_industry
            if selected_industry
            else None,

        "country":
            selected_country
            if selected_country
            else None,

        "remote":
            selected_remote
            if selected_remote
            else None,

        "year":
            selected_year
            if selected_year
            else None,
    }

    st.subheader("Jobs by Category")

    data = get_jobs_by_category(filters)

    if data:

        fig = px.bar(
            data,
            x="job_category",
            y="number_of_jobs",
            title="Jobs by Job Category",
            labels={
                "job_category": "Job Category",
                "number_of_jobs": "Number of Jobs"
            }
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    st.subheader("Jobs by Experience")

    data = get_jobs_by_experience(filters)

    if data:

        fig = px.bar(
            data,
            x="experience_level",
            y="number_of_jobs",
            title="Jobs by Experience Level",
            labels={
                "experience_level": "Experience Level",
                "number_of_jobs": "Number of Jobs"
            }
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    st.subheader(" Remote Work")

    data = get_remote_work(filters)

    if data:

        fig = px.bar(
            data,
            x="remote_work",
            y="number_of_jobs",
            title="Remote Work Distribution",
            labels={
                "remote_work": "Remote Work",
                "number_of_jobs": "Number of Jobs"
            }
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )


    st.subheader("Jobs by Industry")

    data = get_jobs_by_industry(filters)

    if data:

        fig = px.bar(
            data,
            x="industry",
            y="number_of_jobs",
            title="Top 15 Industries",
            labels={
                "industry": "Industry",
                "number_of_jobs": "Number of Jobs"
            }
        )

        fig.update_layout(
            xaxis_tickangle=-45
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )


    st.subheader("Jobs by Country")

    data = get_jobs_by_country(filters)

    if data:

        fig = px.bar(
            data,
            x="country",
            y="number_of_jobs",
            title="Top 15 Countries",
            labels={
                "country": "Country",
                "number_of_jobs": "Number of Jobs"
            }
        )

        fig.update_layout(
            xaxis_tickangle=-45
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )


    st.subheader("Posting Trend")

    data = get_posting_trend(filters)

    if data:

        fig = px.line(
            data,
            x="posting_year",
            y="number_of_jobs",
            markers=True,
            title="Job Posting Trend",
            labels={
                "posting_year": "Posting Year",
                "number_of_jobs": "Number of Jobs"
            }
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )




elif page == "Salary":

    st.header("Salary Analysis")

    st.write(
        "Analyze salary based on experience, job categories, "
        "company size,job titles and industry."
    )

    st.sidebar.subheader("Salary Filters")

    filter_data = get_salary_filters()


    experiences = sorted({
        row["experience_level"]
        for row in filter_data
        if row["experience_level"] is not None
    })

    company_sizes = sorted({
        row["company_size"]
        for row in filter_data
        if row["company_size"] is not None
    })

    industries = sorted({
        row["industry"]
        for row in filter_data
        if row["industry"] is not None
    })

    categories = sorted({
        row["job_category"]
        for row in filter_data
        if row["job_category"] is not None
    })
     
    job_titles = sorted({
        row["job_title"]
        for row in filter_data
        if row["job_title"] is not None
    })

    years_of_experience = [
        row["years_of_experience"]
        for row in filter_data
        if row["years_of_experience"] is not None
    ]

    salaries = [
        row["annual_salary_usd"]
        for row in filter_data
        if row["annual_salary_usd"] is not None
    ]
    


    selected_experience = st.sidebar.multiselect(
        "Experience Level",
        experiences
    )

    selected_company = st.sidebar.multiselect(
        "Company Size",
        company_sizes
    )

    selected_industry = st.sidebar.multiselect(
        "Industry",
        industries
    )

    selected_category = st.sidebar.multiselect(
        "Job Category",
        categories
    )

    selected_job_title = st.sidebar.multiselect(
        "Job Title",
        job_titles
    )



    experience_min = int(min(years_of_experience))
    experience_max = int(max(years_of_experience))

    selected_years = st.sidebar.slider(
        "Years of Experience",
        experience_min,
        experience_max,
        (
            experience_min,
            experience_max
        )
    )


    salary_min = float(min(salaries))
    salary_max = float(max(salaries))

    selected_salary = st.sidebar.slider(
        "Annual Salary (USD)",
        salary_min,
        salary_max,
        (
            salary_min,
            salary_max
        )
    )


    salary_filters = {

        "experience":
            selected_experience
            if selected_experience
            else None,

        "company":
            selected_company
            if selected_company
            else None,

        "industry":
            selected_industry
            if selected_industry
            else None,

        "category": 
            selected_category 
            if selected_category 
            else None,

        "job_title": 
            selected_job_title 
            if selected_job_title 
            else None,

        "years_min":
            selected_years[0],

        "years_max":
            selected_years[1],

        "salary_min":
            selected_salary[0],

        "salary_max":
            selected_salary[1],
    }


    st.subheader(
        "Average Salary by Experience Level"
    )

    data = get_average_salary_by_experience(
        salary_filters
    )

    if data:

        fig = px.bar(
            data,
            x="experience_level",
            y="average_salary",
            title="Average Salary by Experience Level",
            labels={
                "experience_level": "Experience Level",
                "average_salary": "Average Salary (USD)"
            }
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )



    st.subheader(
        "Top Salary Roles"
    )

    data = get_top_salary_roles(
        salary_filters
    )

    if data:

        fig = px.bar(
            data,
            x="job_title",
            y="average_salary",
            title="Top 15 Highest Paying Job Roles",
            labels={
                "job_title": "Job Title",
                "average_salary": "Average Salary (USD)"
            }
        )

        fig.update_layout(
            xaxis_tickangle=-45
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )


    st.subheader(
        "Average Salary by Job Category"
    )

    data = get_average_salary_by_category(
    salary_filters
    )

    if data:

        fig = px.bar(
            data,
            x="job_category",
            y="average_salary",
            title="Average Salary by Job Category",
            labels={
                "job_category": "Job Category",
                "average_salary": "Average Salary (USD)"
            }
        )

        fig.update_layout(
            xaxis_tickangle=-45
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )


    st.subheader(
        "Salary vs Years of Experience"
    )

    data = get_salary_vs_experience(
        salary_filters
    )

    if data:

        fig = px.scatter(
            data,
            x="years_of_experience",
            y="annual_salary_usd",
            title="Salary vs Years of Experience",
            labels={
                "years_of_experience": "Years of Experience",
                "annual_salary_usd": "Annual Salary (USD)"
            },
            opacity=0.7
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )


    st.subheader(
        "Salary by Industry"
    )

    data = get_salary_by_industry(
        salary_filters
    )

    if data:

        fig = px.bar(
            data,
            x="industry",
            y="average_salary",
            title="Top 15 Industries by Average Salary",
            labels={
                "industry": "Industry",
                "average_salary": "Average Salary (USD)"
            }
        )

        fig.update_layout(
            xaxis_tickangle=-45
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )



    st.subheader(
        "AI Salary Premium by Job Category"
    )

    data = get_ai_salary_premium_by_category(
        salary_filters
    )

    if data:

        fig = px.bar(
            data,
            x="job_category",
            y="average_ai_premium",
            title="AI Salary Premium by Job Category",
            labels={
                "job_category": "Job Category",
                "average_ai_premium": "AI Salary Premium (%)"
            }
        )

        fig.update_layout(
            xaxis_tickangle=-45
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )




elif page == "Demand & Technology":

    st.header("Demand & Technology")

    st.write(
        "Analyze job demand, LLM roles, senior roles "
        "and remote-friendly opportunities."
    )

    st.sidebar.subheader(
        "Demand & Technology Filters"
    )

    filter_data = get_demand_filters()


    job_titles = sorted({
        row["job_title"]
        for row in filter_data
        if row["job_title"] is not None
    })

    experiences = sorted({
        row["experience_level"]
        for row in filter_data
        if row["experience_level"] is not None
    })

    industries = sorted({
        row["industry"]
        for row in filter_data
        if row["industry"] is not None
    })
    categories = sorted({
        row["job_category"]
        for row in filter_data
        if row["job_category"] is not None
    })


    selected_job_title = st.sidebar.multiselect(
        "Job Title",
        job_titles
    )

    selected_experience = st.sidebar.multiselect(
        "Experience Level",
        experiences
    )

    selected_industry = st.sidebar.multiselect(
        "Industry",
        industries
    )
    selected_category = st.sidebar.multiselect(
        "Job Category",
        categories,
   
    )
    senior_only = st.sidebar.checkbox(
        "Senior Roles Only"
    )

    remote_only = st.sidebar.checkbox(
        "Remote Friendly Only"
    )

    llm_only = st.sidebar.checkbox(
        "LLM Roles Only"
    )


    demand_filters = {

        "job_title":
            selected_job_title
            if selected_job_title
            else None,

        "experience":
            selected_experience
            if selected_experience
            else None,

        "industry":
            selected_industry
            if selected_industry
            else None,
        "category": 
            selected_category 
            if selected_category 
            else None,

        "senior":
            senior_only,

        "remote":
            remote_only,

        "llm":
            llm_only,
    }


    st.subheader(
        "Average Demand Score by Job Title"
    )

    data = get_demand_by_role(
        demand_filters
    )

    if data:

        fig = px.bar(
            data,
            x="job_title",
            y="average_demand_score",
            title="Top 15 Job Roles by Demand",
            labels={
                "job_title": "Job Title",
                "average_demand_score": "Average Demand Score"
            }
        )

        fig.update_layout(
            xaxis_tickangle=-45
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )


    st.subheader(
        "LLM vs Non-LLM Jobs"
    )

    data = get_llm_roles(
        demand_filters
    )

    if data:

        fig = px.bar(
            data,
            x="role_type",
            y="number_of_jobs",
            title="LLM vs Non-LLM Jobs",
            labels={
                "role_type": "Role Type",
                "number_of_jobs": "Number of Jobs"
            }
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )


    st.subheader(
        "Demand Growth by Job Category"
    )

    data = get_demand_growth_by_category(
        demand_filters
    )

    if data:

        fig = px.bar(
            data,
            x="job_category",
            y="average_demand_growth",
            title="Demand Growth by Job Category",
            labels={
                "job_category": "Job Category",
                "average_demand_growth": "Demand Growth (%)"
            }
        )

        fig.update_layout(
            xaxis_tickangle=-45
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    st.subheader(
        "Senior vs Non-Senior Jobs"
    )

    data = get_senior_vs_non_senior(
        demand_filters
    )

    if data:

        fig = px.bar(
            data,
            x="role_type",
            y="number_of_jobs",
            title="Senior vs Non-Senior Jobs",
            labels={
                "role_type": "Role Type",
                "number_of_jobs": "Number of Jobs"
            }
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )



    st.subheader(
        "Remote-Friendly vs Non-Remote-Friendly Jobs"
    )

    data = get_remote_friendly_vs_non_remote(
        demand_filters
    )

    if data:

        fig = px.bar(
            data,
            x="remote_status",
            y="number_of_jobs",
            title="Remote-Friendly vs Non-Remote-Friendly Jobs",
            labels={
                "remote_status": "Remote Status",
                "number_of_jobs": "Number of Jobs"
            }
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )