import os
from dotenv import load_dotenv

# Load env variables since the other script failed due to missing SUPABASE_KEY
load_dotenv()

from src.database.db import supabase

try:
    print("Testing basic query:")
    res1 = supabase.table('subject_students').select('*').execute()
    print("All subject_students:", res1.data)
    
    if res1.data:
        subj_id = res1.data[0]['subject_id']
        print(f"\nTesting complex query for subject_id {subj_id}:")
        res2 = supabase.table('subject_students').select('student_id, students(student_id, users(name))').eq('subject_id', subj_id).execute()
        print("Complex query result:", res2.data)
        
except Exception as e:
    print(f"Exception: {e}")
