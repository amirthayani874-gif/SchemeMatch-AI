import sqlite3
from pathlib import Path
from datetime import datetime
import re
import uuid


# ========================================================
# PATHS
# ========================================================

BASE_DIR = Path(__file__).resolve().parent.parent

DB_PATH = BASE_DIR / "schemematch.db"

UPLOAD_DIR = BASE_DIR / "data" / "uploads"
UPLOAD_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# ========================================================
# DATABASE CONNECTION
# ========================================================

def get_connection():
    return sqlite3.connect(DB_PATH)


# ========================================================
# DOCUMENT UPLOAD TABLE
# ========================================================

def initialize_document_upload_table():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS document_uploads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,

            profile_id INTEGER NOT NULL,

            scheme_id TEXT NOT NULL,

            document_name TEXT NOT NULL,

            file_name TEXT NOT NULL,

            file_path TEXT NOT NULL,

            uploaded_at TEXT NOT NULL,

            UNIQUE (
                profile_id,
                scheme_id,
                document_name
            ),

            FOREIGN KEY (profile_id)
            REFERENCES profiles(id)
        )
    """)

    conn.commit()
    conn.close()


# ========================================================
# DATABASE INITIALIZATION
# ========================================================

def initialize_database():

    conn = get_connection()
    cursor = conn.cursor()

    # ====================================================
    # PROFILES
    # ====================================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS profiles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            age INTEGER,
            state TEXT,
            district TEXT,
            category TEXT,
            business_type TEXT,
            business_stage TEXT,
            annual_income REAL,
            investment REAL,
            employees INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # ====================================================
    # SCHEME SNAPSHOTS
    # ====================================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS scheme_snapshots (
            scheme_id TEXT PRIMARY KEY,
            scheme_name TEXT,
            data_hash TEXT,
            last_checked TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # ====================================================
    # NOTIFICATIONS
    # ====================================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS notifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,

            profile_id INTEGER NOT NULL,

            scheme_id TEXT,

            notification_type TEXT NOT NULL,

            title TEXT NOT NULL,

            message TEXT NOT NULL,

            is_read INTEGER DEFAULT 0,

            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

            FOREIGN KEY (profile_id)
            REFERENCES profiles(id)
        )
    """)

    # ====================================================
    # PROFILE NOTIFICATION SETTINGS
    # ====================================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS profile_notification_settings (
            profile_id INTEGER PRIMARY KEY,

            notifications_enabled INTEGER DEFAULT 1,

            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

            FOREIGN KEY (profile_id)
            REFERENCES profiles(id)
        )
    """)

    cursor.execute("""
        INSERT OR IGNORE INTO profile_notification_settings (
            profile_id,
            notifications_enabled
        )
        SELECT id, 1
        FROM profiles
    """)

    # ====================================================
    # DOCUMENT READINESS
    # ====================================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS document_readiness (
            id INTEGER PRIMARY KEY AUTOINCREMENT,

            profile_id INTEGER NOT NULL,

            scheme_id TEXT NOT NULL,

            document_name TEXT NOT NULL,

            status TEXT DEFAULT 'missing',

            file_name TEXT,

            file_path TEXT,

            uploaded_at TIMESTAMP,

            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

            UNIQUE (
                profile_id,
                scheme_id,
                document_name
            ),

            FOREIGN KEY (profile_id)
            REFERENCES profiles(id)
        )
    """)

    # ====================================================
    # DOCUMENT READINESS MIGRATION
    # ====================================================

    cursor.execute("""
        PRAGMA table_info(document_readiness)
    """)

    existing_columns = {
        row[1]
        for row in cursor.fetchall()
    }

    if "file_name" not in existing_columns:

        cursor.execute("""
            ALTER TABLE document_readiness
            ADD COLUMN file_name TEXT
        """)

    if "file_path" not in existing_columns:

        cursor.execute("""
            ALTER TABLE document_readiness
            ADD COLUMN file_path TEXT
        """)

    if "uploaded_at" not in existing_columns:

        cursor.execute("""
            ALTER TABLE document_readiness
            ADD COLUMN uploaded_at TIMESTAMP
        """)

    # ====================================================
    # REQUIRED SCHEME DOCUMENTS
    # ====================================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS scheme_documents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,

            scheme_id TEXT NOT NULL,

            document_name TEXT NOT NULL,

            UNIQUE (
                scheme_id,
                document_name
            )
        )
    """)

    # ====================================================
    # DOCUMENT UPLOADS
    # ====================================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS document_uploads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,

            profile_id INTEGER NOT NULL,

            scheme_id TEXT NOT NULL,

            document_name TEXT NOT NULL,

            file_name TEXT NOT NULL,

            file_path TEXT NOT NULL,

            uploaded_at TEXT NOT NULL,

            UNIQUE (
                profile_id,
                scheme_id,
                document_name
            ),

            FOREIGN KEY (profile_id)
            REFERENCES profiles(id)
        )
    """)

    conn.commit()
    conn.close()

    # Add default documents
    initialize_scheme_documents()


