import pandas as pd


def calculate_match_score(
    scheme,
    age,
    business_type,
    business_stage,
    investment_required,
    target_category,
    state
):
    score = 0
    reasons = []
    warnings = []

    # --------------------------------------------------
    # 1. AGE CHECK — 10 POINTS
    # --------------------------------------------------

    if age >= scheme["min_age"]:
        score += 10
        reasons.append("Age requirement satisfied.")
    else:
        warnings.append(
            "Age requirement may not be satisfied."
        )

    # --------------------------------------------------
    # 2. BUSINESS TYPE — 25 POINTS
    # --------------------------------------------------

    business_types = [
        item.strip()
        for item in str(
            scheme["business_types"]
        ).split("|")
    ]

    if business_type in business_types:
        # Exact business type match
        score += 25

        reasons.append(
            "Your business type matches the scheme."
        )

    elif "Other" in business_types:
        # Other is only a fallback.
        # Do NOT give full points.
        score += 5

        reasons.append(
            "The scheme may support other business types."
        )

    else:
        warnings.append(
            "Your business type does not appear "
            "to match the listed sectors."
        )

    # --------------------------------------------------
    # 3. BUSINESS STAGE — 20 POINTS
    # --------------------------------------------------

    business_stages = [
        item.strip()
        for item in str(
            scheme["business_stages"]
        ).split("|")
    ]

    if business_stage in business_stages:

        score += 20

        reasons.append(
            "Your business stage matches the scheme."
        )

    else:

        warnings.append(
            "Your current business stage may not match."
        )

    # --------------------------------------------------
    # 4. INVESTMENT — 20 POINTS
    # --------------------------------------------------

    max_project_cost = float(
        scheme["max_project_cost"]
    )

    if investment_required <= max_project_cost:

        score += 20

        reasons.append(
            "Your required investment is within "
            "the scheme's project-cost range."
        )

    else:

        warnings.append(
            "Your required investment exceeds "
            "the listed project-cost limit."
        )

    # --------------------------------------------------
    # 5. TARGET CATEGORY — 15 POINTS
    # --------------------------------------------------

    target_groups = [
        item.strip()
        for item in str(
            scheme["target_groups"]
        ).split("|")
    ]

    if target_category in target_groups:

        # Exact category match
        score += 15

        reasons.append(
            "Your entrepreneur category is "
            "specifically supported."
        )

    elif (
        target_category == "General"
        and "General" in target_groups
    ):

        # General entrepreneur + General scheme
        score += 10

        reasons.append(
            "The scheme is open to general entrepreneurs."
        )

    elif "General" in target_groups:

        # Other categories using a generally available scheme
        score += 5

        reasons.append(
            "The scheme may be available to a broad "
            "range of entrepreneurs."
        )

    else:

        warnings.append(
            "Your entrepreneur category may not "
            "be specifically covered."
        )

    # --------------------------------------------------
    # 6. LOCATION — 10 POINTS
    # --------------------------------------------------

    scheme_location = str(
        scheme["location"]
    )

    if (
        scheme_location == "All India"
        or state in scheme_location
    ):

        score += 10

        reasons.append(
            "Your location is covered."
        )

    else:

        warnings.append(
            "Location eligibility needs verification."
        )

    # --------------------------------------------------
    # RETURN RESULT
    # --------------------------------------------------

    return score, reasons, warnings


def match_schemes(
    schemes,
    age,
    business_type,
    business_stage,
    investment_required,
    target_category,
    state
):

    results = []

    for _, scheme in schemes.iterrows():

        score, reasons, warnings = calculate_match_score(
            scheme,
            age,
            business_type,
            business_stage,
            investment_required,
            target_category,
            state
        )

        result = {
            "scheme_id": scheme["scheme_id"],
            "scheme_name": scheme["scheme_name"],
            "score": score,
            "benefit_type": scheme["benefit_type"],
            "benefit_description": scheme[
                "benefit_description"
            ],
            "official_url": scheme["official_url"],
            "reasons": reasons,
            "warnings": warnings
        }

        results.append(result)

    # --------------------------------------------------
    # SORT BY MATCH SCORE
    # --------------------------------------------------

    results = sorted(
        results,
        key=lambda x: x["score"],
        reverse=True
    )

    return results