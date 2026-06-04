import streamlit as st
import pandas as pd
import requests

# -----------------------------
# Page Config
# -----------------------------
st.set_page_config(
    page_title="Autonomous Data Analyst",
    page_icon="🤖",
    layout="wide"
)

# -----------------------------
# Title
# -----------------------------
st.title("🤖 Autonomous Data Analyst")
st.markdown("Upload a CSV dataset and automatically generate insights.")

st.divider()

# -----------------------------
# File Upload
# -----------------------------
uploaded_file = st.file_uploader(
    "Upload a CSV file",
    type=["csv"]
)

# -----------------------------
# Process File
# -----------------------------
if uploaded_file is not None:

    files = {
        "file": (
            uploaded_file.name,
            uploaded_file.getvalue(),
            "text/csv"
        )
    }

    with st.spinner("Analyzing dataset..."):

       response = requests.post(
    "https://autonomous-data-analyst-api.onrender.com/api/v1/upload/",
    files=files
)

    if response.status_code == 200:

        data = response.json()

        st.success("Dataset uploaded successfully!")

        # =========================
        # Metrics Section
        # =========================
        st.subheader("📊 Dataset Summary")

        col1, col2 = st.columns(2)

        with col1:
            st.metric(
                label="Rows",
                value=data["rows"]
            )

        with col2:
            st.metric(
                label="Columns",
                value=data["columns"]
            )

        st.divider()

        # =========================
        # Insights Section
        # =========================
        st.subheader("🧠 Insights")

        for insight in data["insights"]:
            st.success(insight)

        st.divider()

        # =========================
        # Tabs
        # =========================
        tab1, tab2, tab3 = st.tabs(
            [
                "📋 Preview",
                "🔍 Profile",
                "📈 Statistics"
            ]
        )

        # -------------------------
        # Preview Tab
        # -------------------------
        with tab1:

            st.subheader("Dataset Preview")

            preview_df = pd.DataFrame(
                data["preview"]
            )

            st.dataframe(
                preview_df,
                use_container_width=True
            )

        # -------------------------
        # Profile Tab
        # -------------------------
        with tab2:

            st.subheader("Column Names")

            st.write(data["column_names"])

            st.subheader("Data Types")

            dtype_df = pd.DataFrame(
                list(data["data_types"].items()),
                columns=["Column", "Data Type"]
            )

            st.dataframe(
                dtype_df,
                use_container_width=True
            )

            st.subheader("Missing Values")

            missing_df = pd.DataFrame(
                list(data["missing_values"].items()),
                columns=["Column", "Missing Values"]
            )

            st.dataframe(
                missing_df,
                use_container_width=True
            )

            st.metric(
                "Duplicate Rows",
                data["duplicate_rows"]
            )

        # -------------------------
        # Statistics Tab
        # -------------------------
        with tab3:

            st.subheader("Numeric Summary")

            numeric_summary = pd.DataFrame(
                data["numeric_summary"]
            )

            st.dataframe(
                numeric_summary,
                use_container_width=True
            )

    else:
        st.error(
            f"API Error: {response.status_code}"
        )