# ========================================================
# PROFILES
# ========================================================

def create_profile(
    name,
    age,
    state,
    district,
    category,
    business_type,
    business_stage,
    annual_income,
    investment,
    employees
):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO profiles (
            name,
            age,
            state,
            district,
            category,
            business_type,
            business_stage,
            annual_income,
            investment,
            employees
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        name,
        age,
        state,
        district,
        category,
        business_type,
        business_stage,
        annual_income,
        investment,
        employees
    ))

    profile_id = cursor.lastrowid

    cursor.execute("""
        INSERT OR IGNORE INTO profile_notification_settings (
            profile_id,
            notifications_enabled
        )
        VALUES (?, 1)
    """, (
        profile_id,
    ))

    conn.commit()
    conn.close()

    return profile_id


def get_profiles():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM profiles
        ORDER BY created_at DESC
    """)

    profiles = cursor.fetchall()

    conn.close()

    return profiles


def get_profile(profile_id):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM profiles
        WHERE id = ?
    """, (
        profile_id,
    ))

    profile = cursor.fetchone()

    conn.close()

    return profile


# ========================================================
# DELETE PROFILE
# ========================================================

def delete_profile(profile_id):

    conn = get_connection()
    cursor = conn.cursor()

    # ----------------------------------------------------
    # Find files from document_readiness
    # ----------------------------------------------------

    cursor.execute("""
        SELECT file_path
        FROM document_readiness
        WHERE profile_id = ?
    """, (
        profile_id,
    ))

    readiness_files = cursor.fetchall()

    for row in readiness_files:

        if row[0]:

            file_path = Path(row[0])

            if file_path.exists():

                try:
                    file_path.unlink()
                except Exception:
                    pass

    # ----------------------------------------------------
    # Find files from document_uploads
    # ----------------------------------------------------

    cursor.execute("""
        SELECT file_path
        FROM document_uploads
        WHERE profile_id = ?
    """, (
        profile_id,
    ))

    upload_files = cursor.fetchall()

    for row in upload_files:

        if row[0]:

            file_path = Path(row[0])

            if file_path.exists():

                try:
                    file_path.unlink()
                except Exception:
                    pass

    # ----------------------------------------------------
    # Delete notifications
    # ----------------------------------------------------

    cursor.execute("""
        DELETE FROM notifications
        WHERE profile_id = ?
    """, (
        profile_id,
    ))

    # ----------------------------------------------------
    # Delete document readiness
    # ----------------------------------------------------

    cursor.execute("""
        DELETE FROM document_readiness
        WHERE profile_id = ?
    """, (
        profile_id,
    ))

    # ----------------------------------------------------
    # Delete document uploads
    # ----------------------------------------------------

    cursor.execute("""
        DELETE FROM document_uploads
        WHERE profile_id = ?
    """, (
        profile_id,
    ))

    # ----------------------------------------------------
    # Delete notification settings
    # ----------------------------------------------------

    cursor.execute("""
        DELETE FROM profile_notification_settings
        WHERE profile_id = ?
    """, (
        profile_id,
    ))

    # ----------------------------------------------------
    # Delete profile
    # ----------------------------------------------------

    cursor.execute("""
        DELETE FROM profiles
        WHERE id = ?
    """, (
        profile_id,
    ))

    conn.commit()
    conn.close()


