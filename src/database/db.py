from src.database.config import supabase
# pyrefly: ignore [missing-import]
import bcrypt as bc
import random
import string
from datetime import datetime, timezone


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

# random and string imported at top

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
    """Delete a subject and all associated enrollments and attendance logs."""
    try:
        # Delete attendance logs for this subject first
        supabase.table('attendance_logs').delete().eq('subject_id', subject_id).execute()
        # Delete student enrollments
        supabase.table('subject_students').delete().eq('subject_id', subject_id).execute()
        # Finally delete the subject
        supabase.table('subjects').delete().eq('subject_id', subject_id).execute()
        return {"success": True, "message": "Subject and all related records deleted successfully."}
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

def check_duplicate_attendance(subject_id: int, date_str: str) -> bool:
    """Check if attendance has already been marked for a subject on a given date."""
    try:
        res = supabase.table('attendance_logs').select('timestamp').eq('subject_id', subject_id).execute()
        if res.data:
            for log in res.data:
                if log.get('timestamp', '')[:10] == date_str:
                    return True
        return False
    except Exception:
        return False


def mark_attendance(subject_id: int, results: dict) -> dict:
    """Mark attendance for a subject. Prevents duplicate attendance for the same day."""
    try:
        timestamp = datetime.now(timezone.utc).isoformat()
        today_str = timestamp[:10]

        # Check for duplicate attendance on the same day
        if check_duplicate_attendance(subject_id, today_str):
            return {
                "success": False,
                "message": "Attendance has already been marked for this subject today. Duplicate entries are not allowed."
            }

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


# ----------------------------
# DASHBOARD ANALYTICS
# ----------------------------

def get_teacher_dashboard_stats(teacher_id: int) -> dict:
    """Get aggregated dashboard statistics for a teacher."""
    try:
        # Get all subjects for this teacher
        subjects = get_teacher_subjects(teacher_id)
        total_subjects = len(subjects)

        # Get all unique enrolled students across all subjects
        all_student_ids = set()
        for sub in subjects:
            students = get_subject_students(sub['subject_id'])
            for s in students:
                all_student_ids.add(s.get('student_id'))
        total_students = len(all_student_ids)

        # Get today's sessions and overall attendance stats
        today_str = datetime.now(timezone.utc).strftime('%Y-%m-%d')
        sessions = get_teacher_attendance_sessions(teacher_id)

        sessions_today = 0
        total_present = 0
        total_records = 0

        for session in sessions:
            ts = session.get('timestamp', '')
            if ts[:10] == today_str:
                sessions_today += 1
            total_present += session.get('present', 0)
            total_records += session.get('present', 0) + session.get('absent', 0)

        avg_attendance = round((total_present / total_records * 100), 1) if total_records > 0 else 0

        return {
            "total_subjects": total_subjects,
            "total_students": total_students,
            "sessions_today": sessions_today,
            "avg_attendance": avg_attendance,
            "total_sessions": len(sessions),
            "total_present": total_present,
            "total_records": total_records
        }
    except Exception as e:
        print(f"Error fetching dashboard stats: {e}")
        return {
            "total_subjects": 0,
            "total_students": 0,
            "sessions_today": 0,
            "avg_attendance": 0,
            "total_sessions": 0,
            "total_present": 0,
            "total_records": 0
        }


def get_all_enrolled_students(teacher_id: int) -> list:
    """Get all students enrolled across all subjects for a teacher, with their biometric status."""
    try:
        subjects = get_teacher_subjects(teacher_id)
        student_map = {}  # student_id -> {name, subjects: [], has_face, has_voice}

        for sub in subjects:
            students = get_subject_students(sub['subject_id'])
            for s in students:
                sid = s.get('student_id')
                if sid not in student_map:
                    student_map[sid] = {
                        'student_id': sid,
                        'name': s.get('name', 'Unknown'),
                        'subjects': [],
                    }
                student_map[sid]['subjects'].append(sub.get('name', ''))

        # Fetch biometric status for all students
        if student_map:
            student_ids = list(student_map.keys())
            res = supabase.table('students').select(
                'student_id, face_embedding, voice_embedding'
            ).in_('student_id', student_ids).execute()

            if res.data:
                for record in res.data:
                    sid = record['student_id']
                    if sid in student_map:
                        student_map[sid]['has_face'] = bool(record.get('face_embedding'))
                        student_map[sid]['has_voice'] = bool(record.get('voice_embedding'))

        return list(student_map.values())
    except Exception as e:
        print(f"Error fetching enrolled students: {e}")
        return []


