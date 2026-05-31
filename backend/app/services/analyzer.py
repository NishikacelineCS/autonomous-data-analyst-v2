def generate_insights(profile):
    insights = []

    insights.append(
        f"Dataset contains {profile['rows']} rows and {profile['columns']} columns"
    )

    if profile["duplicate_rows"] == 0:
        insights.append("No duplicate rows detected")

    total_missing = sum(profile["missing_values"].values())

    if total_missing == 0:
        insights.append("No missing values detected")
    else:
        insights.append(f"Dataset contains {total_missing} missing values")

    return insights