# ========================================================
# NOTIFICATION SETTINGS
# ========================================================

def get_notification_status(profile_id):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT notifications_enabled
        FROM profile_notification_settings
        WHERE profile_id = ?
    """, (
        profile_id,
    ))

    result = cursor.fetchone()

    if result is None:

        cursor.execute("""
            INSERT INTO profile_notification_settings (
                profile_id,
                notifications_enabled
            )
            VALUES (?, 1)
        """, (
            profile_id,
        ))

        conn.commit()
        conn.close()

        return True

    conn.close()

    return bool(result[0])


def set_notification_status(
    profile_id,
    enabled
):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO profile_notification_settings (
            profile_id,
            notifications_enabled,
            updated_at
        )
        VALUES (?, ?, CURRENT_TIMESTAMP)

        ON CONFLICT(profile_id)
        DO UPDATE SET
            notifications_enabled = excluded.notifications_enabled,
            updated_at = CURRENT_TIMESTAMP
    """, (
        profile_id,
        1 if enabled else 0
    ))

    conn.commit()
    conn.close()


# ========================================================
# SCHEME SNAPSHOTS
# ========================================================

def get_scheme_snapshots():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            scheme_id,
            scheme_name,
            data_hash
        FROM scheme_snapshots
    """)

    rows = cursor.fetchall()

    conn.close()

    return {
        row[0]: {
            "scheme_name": row[1],
            "data_hash": row[2]
        }
        for row in rows
    }


def save_scheme_snapshot(
    scheme_id,
    scheme_name,
    data_hash
):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO scheme_snapshots (
            scheme_id,
            scheme_name,
            data_hash,
            last_checked
        )
        VALUES (?, ?, ?, CURRENT_TIMESTAMP)

        ON CONFLICT(scheme_id)
        DO UPDATE SET
            scheme_name = excluded.scheme_name,
            data_hash = excluded.data_hash,
            last_checked = CURRENT_TIMESTAMP
    """, (
        scheme_id,
        scheme_name,
        data_hash
    ))

    conn.commit()
    conn.close()


# ========================================================
# NOTIFICATIONS
# ========================================================

def save_notification(
    profile_id,
    scheme_id,
    notification_type,
    title,
    message
):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id
        FROM notifications
        WHERE profile_id = ?
        AND scheme_id = ?
        AND notification_type = ?
        AND message = ?
    """, (
        profile_id,
        scheme_id,
        notification_type,
        message
    ))

    existing = cursor.fetchone()

    if existing:

        conn.close()

        return existing[0]

    cursor.execute("""
        INSERT INTO notifications (
            profile_id,
            scheme_id,
            notification_type,
            title,
            message
        )
        VALUES (?, ?, ?, ?, ?)
    """, (
        profile_id,
        scheme_id,
        notification_type,
        title,
        message
    ))

    notification_id = cursor.lastrowid

    conn.commit()
    conn.close()

    return notification_id


def get_notifications(profile_id):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM notifications
        WHERE profile_id = ?
        ORDER BY created_at DESC
    """, (
        profile_id,
    ))

    notifications = cursor.fetchall()

    conn.close()

    return notifications


def mark_notification_read(notification_id):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE notifications
        SET is_read = 1
        WHERE id = ?
    """, (
        notification_id,
    ))

    conn.commit()
    conn.close()


# ========================================================
# SCHEME DOCUMENTS
# ========================================================

def save_scheme_document(
    scheme_id,
    document_name
):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT OR IGNORE INTO scheme_documents (
            scheme_id,
            document_name
        )
        VALUES (?, ?)
    """, (
        scheme_id,
        document_name
    ))

    conn.commit()
    conn.close()


