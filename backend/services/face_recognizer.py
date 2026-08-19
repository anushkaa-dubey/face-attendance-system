import cv2
import numpy as np
import onnxruntime as ort
from typing import Optional
from backend.config import MOBILEFACENET_MODEL_PATH

class FaceRecognizer:
    def __init__(self, model_path: str = MOBILEFACENET_MODEL_PATH):
        self.model_path = model_path
        self.session = ort.InferenceSession(
            model_path,
            providers=["CPUExecutionProvider"]
        )
        self.input_name = self.session.get_inputs()[0].name

    def get_embedding(self, face_image: np.ndarray) -> Optional[np.ndarray]:
        """
        Generates a 512-D L2-normalized embedding for a cropped face image (BGR).
        """
        if face_image is None or face_image.size == 0:
            return None

        # ArcFace MobileFaceNet expects 112x112
        face = cv2.resize(
            face_image,
            (112, 112)
        )

        # BGR -> RGB
        face = cv2.cvtColor(
            face,
            cv2.COLOR_BGR2RGB
        )

        # float32
        face = face.astype(np.float32)

        # Preprocessing: (pixel - 127.5) / 127.5
        face = (face - 127.5) / 127.5

        # HWC -> CHW
        face = np.transpose(
            face,
            (2, 0, 1)
        )

        # Add batch dimension
        face = np.expand_dims(
            face,
            axis=0
        ).astype(np.float32)

        # Run model
        embedding = self.session.run(
            None,
            {self.input_name: face}
        )[0]

        # L2 normalization
        norm = np.linalg.norm(
            embedding,
            axis=1,
            keepdims=True
        )

        embedding = embedding / (norm + 1e-12)

        return embedding[0]

    @staticmethod
    def cosine_similarity(embedding1: np.ndarray, embedding2: np.ndarray) -> float:
        """
        Computes cosine similarity between two 512-D L2-normalized embeddings.
        """
        return float(
            np.dot(embedding1, embedding2) /
            (
                np.linalg.norm(embedding1) *
                np.linalg.norm(embedding2) + 1e-12
            )
        )
