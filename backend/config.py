import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Model Paths
SCRFD_MODEL_PATH = os.getenv(
    "SCRFD_MODEL_PATH",
    os.path.join(BASE_DIR, "models", "scrfd_500m.onnx")
)
MOBILEFACENET_MODEL_PATH = os.getenv(
    "MOBILEFACENET_MODEL_PATH",
    os.path.join(BASE_DIR, "models", "w600k_mbf.onnx")
)

# Dataset Path
TRAIN_DIR = os.getenv(
    "TRAIN_DIR",
    os.path.join(BASE_DIR, "Recognition Dataset", "Kaggle Indian Face Dataset", "Image_Train")
)

# SCRFD Parameters
INPUT_SIZE = 640
STRIDES = [8, 16, 32]
DETECTION_CONFIDENCE = float(os.getenv("DETECTION_CONFIDENCE", "0.5"))
NMS_THRESHOLD = 0.4

# Face Recognition Settings
FACE_RECOGNITION_THRESHOLD = float(os.getenv("FACE_RECOGNITION_THRESHOLD", "0.5"))

# Database Path
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    f"sqlite:///{os.path.join(BASE_DIR, 'attendance.db')}"
)
