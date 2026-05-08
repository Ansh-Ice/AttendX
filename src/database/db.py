from src.database.config import supabase
import bcrypt as bc


# ----------------------------
# USER HELPERS
# ----------------------------

def check_user_exists(email: str) -> bool:
    res = supabase.table('users').select('user_id').eq('email', email).execute()
    return len(res.data) > 0


def hash_password(password: str) -> str:
    return bc.hashpw(password.encode(), bc.gensalt()).decode()


def verify_password(password: str, hashed: str) -> bool:
    return bc.checkpw(password.encode(), hashed.encode())


# ----------------------------
# CREATE USERS
# ----------------------------

def create_user(email: str, password: str, role: str) -> dict:
    if check_user_exists(email):
        return {"success": False, "message": "User already exists"}

    hashed = hash_password(password)

    res = supabase.table('users').insert({
        "email": email,
        "password": hashed,
        "role": role
    }).execute()

    if not res.data:
        return {"success": False, "message": "User creation failed"}

    return {"success": True, "user": res.data[0]}


# ----------------------------
# CREATE TEACHER
# ----------------------------

def create_teacher(name: str, email: str, password: str) -> dict:
    user_res = create_user(email, password, "teacher")

    if not user_res["success"]:
        return user_res

    user_id = user_res["user"]["user_id"]

    res = supabase.table('teachers').insert({
        "name": name,
        "user_id": user_id
    }).execute()

    if not res.data:
        return {"success": False, "message": "Teacher creation failed"}

    return {"success": True, "teacher": res.data[0]}


# ----------------------------
# CREATE STUDENT (WITH LOGIN)
# ----------------------------

def create_student(name: str, email: str, password: str) -> dict:
    user_res = create_user(email, password, "student")

    if not user_res["success"]:
        return user_res

    user_id = user_res["user"]["user_id"]

    res = supabase.table('students').insert({
        "name": name,
        "user_id": user_id
    }).execute()

    if not res.data:
        return {"success": False, "message": "Student creation failed"}

    return {"success": True, "student": res.data[0]}


# ----------------------------
# LOGIN (UNIFIED)
# ----------------------------

def login_user(email: str, password: str) -> dict:
    res = supabase.table('users').select('*').eq('email', email).execute()

    if not res.data:
        return {"success": False, "message": "User not found"}

    user = res.data[0]

    if not verify_password(password, user['password']):
        return {"success": False, "message": "Invalid password"}

    return {
        "success": True,
        "user_id": user["user_id"],
        "role": user["role"]
    }


# ----------------------------
# GET PROFILE DATA
# ----------------------------

def get_teacher_by_user_id(user_id: int) -> dict:
    res = supabase.table('teachers').select('*').eq('user_id', user_id).execute()
    return res.data[0] if res.data else None


def get_student_by_user_id(user_id: int) -> dict:
    res = supabase.table('students').select('*').eq('user_id', user_id).execute()
    return res.data[0] if res.data else None


# ----------------------------
# OPTIONAL: ADMIN CREATION
# ----------------------------

def create_admin(email: str, password: str) -> dict:
    return create_user(email, password, "admin")

def get_all_students():
    res = supabase.table('students').select('*').execute()
    return res.data