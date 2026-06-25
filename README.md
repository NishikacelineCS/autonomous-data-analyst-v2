# Autonomous Data Analyst

Autonomous Data Analyst is a data analysis platform that automatically profiles datasets and generates meaningful statistical insights from uploaded CSV files.

Built using FastAPI, Streamlit, and Pandas, the application allows users to upload datasets and instantly receive automated exploratory data analysis (EDA), data quality reports, and statistical insights through an interactive dashboard.

## Features

- Upload CSV datasets
- Automatic dataset profiling
- Dataset preview
- Column information and data types
- Missing value analysis
- Duplicate row detection
- Numeric summary statistics
- Correlation analysis
- Outlier detection using the IQR method
- Skewness detection
- Rule-based analytical insights
- Interactive dashboard built with Streamlit

## Project Architecture

```text
                 Streamlit Frontend
                         │
                         ▼
                FastAPI Backend API
                         │
                         ▼
                  Upload Service
                         │
                         ▼
              Pandas Data Processing
                         │
         ┌───────────────┴───────────────┐
         ▼                               ▼
  Profiler Service               Analyzer Service
         │                               │
         └───────────────┬───────────────┘
                         ▼
              Statistical Insights
                         │
                         ▼
               Streamlit Dashboard
```

## Project Structure

```text
autonomous-data-analyst/
│
├── backend/
│   └── app/
│       ├── api/
│       │   ├── upload.py
│       │   ├── analysis.py
│       │   ├── query.py
│       │   └── health.py
│       │
│       ├── services/
│       │   ├── profiler.py
│       │   └── analyzer.py
│       │
│       ├── agents/
│       │   ├── base_agent.py
│       │   └── profiling_agent.py
│       │
│       ├── config.py
│       └── main.py
│
├── frontend/
│   └── app.py
│
├── requirements.txt
└── README.md
```

## Technology Stack

**Frontend**
- Streamlit

**Backend**
- FastAPI
- Uvicorn

**Data Processing**
- Pandas
- NumPy

**Programming Language**
- Python

## Analysis Capabilities

The application currently performs:

- Dataset profiling
- Missing value detection
- Duplicate record detection
- Data type identification
- Numeric summary generation
- Correlation analysis
- Outlier detection using the IQR method
- Skewness analysis
- Dataset size classification

## Installation

Clone the repository:

```bash
git clone <repository-url>
cd autonomous-data-analyst
```

Create a virtual environment:

```bash
python -m venv venv
```

Activate the virtual environment.

**Windows**

```bash
venv\Scripts\activate
```

**Linux/macOS**

```bash
source venv/bin/activate
```

Install the dependencies:

```bash
pip install -r requirements.txt
```

Start the FastAPI backend:

```bash
uvicorn backend.app.main:app --reload
```

Backend:

```
http://127.0.0.1:8000
```

Swagger Documentation:

```
http://127.0.0.1:8000/docs
```

Start the Streamlit frontend:

```bash
streamlit run frontend/app.py
```

Frontend:

```
http://localhost:8501
```

## Application Workflow

1. Upload a CSV dataset.
2. The backend reads the dataset using Pandas.
3. The Profiler extracts dataset statistics.
4. The Analyzer generates statistical insights.
5. Results are displayed in the Streamlit dashboard.

## Live Demo

Frontend:

https://autonomous-data-analyst-v2-hhxupfqdyxbvv37bkoeaxj.streamlit.app/

> Note: The frontend is deployed on Streamlit Cloud. The FastAPI backend currently runs locally and will be deployed separately.

## Future Improvements

- AI-powered natural language querying
- Automatic visualization generation
- Downloadable analysis reports
- Multi-agent workflow orchestration
- Backend cloud deployment
- Support for Excel and Parquet files

## Author

**Nishika Celine C S**

B.Tech Computer Science Engineering  
SRM Institute of Science and Technology

GitHub: https://github.com/NishikacelineCS

LinkedIn: https://linkedin.com/in/nishika-celine-c-s-762269279

## Project Status

This project is under active development. The current version provides an end-to-end pipeline for dataset upload, profiling, statistical analysis, and interactive visualization. Additional AI-powered analytical capabilities and deployment enhancements are planned.