def get_scheme_documents(scheme_id):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT document_name
        FROM scheme_documents
        WHERE scheme_id = ?
        ORDER BY id
    """, (
        scheme_id,
    ))

    documents = cursor.fetchall()

    conn.close()

    return [
        row[0]
        for row in documents
    ]


def delete_scheme_documents(scheme_id):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        DELETE FROM scheme_documents
        WHERE scheme_id = ?
    """, (
        scheme_id,
    ))

    conn.commit()
    conn.close()


# ========================================================
# DEFAULT SCHEME DOCUMENTS
# ========================================================

def initialize_scheme_documents():

    scheme_documents = {

        # ------------------------------------------------
        # PMEGP
        # ------------------------------------------------

        "PMEGP": [
            "Aadhaar Card",
            "Passport Size Photograph",
            "Caste Certificate",
            "Special Category Certificate",
            "Rural Area Certificate",
            "Project Report",
            "Education / EDP / Skill Development Certificate"
        ],

        # ------------------------------------------------
        # PMMY
        # ------------------------------------------------

        "PMMY": [
            "Identity Proof",
            "Address Proof",
            "Passport Size Photograph",
            "Business / Activity Proof",
            "Bank Account Details",
            "Business Plan / Project Details"
        ],

        # ------------------------------------------------
        # CGTMSE
        # ------------------------------------------------

        "CGTMSE": [
            "Business Registration / Udyam Certificate",
            "PAN Card",
            "Aadhaar Card",
            "Business Address Proof",
            "Financial Statements",
            "Bank / Loan Documents"
        ],

        # ------------------------------------------------
        # PM VISHWAKARMA
        # ------------------------------------------------

        "PMVISHWAKARMA": [
            "Aadhaar Card",
            "Identity Proof",
            "Bank Account Details",
            "Mobile Number",
            "Certificate / Proof of Trade"
        ]
    }

    for scheme_id, documents in scheme_documents.items():

        for document in documents:

            save_scheme_document(
                scheme_id,
                document
            )


# ========================================================
# DOCUMENT READINESS
# ========================================================

def get_document_readiness(
    profile_id,
    scheme_id
):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            id,
            profile_id,
            scheme_id,
            document_name,
            status,
            file_name,
            file_path,
            uploaded_at,
            updated_at
        FROM document_readiness
        WHERE profile_id = ?
        AND scheme_id = ?
        ORDER BY id
    """, (
        profile_id,
        scheme_id
    ))

    documents = cursor.fetchall()

    conn.close()

    return documents


# ========================================================
# GET SINGLE DOCUMENT
# ========================================================

def get_document(
    profile_id,
    scheme_id,
    document_name
):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            id,
            profile_id,
            scheme_id,
            document_name,
            status,
            file_name,
            file_path,
            uploaded_at,
            updated_at
        FROM document_readiness
        WHERE profile_id = ?
        AND scheme_id = ?
        AND document_name = ?
    """, (
        profile_id,
        scheme_id,
        document_name
    ))

    document = cursor.fetchone()

    conn.close()

    return document


# ========================================================
# DOCUMENT UPLOAD
# ========================================================

