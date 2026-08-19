# Face Attendance System - FastAPI Backend

FastAPI backend server for the React Native Face Attendance Application. It performs single-face detection via SCRFD, face feature extraction via ArcFace MobileFaceNet, cosine similarity matching against a pre-built recognition gallery, and SQLite-backed attendance logging.

---

## Model Files Location

The backend uses the following ONNX models located in the `models/` directory:

- **Face Detection:** `models/scrfd_500m.onnx` (SCRFD 500M)
- **Face Recognition / Embeddings:** `models/w600k_mbf.onnx` (MobileFaceNet with ArcFace weights)

---

## How the Gallery Works

1. **Initialization on Startup:**
   At backend startup, `Gallery.load_gallery()` scans the training dataset located at:
   `Recognition Dataset/Kaggle Indian Face Dataset/Image_Train/`
2. **Feature Extraction:**
   - Detects the face in each training image using SCRFD.
   - Extracts a 512-dimensional embedding using MobileFaceNet.
3. **Averaging & L2 Normalization:**
   - Averages all 512-D embeddings for each identity.
   - L2-normalizes the final averaged vector for each identity.
4. **In-Memory Caching:**
   - The resulting embeddings dictionary `{person_name: normalized_embedding}` is cached in memory.
   - **Note:** The gallery is loaded once during application startup and is **not** regenerated per request.

---

## 1. Installation

Ensure you have Python 3.9+ installed.

```bash
# Clone the repository (if applicable) and enter the directory
cd "Face Attendance"

# Create and activate a virtual environment
python -m venv .venv
# On Windows:
.venv\Scripts\activate
# On Linux/macOS:
source .venv/bin/activate

# Install required dependencies
pip install fastapi uvicorn python-multipart opencv-python numpy onnxruntime sqlalchemy
```

---

## 2. How to Start FastAPI Server

Run the following command from the project root directory:

```bash
uvicorn backend.main:app --reload
```

Or run via Python module:

```bash
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```

The server will start at `http://127.0.0.1:8000`. You can also access the interactive API docs at `http://127.0.0.1:8000/docs`.

---

## 3. API Endpoints Overview

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/health` | Server health check endpoint |
| `POST` | `/recognize` | Select/upload an image (`multipart/form-data`) to recognize person and auto-mark attendance |
| `POST` | `/attendance` | Manually record attendance for a recognized person |
| `GET` | `/attendance` | Fetch all logged attendance records |

---

## 4. Example Requests & Expected Responses

### A. Health Check (`GET /health`)

**Request (curl):**
```bash
curl -X GET http://127.0.0.1:8000/health
```

**Expected Response:**
```json
{
  "status": "ok"
}
```

---

### B. Recognize Face & Mark Attendance (`POST /recognize`)

**Request (curl):**
```bash
curl -X POST http://127.0.0.1:8000/recognize \
  -F "file=@Recognition Dataset/Kaggle Indian Face Dataset/Image_Test/Aditi/Aditi_15.jpeg"
```

**Expected Responses:**

- **Successful Match (First Time Today):**
  ```json
  {
    "recognized": true,
    "person": "Aditi",
    "similarity": 0.7184,
    "message": "Attendance marked"
  }
  ```

- **Successful Match (Repeated Today):**
  ```json
  {
    "recognized": true,
    "person": "Aditi",
    "similarity": 0.7184,
    "message": "Attendance already marked for today"
  }
  ```


- **No Face Detected:**
  ```json
  {
    "recognized": false,
    "person": null,
    "similarity": null,
    "message": "No face detected"
  }
  ```

- **Multiple Faces Detected:**
  ```json
  {
    "recognized": false,
    "person": null,
    "similarity": null,
    "message": "Multiple faces detected"
  }
  ```

- **Unknown / Unmatched Person (Below Threshold):**
  ```json
  {
    "recognized": false,
    "person": null,
    "similarity": 0.42,
    "message": "Unknown person"
  }
  ```

---

### C. Mark Attendance (`POST /attendance`)

**Request (curl):**
```bash
curl -X POST http://127.0.0.1:8000/attendance \
  -H "Content-Type: application/json" \
  -d '{"person": "Aditi"}'
```

**Expected Response:**
```json
{
  "id": 1,
  "person_name": "Aditi",
  "date": "2026-08-19",
  "time": "11:38:27",
  "status": "Present"
}
```

---

### D. Get Attendance Records (`GET /attendance`)

**Request (curl):**
```bash
curl -X GET http://127.0.0.1:8000/attendance
```

**Expected Response:**
```json
[
  {
    "id": 1,
    "person_name": "Aditi",
    "date": "2026-08-19",
    "time": "11:38:27",
    "status": "Present"
  }
]
```

---

## Configuration & Settings

You can tune recognition settings in `backend/config.py` or via environment variables:

- `FACE_RECOGNITION_THRESHOLD`: Default `0.5` (Cosine similarity threshold for gallery matching)
- `DETECTION_CONFIDENCE`: Default `0.5` (SCRFD face detection confidence cutoff)
- `TRAIN_DIR`: Dataset path for gallery construction
