from src.database.config import supabase
# pyrefly: ignore [missing-import]
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


# ----------------------------
# UPDATE STUDENT EMBEDDINGS
# ----------------------------

def update_student_embeddings(student_id: int, face_embedding: list = None, voice_embedding: list = None) -> dict:
    """Update face and/or voice embeddings for a student."""
    update_data = {}
    if face_embedding is not None:
        update_data['face_embedding'] = face_embedding
    if voice_embedding is not None:
        update_data['voice_embedding'] = voice_embedding

    if not update_data:
        return {"success": False, "message": "No embedding data provided."}

    try:
        res = supabase.table('students').update(update_data).eq('student_id', student_id).execute()
        if not res.data:
            return {"success": False, "message": "Failed to update embeddings."}
        return {"success": True, "student": res.data[0]}
    except Exception as e:
        return {"success": False, "message": f"Database error: {str(e)}"}


def check_face_exists(new_embedding: list, threshold: float = 0.6) -> dict:
    """Check if a face embedding already exists in the database.
    Returns the matching student if found, None otherwise."""
    import numpy as np
    students = get_all_students()
    if not students:
        return {"exists": False, "student": None}

    for student in students:
        stored = student.get('face_embedding')
        if stored:
            distance = np.linalg.norm(np.array(new_embedding) - np.array(stored))
            if distance <= threshold:
                return {"exists": True, "student": student}

    return {"exists": False, "student": None}


# ----------------------------
# TEACHER DASHBOARD - SUBJECTS & ATTENDANCE
# ----------------------------

import random
import string

def generate_join_code(length=6):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

def create_subject(subject_code: str, name: str, section: str, teacher_id: int) -> dict:
    if not subject_code or not name or not section:
        return {"success": False, "message": "Subject code, name, and section cannot be empty."}
        
    try:
        existing = supabase.table('subjects').select('*').eq('subject_code', subject_code).eq('section', section).execute()
        if existing.data:
            return {"success": False, "message": f"Subject with code '{subject_code}' and section '{section}' already exists."}
            
        max_retries = 5
        join_code = None
        for _ in range(max_retries):
            code = generate_join_code()
            check = supabase.table('subjects').select('join_code').eq('join_code', code).execute()
            if not check.data:
                join_code = code
                break
                
        if not join_code:
            return {"success": False, "message": "Failed to generate unique join code. Please try again."}
            
        res = supabase.table('subjects').insert({
            "subject_code": subject_code,
            "name": name,
            "section": section,
            "teacher_id": teacher_id,
            "join_code": join_code
        }).execute()
        
        if not res.data:
            return {"success": False, "message": "Failed to create subject."}
            
        return {"success": True, "data": res.data[0], "message": "Subject created successfully."}
    except Exception as e:
        return {"success": False, "message": f"Database error: {str(e)}"}

def get_teacher_subjects(teacher_id: int) -> list:
    try:
        res = supabase.table('subjects').select('*').eq('teacher_id', teacher_id).execute()
        return res.data if res.data else []
    except Exception as e:
        print(f"Error fetching subjects: {e}")
        return []

def delete_subject(subject_id: int) -> dict:
    try:
        res = supabase.table('subjects').delete().eq('subject_id', subject_id).execute()
        return {"success": True, "message": "Subject deleted successfully."}
    except Exception as e:
        return {"success": False, "message": f"Failed to delete subject: {str(e)}"}

def get_subject_students(subject_id: int) -> list:
    try:
        res = supabase.table('subject_students').select(
            'student_id, students(student_id, name)'
        ).eq('subject_id', subject_id).execute()

        if res.data:
            students = []
            for record in res.data:
                student = record.get("students", {})
                students.append({
                    "student_id": student.get("student_id"),
                    "name": student.get("name", "Unknown")
                })
            return students

        return []

    except Exception as e:
        print(f"Error fetching subject students: {e}")
        return []

def get_subject_class_count(subject_id: int) -> int:
    try:
        res = supabase.table('attendance_logs').select('timestamp').eq('subject_id', subject_id).execute()
        if not res.data:
            return 0
        # Count unique days
        days = set([log['timestamp'][:10] for log in res.data if log.get('timestamp')])
        return len(days)
    except Exception as e:
        print(f"Error fetching class count: {e}")
        return 0

def mark_attendance(subject_id: int, results: dict) -> dict:
    from datetime import datetime
    try:
        timestamp = datetime.utcnow().isoformat()
        records = []
        for student_id, is_present in results.items():
            records.append({
                "subject_id": subject_id,
                "student_id": student_id,
                "timestamp": timestamp,
                "is_present": is_present
            })
        
        if records:
            res = supabase.table('attendance_logs').insert(records).execute()
            if not res.data:
                return {"success": False, "message": "Failed to save attendance logs."}
        return {"success": True, "message": "Attendance marked successfully."}
    except Exception as e:
        return {"success": False, "message": f"Database error: {str(e)}"}

def get_teacher_attendance_logs(teacher_id: int) -> list:
    try:
        res = supabase.table('attendance_logs').select(
        'timestamp, is_present, student_id, subjects!inner(name, teacher_id), students(name)'
        ).eq('subjects.teacher_id', teacher_id).execute()
        
        if not res.data:
            return []
            
        logs = []
        for log in res.data:
            student_name = "Unknown"
            if log.get('students'):
                student_name = log['students'].get('name', 'Unknown')
                
            logs.append({
                "subject_name": log['subjects']['name'],
                "student": f"{student_name} (ID: {log['student_id']})",
                "timestamp": log['timestamp'],
                "is_present": "Present" if log['is_present'] else "Absent"
            })
        return logs
    except Exception as e:
        print(f"Error fetching attendance logs: {e}")
        return []

