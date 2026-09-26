import hashlib
from datetime import datetime

from modules.database import (
    get_profiles,
    get_scheme_snapshots,
    save_scheme_snapshot,
    save_notification,
    get_notification_status
)

from modules.matching import match_schemes


# ========================================================
# SCHEME HASH
# ========================================================

def calculate_scheme_hash(scheme):

    scheme_data = "|".join([
        str(scheme["scheme_name"]),
        str(scheme["target_groups"]),
        str(scheme["business_types"]),
        str(scheme["business_stages"]),
        str(scheme["min_age"]),
        str(scheme["max_project_cost"]),
        str(scheme["location"]),
        str(scheme["benefit_type"]),
        str(scheme["benefit_description"]),
        str(scheme["official_url"]),
        str(scheme.get("deadline", ""))
    ])

    return hashlib.sha256(
        scheme_data.encode("utf-8")
    ).hexdigest()


def get_scheme_hashes(schemes):

    hashes = {}

    for _, scheme in schemes.iterrows():

        hashes[scheme["scheme_id"]] = (
            calculate_scheme_hash(scheme)
        )

    return hashes


# ========================================================
# PROFILE CONVERSION
# ========================================================

def profile_to_dict(profile):

    return {
        "id": profile[0],
        "name": profile[1],
        "age": profile[2],
        "state": profile[3],
        "district": profile[4],
        "category": profile[5],
        "business_type": profile[6],
        "business_stage": profile[7],
        "annual_income": profile[8],
        "investment": profile[9],
        "employees": profile[10],
    }


# ========================================================
# CHECK WHETHER SCHEME MATCHES PROFILE
# ========================================================

def get_scheme_match(
    profile,
    scheme,
    all_schemes
):

    profile_data = profile_to_dict(profile)

    results = match_schemes(
        all_schemes,
        profile_data["age"],
        profile_data["business_type"],
        profile_data["business_stage"],
        profile_data["investment"],
        profile_data["category"],
        profile_data["state"]
    )

    for result in results:

        if result["scheme_id"] == scheme["scheme_id"]:

            if result["score"] > 0:
                return result

            break

    return None


# ========================================================
# NEW SCHEME NOTIFICATIONS
# ========================================================

def create_new_scheme_notifications(
    schemes,
    new_scheme_ids
):

    profiles = get_profiles()

    notification_count = 0

    for _, scheme in schemes.iterrows():

        scheme_id = scheme["scheme_id"]

        if scheme_id not in new_scheme_ids:
            continue

        for profile in profiles:

            profile_data = profile_to_dict(profile)

            if not get_notification_status(
                profile_data["id"]
            ):
                continue

            result = get_scheme_match(
                profile,
                scheme,
                schemes
            )

            if result is None:
                continue

            notification_id = save_notification(
                profile_id=profile_data["id"],
                scheme_id=scheme_id,
                notification_type="NEW_SCHEME",
                title="New Scheme Available",
                message=(
                    f"{scheme['scheme_name']} may be relevant "
                    f"to your entrepreneur profile."
                )
            )

            if notification_id is not None:
                notification_count += 1

    return notification_count


# ========================================================
# UPDATED SCHEME NOTIFICATIONS
# ========================================================

def create_updated_scheme_notifications(
    schemes,
    updated_scheme_ids
):

    profiles = get_profiles()

    notification_count = 0

    for _, scheme in schemes.iterrows():

        scheme_id = scheme["scheme_id"]

        if scheme_id not in updated_scheme_ids:
            continue

        for profile in profiles:

            profile_data = profile_to_dict(profile)

            if not get_notification_status(
                profile_data["id"]
            ):
                continue

            result = get_scheme_match(
                profile,
                scheme,
                schemes
            )

            if result is None:
                continue

            notification_id = save_notification(
                profile_id=profile_data["id"],
                scheme_id=scheme_id,
                notification_type="SCHEME_UPDATED",
                title="Scheme Updated",
                message=(
                    f"Important information about "
                    f"{scheme['scheme_name']} has changed."
                )
            )

            if notification_id is not None:
                notification_count += 1

    return notification_count


# ========================================================
# DEADLINE NOTIFICATIONS
# ========================================================

