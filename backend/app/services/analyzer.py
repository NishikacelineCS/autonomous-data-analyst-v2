import pandas as pd


def generate_insights(df: pd.DataFrame):
    insights = []

    rows = len(df)
    cols = len(df.columns)

    insights.append(
        f"Dataset contains {rows} rows and {cols} columns"
    )

    # -------------------------
    # Missing Values
    # -------------------------
    missing = df.isnull().sum()

    for col, count in missing.items():
        if count > 0:
            pct = round((count / rows) * 100, 2)

            insights.append(
                f"Column '{col}' contains {pct}% missing values"
            )

    # -------------------------
    # Duplicate Rows
    # -------------------------
    duplicates = int(df.duplicated().sum())

    if duplicates > 0:
        insights.append(
            f"Dataset contains {duplicates} duplicate rows"
        )
    else:
        insights.append(
            "No duplicate rows detected"
        )

    # -------------------------
    # Dataset Size
    # -------------------------
    if rows < 1000:
        insights.append(
            "Small dataset detected"
        )
    elif rows < 100000:
        insights.append(
            "Medium dataset detected"
        )
    else:
        insights.append(
            "Large dataset detected"
        )

    # -------------------------
    # Numeric Columns
    # -------------------------
    numeric_df = df.select_dtypes(include="number")

    if len(numeric_df.columns) == 0:
        insights.append(
            "No numeric columns available for advanced analysis"
        )
        return insights

    insights.append(
        f"{len(numeric_df.columns)} numeric columns detected"
    )

    # -------------------------
    # Correlation Analysis
    # -------------------------
    if len(numeric_df.columns) >= 2:

        corr_matrix = numeric_df.corr()

        for i in range(len(corr_matrix.columns)):
            for j in range(i + 1, len(corr_matrix.columns)):

                corr = corr_matrix.iloc[i, j]

                if abs(corr) >= 0.8:

                    insights.append(
                        f"Columns '{corr_matrix.columns[i]}' and "
                        f"'{corr_matrix.columns[j]}' are highly correlated "
                        f"({corr:.2f})"
                    )

    # -------------------------
    # Outlier Detection
    # -------------------------
    for col in numeric_df.columns:

        q1 = numeric_df[col].quantile(0.25)
        q3 = numeric_df[col].quantile(0.75)

        iqr = q3 - q1

        lower = q1 - (1.5 * iqr)
        upper = q3 + (1.5 * iqr)

        outliers = numeric_df[
            (numeric_df[col] < lower)
            | (numeric_df[col] > upper)
        ]

        if len(outliers) > 0:

            insights.append(
                f"Column '{col}' contains "
                f"{len(outliers)} potential outliers"
            )

    # -------------------------
    # Skew Detection
    # -------------------------
    skewness = numeric_df.skew()

    for col, value in skewness.items():

        if abs(value) > 1:

            direction = (
                "right-skewed"
                if value > 0
                else "left-skewed"
            )

            insights.append(
                f"Column '{col}' is heavily {direction}"
            )

    return insights