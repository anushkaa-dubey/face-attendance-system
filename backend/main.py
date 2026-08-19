import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.database.database import engine, Base
from backend.services.face_detector import FaceDetector
from backend.services.face_recognizer import FaceRecognizer
from backend.services.gallery import Gallery
from backend.routes import recognition, attendance

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("backend.main")

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing database tables...")
    Base.metadata.create_all(bind=engine)

    logger.info("Loading AI models and gallery...")
    detector = FaceDetector()
    recognizer = FaceRecognizer()
    gallery = Gallery(detector, recognizer)
    gallery.load_gallery()

    app.state.face_detector = detector
    app.state.face_recognizer = recognizer
    app.state.gallery = gallery

    logger.info("Backend startup complete.")
    yield

app = FastAPI(
    title="Face Attendance Backend",
    version="1.0.0",
    lifespan=lifespan
)

# Enable CORS for React Native & Web clients
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health_check():
    return {"status": "ok"}

app.include_router(recognition.router)
app.include_router(attendance.router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