def create_deadline_notifications(schemes):

    profiles = get_profiles()

    notification_count = 0

    today = datetime.now().date()

    for _, scheme in schemes.iterrows():

        # ------------------------------------------------
        # Check whether deadline column exists
        # ------------------------------------------------

        if "deadline" not in scheme.index:
            continue

        deadline_value = scheme["deadline"]

        # Ignore empty deadlines
        if (
            deadline_value is None
            or str(deadline_value).strip() == ""
            or str(deadline_value).lower() == "nan"
        ):
            continue

        try:

            deadline = datetime.strptime(
                str(deadline_value).strip(),
                "%Y-%m-%d"
            ).date()

        except ValueError:

            # Ignore invalid date formats
            continue

        days_remaining = (
            deadline - today
        ).days

        # ------------------------------------------------
        # Only notify before/on deadline
        # ------------------------------------------------

        if days_remaining not in [7, 3, 1, 0]:
            continue

        for profile in profiles:

            profile_data = profile_to_dict(profile)

            # ------------------------------------------------
            # Respect profile notification setting
            # ------------------------------------------------

            if not get_notification_status(
                profile_data["id"]
            ):
                continue

            # ------------------------------------------------
            # Only notify if scheme matches profile
            # ------------------------------------------------

            result = get_scheme_match(
                profile,
                scheme,
                schemes
            )

            if result is None:
                continue

            scheme_name = scheme["scheme_name"]

            if days_remaining == 0:

                title = "Scheme Deadline Today"

                message = (
                    f"{scheme_name} has a deadline today. "
                    f"Please check the official information "
                    f"before applying."
                )

            elif days_remaining == 1:

                title = "Scheme Deadline Tomorrow"

                message = (
                    f"{scheme_name} has a deadline tomorrow. "
                    f"Please check the official information "
                    f"before applying."
                )

            else:

                title = "Upcoming Scheme Deadline"

                message = (
                    f"{scheme_name} has a deadline in "
                    f"{days_remaining} days. "
                    f"Please check the official information "
                    f"before applying."
                )

            notification_id = save_notification(
                profile_id=profile_data["id"],
                scheme_id=scheme["scheme_id"],
                notification_type="DEADLINE",
                title=title,
                message=message
            )

            if notification_id is not None:
                notification_count += 1

    return notification_count


# ========================================================
# MAIN NOTIFICATION CHECK
# ========================================================

def run_notification_check(schemes):

    previous_snapshots = get_scheme_snapshots()

    current_hashes = get_scheme_hashes(schemes)

    current_scheme_ids = set(
        current_hashes.keys()
    )

    previous_scheme_ids = set(
        previous_snapshots.keys()
    )

    # ----------------------------------------------------
    # NEW SCHEMES
    # ----------------------------------------------------

    new_scheme_ids = (
        current_scheme_ids
        - previous_scheme_ids
    )

    # ----------------------------------------------------
    # UPDATED SCHEMES
    # ----------------------------------------------------

    updated_scheme_ids = set()

    for scheme_id in (
        current_scheme_ids
        & previous_scheme_ids
    ):

        previous_hash = previous_snapshots[
            scheme_id
        ]["data_hash"]

        current_hash = current_hashes[
            scheme_id
        ]

        if previous_hash != current_hash:

            updated_scheme_ids.add(
                scheme_id
            )

    # ----------------------------------------------------
    # CREATE NOTIFICATIONS
    # ----------------------------------------------------

    new_notifications = (
        create_new_scheme_notifications(
            schemes,
            new_scheme_ids
        )
    )

    updated_notifications = (
        create_updated_scheme_notifications(
            schemes,
            updated_scheme_ids
        )
    )

    deadline_notifications = (
        create_deadline_notifications(
            schemes
        )
    )

    # ----------------------------------------------------
    # SAVE CURRENT SNAPSHOTS
    # ----------------------------------------------------

    for _, scheme in schemes.iterrows():

        scheme_id = scheme["scheme_id"]

        save_scheme_snapshot(
            scheme_id=scheme_id,
            scheme_name=scheme["scheme_name"],
            data_hash=current_hashes[scheme_id]
        )

    # ----------------------------------------------------
    # RETURN INFORMATION
    # ----------------------------------------------------

    return {
        "new_notifications": new_notifications,
        "updated_notifications": updated_notifications,
        "deadline_notifications": deadline_notifications,
        "new_scheme_ids": new_scheme_ids,
        "updated_scheme_ids": updated_scheme_ids
    }