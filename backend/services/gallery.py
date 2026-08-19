import os
import cv2
import numpy as np
import logging
from typing import Dict, Optional, Tuple
from backend.config import TRAIN_DIR, FACE_RECOGNITION_THRESHOLD
from backend.services.face_detector import FaceDetector
from backend.services.face_recognizer import FaceRecognizer

logger = logging.getLogger(__name__)

class Gallery:
    def __init__(self, face_detector: FaceDetector, face_recognizer: FaceRecognizer):
        self.face_detector = face_detector
        self.face_recognizer = face_recognizer
        self.gallery_embeddings: Dict[str, np.ndarray] = {}

    def load_gallery(self, train_dir: str = TRAIN_DIR) -> int:
        """
        Scans train_dir, generates 512-D embeddings per identity, averages & normalizes them,
        and stores them in memory.
        """
        logger.info(f"Building gallery from: {train_dir}")
        if not os.path.exists(train_dir):
            logger.warning(f"Train dataset directory not found: {train_dir}")
            return 0

        gallery = {}
        gallery_images = 0
        gallery_skipped = 0

        for person in sorted(os.listdir(train_dir)):
            person_dir = os.path.join(train_dir, person)
            if not os.path.isdir(person_dir):
                continue

            embeddings = []

            for filename in sorted(os.listdir(person_dir)):
                image_path = os.path.join(person_dir, filename)
                image = cv2.imread(image_path)
                if image is None:
                    gallery_skipped += 1
                    continue

                faces = self.face_detector.detect_faces(image)
                if not faces:
                    gallery_skipped += 1
                    continue

                best_face = faces[0]["crop"]
                emb = self.face_recognizer.get_embedding(best_face)
                if emb is not None:
                    embeddings.append(emb)
                    gallery_images += 1
                else:
                    gallery_skipped += 1

            if embeddings:
                # Average training embeddings
                person_embedding = np.mean(embeddings, axis=0)
                # L2 normalize averaged embedding
                person_embedding = person_embedding / (
                    np.linalg.norm(person_embedding) + 1e-12
                )
                gallery[person] = person_embedding

        self.gallery_embeddings = gallery
        logger.info(f"Gallery loaded successfully with {len(gallery)} identities ({gallery_images} images processed, {gallery_skipped} skipped).")
        return len(gallery)

    def recognize(
        self,
        query_embedding: np.ndarray,
        threshold: float = FACE_RECOGNITION_THRESHOLD
    ) -> Tuple[bool, Optional[str], float]:
        """
        Compares query_embedding against all gallery embeddings using cosine similarity.
        Returns: (is_recognized, person_name, similarity_score)
        """
        if not self.gallery_embeddings or query_embedding is None:
            return False, None, 0.0

        best_person = None
        best_similarity = -1.0

        for person, gallery_emb in self.gallery_embeddings.items():
            similarity = self.face_recognizer.cosine_similarity(query_embedding, gallery_emb)
            if similarity > best_similarity:
                best_similarity = similarity
                best_person = person

        if best_similarity >= threshold:
            return True, best_person, round(float(best_similarity), 4)
        else:
            return False, None, round(float(best_similarity), 4)
