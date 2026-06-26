import dlib
import numpy as np
import face_recognition_models
from sklearn.svm import SVC
import streamlit as st
from src.database.db import get_all_students


@st.cache_resource
def load_dlib_models():
    """Load and cache the heavy dlib models (detector, shape predictor, face recognizer)."""
    detector = dlib.get_frontal_face_detector()
    sp = dlib.shape_predictor(
        face_recognition_models.pose_predictor_model_location()
    )
    facerec = dlib.face_recognition_model_v1(
        face_recognition_models.face_recognition_model_location()
    )
    return detector, sp, facerec


def get_face_embeddings(image_np):
    """Detect faces in an image and return their 128-d embeddings."""
    detector, sp, facerec = load_dlib_models()
    faces = detector(image_np, 1)

    encodings = []
    for face in faces:
        shape = sp(image_np, face)
        face_descriptor = facerec.compute_face_descriptor(image_np, shape, 1)
        encodings.append(np.array(face_descriptor))
    return encodings


# Use a separate cache key so we can clear ONLY the trained model
# without nuking the heavy dlib model cache.
_MODEL_CACHE_KEY = "attendx_face_model"


@st.cache_resource
def get_trained_model():
    """Train an SVM classifier on all registered student face embeddings."""
    X = []
    y = []

    students = get_all_students()

    if not students:
        return None

    for student in students:
        embeddings = student.get('face_embedding')
        if embeddings:
            X.append(np.array(embeddings))
            y.append(student.get('student_id'))

    if not X:
        return None

    unique_classes = list(set(y))

    # SVM requires at least 2 classes — if only 1 student is registered,
    # fall back to distance-based matching only (no classifier).
    if len(unique_classes) < 2:
        return {'clf': None, 'X': X, 'y': y}

    model = SVC(kernel='linear', probability=True, class_weight='balanced')
    model.fit(X, y)

    return {'clf': model, 'X': X, 'y': y}


def train_classifier():
    """Retrain the face classifier with latest student data.
    
    Only clears the trained model cache — does NOT clear the heavy dlib model cache.
    """
    # Clear only the trained model, not all cached resources
    get_trained_model.clear()
    model_data = get_trained_model()
    return bool(model_data)


def predict_attendance(class_image_np):
    """Run face recognition on a class image and return detected students.
    
    Returns:
        Tuple of (detected_students_dict, all_student_ids, face_count)
    """
    encodings = get_face_embeddings(class_image_np)
    model_data = get_trained_model()

    detected_students = {}

    if not model_data:
        return detected_students, [], len(encodings)

    clf = model_data['clf']
    X_train = model_data['X']
    y_train = model_data['y']

    all_students = sorted(list(set(y_train)))

    for encoding in encodings:
        if clf is not None and len(all_students) >= 2:
            predicted_id = int(clf.predict([encoding])[0])
        else:
            # Single-class fallback: compare against the only registered student
            predicted_id = all_students[0]

        student_embedding = X_train[y_train.index(predicted_id)]
        best_match_score = np.linalg.norm(encoding - student_embedding)

        if best_match_score <= 0.6:
            detected_students[predicted_id] = True

    return detected_students, all_students, len(encodings)