# ----------------------------
# EMAIL VERIFICATION
# ----------------------------

def generate_verification_token(length=32):
    """Generate a secure random verification token."""
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))


def set_user_verified(user_id: int) -> dict:
    """Mark a user as email-verified."""
    try:
        res = supabase.table('users').update({
            'is_verified': True,
            'verification_token': None
        }).eq('user_id', user_id).execute()
        if res.data:
            return {"success": True}
        return {"success": False, "message": "User not found."}
    except Exception as e:
        return {"success": False, "message": str(e)}


def create_pending_registration(token: str, name: str, email: str, password: str, role: str, face_embedding: list = None, voice_embedding: list = None) -> dict:
    if check_user_exists(email):
        return {"success": False, "message": "User already exists"}
        
    hashed = hash_password(password)
    
    try:
        res = supabase.table('pending_registrations').insert({
            "token": token,
            "name": name,
            "email": email,
            "password_hash": hashed,
            "role": role,
            "face_embedding": face_embedding,
            "voice_embedding": voice_embedding
        }).execute()
        return {"success": True, "message": "Pending registration created"}
    except Exception as e:
        return {"success": False, "message": f"Database error: {str(e)}"}

def verify_and_commit_registration(token: str) -> dict:
    """Look up a verification token in pending_registrations, create the user, and mark them as verified."""
    try:
        # Check pending registrations
        res = supabase.table('pending_registrations').select('*').eq('token', token).execute()
        if not res.data:
            return {"success": False, "message": "Invalid or expired verification token."}
            
        pending = res.data[0]
        email = pending['email']
        role = pending['role']
        
        # Make sure user doesn't exist
        if check_user_exists(email):
            # Cleanup pending
            supabase.table('pending_registrations').delete().eq('token', token).execute()
            return {"success": False, "message": "User already exists."}
            
        # 1. Create user in users table
        user_res = supabase.table('users').insert({
            "email": email,
            "password": pending['password_hash'],
            "role": role,
            "is_verified": True,
            "verification_token": None
        }).execute()
        
        if not user_res.data:
            return {"success": False, "message": "Failed to create user record."}
            
        user_id = user_res.data[0]["user_id"]
        
        # 2. Create role profile
        if role == "teacher":
            supabase.table('teachers').insert({
                "name": pending['name'],
                "user_id": user_id
            }).execute()
        elif role == "student":
            supabase.table('students').insert({
                "name": pending['name'],
                "user_id": user_id,
                "face_embedding": pending['face_embedding'],
                "voice_embedding": pending['voice_embedding']
            }).execute()
            
        # 3. Delete pending registration
        supabase.table('pending_registrations').delete().eq('token', token).execute()
        
        return {"success": True, "message": "Account created and verified successfully!"}
        
    except Exception as e:
        return {"success": False, "message": f"Database error: {str(e)}"}


def get_user_by_email(email: str) -> dict:
    """Fetch a user record by email."""
    try:
        res = supabase.table('users').select('*').eq('email', email).execute()
        return res.data[0] if res.data else None
    except Exception:
        return None


def update_verification_token(user_id: int, token: str) -> dict:
    """Update the verification token for a user (for resend)."""
    try:
        res = supabase.table('users').update({
            'verification_token': token
        }).eq('user_id', user_id).execute()
        return {"success": bool(res.data)}
    except Exception as e:
        return {"success": False, "message": str(e)}
