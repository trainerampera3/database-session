import streamlit as st
import plotly.express as px
import logging
import filters.filter as ft

logging.basicConfig(level=logging.INFO)


def show_hospital_dashboard():

    database = ft.Filter()

    st.title("Hospital Management Dashboard")

    database.filter()

    logging.info("Done with filtering!")

 

    logging.info("Metrics section is started")

    col1, col2, col3 = st.columns(3)

    with col1:
        patient_count = database.get_patient_count()
        st.metric("Patient Count", patient_count)

    with col2:
        billing_amount = database.get_total_billing_amount()
        st.metric("Billing Amount", billing_amount)

    with col3:
        discharge = database.get_avg_discharge_rate()
        st.metric("Avg Days to Discharge", discharge)

    logging.info("Done with the metrics")

  

    logging.info("Started gender pie chart!")

    labels, values = database.get_gender_count()

    gender_df = {
        "Gender": labels,
        "Count": values
    }

    fig = px.pie(
        gender_df,
        names="Gender",
        values="Count",
        title="Gender Distribution"
    )

    st.plotly_chart(fig, use_container_width=True)

    

    logging.info("Started admissions by time")

    labels, values = database.get_admissions_by_time()

    admissions_df = {
        "Year": labels,
        "Admissions": values
    }

    fig = px.line(
        admissions_df,
        x="Year",
        y="Admissions",
        title="Admissions by Year",
        markers=True
    )

    fig.update_layout(
        xaxis_title="Year",
        yaxis_title="Admissions"
    )

    st.plotly_chart(fig, use_container_width=True)

    logging.info("Done with admissions")

    

    logging.info("Started plotting medical conditions")

    labels, values = database.get_disease_frequency()

    disease_df = {
        "Medical Condition": labels,
        "Frequency": values
    }

    fig = px.bar(
        disease_df,
        x="Medical Condition",
        y="Frequency",
        title="Most Common Diseases"
    )

    fig.update_layout(
        xaxis_title="Medical Condition",
        yaxis_title="Frequency"
    )

    st.plotly_chart(fig, use_container_width=True)

    logging.info("Done with medical conditions")

   

    labels, values = database.get_drug_frequency()

    drug_df = {
        "Medication": labels,
        "Frequency": values
    }

    fig = px.bar(
        drug_df,
        x="Medication",
        y="Frequency",
        title="Drug Frequency"
    )

    fig.update_layout(
        xaxis_title="Medication",
        yaxis_title="Frequency"
    )

    st.plotly_chart(fig, use_container_width=True)

    

    labels, values = database.get_admission_type()

    admission_df = {
        "Admission Type": labels,
        "Frequency": values
    }

    fig = px.bar(
        admission_df,
        x="Admission Type",
        y="Frequency",
        title="Admission Type"
    )

    fig.update_layout(
        xaxis_title="Admission Type",
        yaxis_title="Frequency"
    )

    st.plotly_chart(fig, use_container_width=True)

    logging.info("Done with all plots!!!!")