def save_uploaded_document(
    profile_id,
    scheme_id,
    document_name,
    uploaded_file
):

    profile_folder = (
        UPLOAD_DIR
        / f"PROF-{int(profile_id):03d}"
        / str(scheme_id)
    )

    profile_folder.mkdir(
        parents=True,
        exist_ok=True
    )

    original_name = Path(
        uploaded_file.name
    ).name

    safe_name = re.sub(
        r"[^a-zA-Z0-9._-]",
        "_",
        original_name
    )

    unique_name = (
        f"{uuid.uuid4().hex[:10]}_"
        f"{safe_name}"
    )

    file_path = profile_folder / unique_name

    with open(
        file_path,
        "wb"
    ) as file:

        file.write(
            uploaded_file.getbuffer()
        )

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT file_path
        FROM document_readiness
        WHERE profile_id = ?
        AND scheme_id = ?
        AND document_name = ?
    """, (
        profile_id,
        scheme_id,
        document_name
    ))

    old_record = cursor.fetchone()

    if old_record and old_record[0]:

        old_path = Path(
            old_record[0]
        )

        if old_path.exists():

            try:
                old_path.unlink()
            except Exception:
                pass

    uploaded_at = datetime.now()

    cursor.execute("""
        INSERT INTO document_readiness (
            profile_id,
            scheme_id,
            document_name,
            status,
            file_name,
            file_path,
            uploaded_at,
            updated_at
        )
        VALUES (
            ?,
            ?,
            ?,
            'available',
            ?,
            ?,
            ?,
            CURRENT_TIMESTAMP
        )

        ON CONFLICT(
            profile_id,
            scheme_id,
            document_name
        )
        DO UPDATE SET
            status = 'available',
            file_name = excluded.file_name,
            file_path = excluded.file_path,
            uploaded_at = excluded.uploaded_at,
            updated_at = CURRENT_TIMESTAMP
    """, (
        profile_id,
        scheme_id,
        document_name,
        original_name,
        str(file_path),
        uploaded_at
    ))

    conn.commit()
    conn.close()


# ========================================================
# REMOVE UPLOADED DOCUMENT
# ========================================================

def remove_uploaded_document(
    profile_id,
    scheme_id,
    document_name
):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT file_path
        FROM document_readiness
        WHERE profile_id = ?
        AND scheme_id = ?
        AND document_name = ?
    """, (
        profile_id,
        scheme_id,
        document_name
    ))

    record = cursor.fetchone()

    if record and record[0]:

        file_path = Path(
            record[0]
        )

        if file_path.exists():

            try:
                file_path.unlink()
            except Exception:
                pass

    cursor.execute("""
        UPDATE document_readiness
        SET
            status = 'missing',
            file_name = NULL,
            file_path = NULL,
            uploaded_at = NULL,
            updated_at = CURRENT_TIMESTAMP
        WHERE profile_id = ?
        AND scheme_id = ?
        AND document_name = ?
    """, (
        profile_id,
        scheme_id,
        document_name
    ))

    conn.commit()
    conn.close()


# ========================================================
# DOCUMENT STATUS HELPERS
# ========================================================

def get_document_status(
    profile_id,
    scheme_id,
    document_name
):

    document = get_document(
        profile_id,
        scheme_id,
        document_name
    )

    if not document:

        return "missing"

    return document[4]


def is_document_available(
    profile_id,
    scheme_id,
    document_name
):

    return (
        get_document_status(
            profile_id,
            scheme_id,
            document_name
        )
        == "available"
    )


# ========================================================
# DOCUMENT READINESS SUMMARY
# ========================================================

def get_document_readiness_summary(
    profile_id,
    scheme_id
):

    required_documents = get_scheme_documents(
        scheme_id
    )

    total_documents = len(
        required_documents
    )

    if total_documents == 0:

        return {
            "total": 0,
            "ready": 0,
            "missing": 0,
            "percentage": 0
        }

    uploaded_documents = 0

    for document_name in required_documents:

        if is_document_available(
            profile_id,
            scheme_id,
            document_name
        ):

            uploaded_documents += 1

    missing_documents = (
        total_documents
        - uploaded_documents
    )

    percentage = round(
        (
            uploaded_documents
            / total_documents
        ) * 100
    )

    return {
        "total": total_documents,
        "ready": uploaded_documents,
        "missing": missing_documents,
        "percentage": percentage
    }


# ========================================================
# BACKWARD COMPATIBILITY
# ========================================================

