def generate_profile(df):
    return {
        "rows": len(df),
        "columns": len(df.columns),
        "column_names": df.columns.tolist(),
        "preview": df.head().to_dict(orient="records"),
        "data_types": df.dtypes.astype(str).to_dict(),
        "missing_values": df.isnull().sum().to_dict(),
        "duplicate_rows": int(df.duplicated().sum()),
        "numeric_summary": df.describe(include=["number"]).to_dict()
    }