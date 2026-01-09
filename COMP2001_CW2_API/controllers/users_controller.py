# users_controller.py


from flask import abort, request
import random

from db import get_conn
from auth_client import verify_credentials

# function to check health
def health():
    """Simple health endpoint for quick checks."""
    return {"status": "OK"}, 200


# -----------------------------
# Helper functions
# -----------------------------
# Convert DB rows to dicts
def _rows_to_dicts(cursor, rows):
    """
    Convert DB rows to a list of dictionaries using cursor column names.
    """
    cols = [column[0] for column in cursor.description]
    return [dict(zip(cols, row)) for row in rows]


# Fetch roles for a user
def _fetch_roles_for_user(cursor, user_id: int):
    """
    Fetch role names for a given user id.
    """
    cursor.execute(
        """
        SELECT r.RoleName
        FROM CW2.UserRoles ur
        JOIN CW2.Roles r ON r.RoleID = ur.RoleID
        WHERE ur.UserID = ?
        ORDER BY r.RoleName
        """,
        user_id,
    )
    return [row[0] for row in cursor.fetchall()]

# Ensure user has at least one role
def _ensure_user_has_a_role(cursor, user_id: int):
    """
    If user already has roles -> return them.
    If not -> randomly assign one role and return it.
    """
    roles = _fetch_roles_for_user(cursor, user_id)
    if roles:
        return roles

    # If there are roles defined, randomly assign one to this user
    cursor.execute("SELECT RoleID, RoleName FROM CW2.Roles ORDER BY RoleID")
    all_roles = cursor.fetchall()
    if not all_roles:
        return []

    chosen = random.choice(all_roles)  # (RoleID, RoleName)
    cursor.execute(
        "INSERT INTO CW2.UserRoles (UserID, RoleID) VALUES (?, ?)",
        user_id,
        chosen[0],
    )
    return [chosen[1]]