def save_document_status(
    profile_id,
    scheme_id,
    document_name,
    status
):

    allowed_statuses = {
        "missing",
        "available"
    }

    if status not in allowed_statuses:

        raise ValueError(
            "Document status can only be "
            "'missing' or 'available'."
        )

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO document_readiness (
            profile_id,
            scheme_id,
            document_name,
            status,
            updated_at
        )
        VALUES (
            ?,
            ?,
            ?,
            ?,
            CURRENT_TIMESTAMP
        )

        ON CONFLICT(
            profile_id,
            scheme_id,
            document_name
        )
        DO UPDATE SET
            status = excluded.status,
            updated_at = CURRENT_TIMESTAMP
    """, (
        profile_id,
        scheme_id,
        document_name,
        status
    ))

    conn.commit()
    conn.close()


# ========================================================
# GET UPLOADED DOCUMENT
# ========================================================

def get_document_upload(
    profile_id,
    scheme_id,
    document_name
):

    initialize_document_upload_table()

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            id,
            profile_id,
            scheme_id,
            document_name,
            file_name,
            file_path,
            uploaded_at
        FROM document_uploads
        WHERE profile_id = ?
        AND scheme_id = ?
        AND document_name = ?
    """, (
        profile_id,
        scheme_id,
        document_name
    ))

    result = cursor.fetchone()

    conn.close()

    return result


# ========================================================
# SAVE DOCUMENT UPLOAD
# ========================================================

def save_document_upload(
    profile_id,
    scheme_id,
    document_name,
    uploaded_file
):

    initialize_document_upload_table()

    profile_folder = (
        UPLOAD_DIR
        / f"PROF-{int(profile_id):03d}"
        / str(scheme_id)
    )

    profile_folder.mkdir(
        parents=True,
        exist_ok=True
    )

    # ----------------------------------------------------
    # Clean filename
    # ----------------------------------------------------

    original_name = Path(
        uploaded_file.name
    ).name

    safe_name = re.sub(
        r"[^a-zA-Z0-9._-]",
        "_",
        original_name
    )

    unique_name = (
        f"{uuid.uuid4().hex[:10]}_"
        f"{safe_name}"
    )

    file_path = profile_folder / unique_name

    # ----------------------------------------------------
    # Save physical file
    # ----------------------------------------------------

    with open(
        file_path,
        "wb"
    ) as file:

        file.write(
            uploaded_file.getbuffer()
        )

    uploaded_at = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    conn = get_connection()
    cursor = conn.cursor()

    # ----------------------------------------------------
    # Find old document
    # ----------------------------------------------------

    cursor.execute("""
        SELECT file_path
        FROM document_uploads
        WHERE profile_id = ?
        AND scheme_id = ?
        AND document_name = ?
    """, (
        profile_id,
        scheme_id,
        document_name
    ))

    old_record = cursor.fetchone()

    # ----------------------------------------------------
    # Delete old physical file
    # ----------------------------------------------------

    if old_record and old_record[0]:

        old_path = Path(
            old_record[0]
        )

        if old_path.exists():

            try:
                old_path.unlink()
            except Exception:
                pass

    # ----------------------------------------------------
    # Save database record
    # ----------------------------------------------------

    cursor.execute("""
        INSERT INTO document_uploads (
            profile_id,
            scheme_id,
            document_name,
            file_name,
            file_path,
            uploaded_at
        )
        VALUES (?, ?, ?, ?, ?, ?)

        ON CONFLICT(
            profile_id,
            scheme_id,
            document_name
        )
        DO UPDATE SET
            file_name = excluded.file_name,
            file_path = excluded.file_path,
            uploaded_at = excluded.uploaded_at
    """, (
        profile_id,
        scheme_id,
        document_name,
        original_name,
        str(file_path),
        uploaded_at
    ))

    conn.commit()
    conn.close()


# ========================================================
# DELETE DOCUMENT UPLOAD
# ========================================================

def delete_document_upload(
    profile_id,
    scheme_id,
    document_name
):

    initialize_document_upload_table()

    existing = get_document_upload(
        profile_id,
        scheme_id,
        document_name
    )

    # ----------------------------------------------------
    # Delete physical file
    # ----------------------------------------------------

    if existing:

        file_path = Path(
            existing[5]
        )

        if file_path.exists():

            try:
                file_path.unlink()
            except Exception:
                pass

    # ----------------------------------------------------
    # Delete database record
    # ----------------------------------------------------

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        DELETE FROM document_uploads
        WHERE profile_id = ?
        AND scheme_id = ?
        AND document_name = ?
    """, (
        profile_id,
        scheme_id,
        document_name
    ))

    conn.commit()
    conn.close()