# ----------------------------
# STUDENT DASHBOARD - SUBJECTS & ATTENDANCE
# ----------------------------

def get_subject_by_join_code(join_code: str):
    try:
        res = supabase.table('subjects').select('*').eq('join_code', join_code).execute()
        return res.data[0] if res.data else None
    except Exception as e:
        print(f"Error fetching subject by join code: {e}")
        return None

def get_student_subjects(student_id: int) -> list:
    try:
        res = supabase.table('subject_students').select('subjects(*)').eq('student_id', student_id).execute()
        if res.data:
            return [record['subjects'] for record in res.data if record.get('subjects')]
        return []
    except Exception as e:
        print(f"Error fetching student subjects: {e}")
        return []

def join_subject(student_id: int, join_code: str) -> dict:
    if not join_code:
        return {"success": False, "message": "Join code is required."}
    try:
        subject_res = supabase.table('subjects').select('*').eq('join_code', join_code).execute()
        if not subject_res.data:
            return {"success": False, "message": "Invalid join code."}
        
        subject_id = subject_res.data[0]['subject_id']
        
        existing = supabase.table('subject_students').select('*').eq('student_id', student_id).eq('subject_id', subject_id).execute()
        if existing.data:
            return {"success": False, "message": "You are already enrolled in this subject."}
            
        join_res = supabase.table('subject_students').insert({
            "student_id": student_id,
            "subject_id": subject_id
        }).execute()
        
        if not join_res.data:
            return {"success": False, "message": "Failed to join subject."}
            
        return {"success": True, "message": "Successfully joined the subject!"}
    except Exception as e:
        return {"success": False, "message": f"Database error: {str(e)}"}

def leave_subject(student_id: int, subject_id: int) -> dict:
    try:
        res = supabase.table('subject_students').delete().eq('student_id', student_id).eq('subject_id', subject_id).execute()
        return {"success": True, "message": "Successfully left the subject."}
    except Exception as e:
        return {"success": False, "message": f"Failed to leave subject: {str(e)}"}

def get_student_attendance(student_id: int) -> list:
    try:
        res = supabase.table('attendance_logs').select(
            'timestamp, is_present, subjects!inner(name, section)'
        ).eq('student_id', student_id).execute()
        
        if not res.data:
            return []
            
        logs = []
        for log in res.data:
            logs.append({
                "subject_name": log['subjects']['name'],
                "section": log['subjects']['section'],
                "timestamp": log['timestamp'],
                "is_present": "Present" if log['is_present'] else "Absent"
            })
        return logs
    except Exception as e:
        print(f"Error fetching attendance logs: {e}")
        return []


# ----------------------------
# GROUPED ATTENDANCE SESSIONS
# ----------------------------

def get_teacher_attendance_sessions(teacher_id: int) -> list:
    """Get attendance logs grouped by session (timestamp) for a teacher."""
    try:
        res = supabase.table('attendance_logs').select(
            'timestamp, is_present, student_id, subjects!inner(name, section, teacher_id), students(name)'
        ).eq('subjects.teacher_id', teacher_id).execute()
        
        if not res.data:
            return []
        
        # Group by timestamp
        sessions = {}
        for log in res.data:
            timestamp = log['timestamp']
            if timestamp not in sessions:
                sessions[timestamp] = {
                    "timestamp": timestamp,
                    "date": timestamp[:10],
                    "subject_name": log['subjects']['name'],
                    "section": log['subjects']['section'],
                    "present": 0,
                    "absent": 0,
                    "records": []
                }
            
            student_name = "Unknown"
            if log.get('students'):
                student_name = log['students'].get('name', 'Unknown')
            
            sessions[timestamp]["records"].append({
                "student_id": log['student_id'],
                "student_name": student_name,
                "is_present": log['is_present']
            })
            
            if log['is_present']:
                sessions[timestamp]["present"] += 1
            else:
                sessions[timestamp]["absent"] += 1
        
        # Convert to list and sort by timestamp descending
        session_list = list(sessions.values())
        session_list.sort(key=lambda x: x['timestamp'], reverse=True)
        return session_list
        
    except Exception as e:
        print(f"Error fetching attendance sessions: {e}")
        return []


def get_session_details(teacher_id: int, timestamp: str) -> dict:
    """Get detailed records for a specific attendance session."""
    try:
        res = supabase.table('attendance_logs').select(
            'timestamp, is_present, student_id, subjects!inner(name, section, teacher_id), students(name)'
        ).eq('subjects.teacher_id', teacher_id).eq('timestamp', timestamp).execute()
        
        if not res.data:
            return None
        
        session = {
            "timestamp": timestamp,
            "date": timestamp[:10],
            "subject_name": res.data[0]['subjects']['name'],
            "section": res.data[0]['subjects']['section'],
            "present": 0,
            "absent": 0,
            "records": []
        }
        
        for log in res.data:
            student_name = "Unknown"
            if log.get('students'):
                student_name = log['students'].get('name', 'Unknown')
            
            session["records"].append({
                "student_id": log['student_id'],
                "student_name": student_name,
                "is_present": log['is_present']
            })
            
            if log['is_present']:
                session["present"] += 1
            else:
                session["absent"] += 1
        
        # Sort by present first
        session["records"].sort(key=lambda x: x['is_present'], reverse=True)
        return session
        
    except Exception as e:
        print(f"Error fetching session details: {e}")
        return None