# Ensure at least one Admin exists
def _ensure_at_least_one_admin(conn):
    """
    If no Admin exists in UserRoles, randomly promote one existing user to Admin.

    This prevents a situation where nobody can perform Admin-only operations.
    """
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT TOP 1 ur.UserID
        FROM CW2.UserRoles ur
        JOIN CW2.Roles r ON r.RoleID = ur.RoleID
        WHERE r.RoleName = 'Admin'
        """
    )
    if cursor.fetchone():
        return  # Admin already exists

    cursor.execute("SELECT RoleID FROM CW2.Roles WHERE RoleName='Admin'")
    admin_role = cursor.fetchone()
    if not admin_role:
        return

    admin_role_id = admin_role[0]

    cursor.execute("SELECT UserID FROM CW2.Users")
    user_ids = [row[0] for row in cursor.fetchall()]
    if not user_ids:
        return

    chosen_user = random.choice(user_ids)

    cursor.execute(
        """
        IF NOT EXISTS (SELECT 1 FROM CW2.UserRoles WHERE UserID=? AND RoleID=?)
        INSERT INTO CW2.UserRoles (UserID, RoleID) VALUES (?, ?)
        """,
        chosen_user,
        admin_role_id,
        chosen_user,
        admin_role_id,
    )

    conn.commit()

# Get user id by email
def _get_user_id_by_email(cursor, email: str):
    """
    Find the local CW2.Users user id for a given email.
    """
    cursor.execute("SELECT UserID FROM CW2.Users WHERE Email = ?", email)
    row = cursor.fetchone()
    return row[0] if row else None

# Require auth headers
def _require_auth_headers():
    """
    Read auth headers and validate they exist.
    """
    email = request.headers.get("X-Auth-Email")
    password = request.headers.get("X-Auth-Password")

    if not email or not password:
        abort(401, "Missing authentication headers: X-Auth-Email and X-Auth-Password")

    return email, password


# -----------------------------
# User endpoints
# -----------------------------
# List users endpoint
def list_users():
    """Return all users."""
    conn = get_conn()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM CW2.Users ORDER BY UserID")
        rows = cursor.fetchall()
        return _rows_to_dicts(cursor, rows), 200
    finally:
        conn.close()

# Get user by id endpoint
def get_user_by_id(user_id):
    """Return one user by id."""
    conn = get_conn()
    try:
        cursor = conn.cursor()
        cursor.execute("EXEC CW2.spUsers_ReadById ?", user_id)
        row = cursor.fetchone()

        if not row:
            abort(404, "User not found")

        return dict(zip([column[0] for column in cursor.description], row)), 200
    finally:
        conn.close()

# Get user by email endpoint
def get_user_by_email(email):
    """Return one user by email."""
    conn = get_conn()
    try:
        cursor = conn.cursor()
        cursor.execute("EXEC CW2.spUsers_ReadByEmail ?", email)
        row = cursor.fetchone()

        if not row:
            abort(404, "User not found")

        return dict(zip([column[0] for column in cursor.description], row)), 200
    finally:
        conn.close()

# Create user endpoint
def create_user(body):
    """Create a new user via stored procedure."""
    conn = get_conn()
    try:
        cursor = conn.cursor()

        cursor.execute(
            "EXEC CW2.spUsers_Create ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?",
            body["email"],
            body["firstName"],
            body["lastName"],
            body.get("phoneNumber"),
            body.get("aboutMe"),
            body.get("city"),
            body.get("country"),
            body.get("units"),
            body.get("activityPreference"),
            body.get("height"),
            body.get("weight"),
            body.get("dob"),
            body.get("language"),
        )

        row = cursor.fetchone()
        conn.commit()

        if not row:
            abort(500, "Create succeeded but no row returned")

        return dict(zip([column[0] for column in cursor.description], row)), 201

    except Exception as e:
        abort(409, str(e))
    finally:
        conn.close()

# Update user endpoint
def update_user(user_id, body):
    """Update an existing user via stored procedure."""
    conn = get_conn()
    try:
        cursor = conn.cursor()

        cursor.execute(
            "EXEC CW2.spUsers_Update ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?",
            user_id,
            body["email"],
            body["firstName"],
            body["lastName"],
            body.get("phoneNumber"),
            body.get("aboutMe"),
            body.get("city"),
            body.get("country"),
            body.get("units"),
            body.get("activityPreference"),
            body.get("height"),
            body.get("weight"),
            body.get("dob"),
            body.get("language"),
        )

        row = cursor.fetchone()
        conn.commit()

        if not row:
            abort(404, "User not found")

        return dict(zip([column[0] for column in cursor.description], row)), 200

    finally:
        conn.close()

# Delete user endpoint
def delete_user(user_id):
    """
    Admin-only delete.

    """
    auth_email, auth_password = _require_auth_headers()

    # Validate against authenticator
    if not verify_credentials(auth_email, auth_password):
        abort(401, "Invalid credentials (Authenticator rejected)")

    conn = get_conn()
    try:
        _ensure_at_least_one_admin(conn)

        cursor = conn.cursor()

        actor_id = _get_user_id_by_email(cursor, auth_email)
        if not actor_id:
            abort(403, "Authenticated user is not present in CW2.Users")

        actor_roles = _fetch_roles_for_user(cursor, actor_id)
        if "Admin" not in actor_roles:
            abort(403, "Forbidden: Admin role required")

        cursor.execute("EXEC CW2.spUsers_Delete ?", user_id)
        row = cursor.fetchone()
        conn.commit()

        if not row or row[0] == 0:
            abort(404, "User not found")

        return {"rowsDeleted": row[0]}, 200

    finally:
        conn.close()


# -----------------------------
# Roles endpoints
# -----------------------------
# List roles endpoint
def list_roles():
    """Return all available roles."""
    conn = get_conn()
    try:
        _ensure_at_least_one_admin(conn)
        cursor = conn.cursor()
        cursor.execute("SELECT RoleID, RoleName FROM CW2.Roles ORDER BY RoleID")
        rows = cursor.fetchall()
        return [{"roleId": r[0], "roleName": r[1]} for r in rows], 200
    finally:
        conn.close()

# Get user roles endpoint
def get_user_roles(user_id):
    """Return roles for a given user id (assign one randomly if user has none)."""
    conn = get_conn()
    try:
        _ensure_at_least_one_admin(conn)

        cursor = conn.cursor()

        cursor.execute("SELECT 1 FROM CW2.Users WHERE UserID = ?", user_id)
        if cursor.fetchone() is None:
            abort(404, "User not found")

        roles = _ensure_user_has_a_role(cursor, user_id)
        conn.commit()

        return {"userId": user_id, "roles": roles}, 200
    finally:
        conn.close()
