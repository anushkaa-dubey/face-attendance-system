import cv2
import numpy as np
import onnxruntime as ort
from typing import List, Dict, Any
from backend.config import (
    SCRFD_MODEL_PATH,
    INPUT_SIZE,
    STRIDES,
    DETECTION_CONFIDENCE,
    NMS_THRESHOLD
)

class FaceDetector:
    def __init__(self, model_path: str = SCRFD_MODEL_PATH):
        self.model_path = model_path
        self.session = ort.InferenceSession(
            model_path,
            providers=["CPUExecutionProvider"]
        )
        self.input_name = self.session.get_inputs()[0].name

    def detect_faces(self, image: np.ndarray) -> List[Dict[str, Any]]:
        """
        Detects faces in a BGR image using SCRFD.
        Returns a list of dicts containing face crops and metadata:
        [{'crop': ndarray, 'score': float, 'box': [x, y, w, h]}]
        """
        if image is None or image.size == 0:
            return []

        h, w = image.shape[:2]

        scale = min(
            INPUT_SIZE / w,
            INPUT_SIZE / h
        )

        new_w = int(w * scale)
        new_h = int(h * scale)

        resized = cv2.resize(
            image,
            (new_w, new_h)
        )

        canvas = np.zeros(
            (INPUT_SIZE, INPUT_SIZE, 3),
            dtype=np.uint8
        )

        canvas[:new_h, :new_w] = resized

        blob = cv2.dnn.blobFromImage(
            canvas,
            1.0 / 128.0,
            (INPUT_SIZE, INPUT_SIZE),
            (127.5, 127.5, 127.5),
            swapRB=True
        )

        outputs = self.session.run(
            None,
            {self.input_name: blob}
        )

        boxes = []
        scores = []

        for level, stride in enumerate(STRIDES):
            scores_out = outputs[level].reshape(-1)
            boxes_out = outputs[level + 3].reshape(-1, 4)

            feature_size = INPUT_SIZE // stride

            for i, score in enumerate(scores_out):
                if score < DETECTION_CONFIDENCE:
                    continue

                location = i // 2
                row = location // feature_size
                col = location % feature_size

                cx = col * stride
                cy = row * stride

                dx1, dy1, dx2, dy2 = boxes_out[i]

                x1 = cx - dx1 * stride
                y1 = cy - dy1 * stride
                x2 = cx + dx2 * stride
                y2 = cy + dy2 * stride

                x1 /= scale
                y1 /= scale
                x2 /= scale
                y2 /= scale

                x1 = int(max(0, x1))
                y1 = int(max(0, y1))
                x2 = int(min(w, x2))
                y2 = int(min(h, y2))

                if x2 <= x1 or y2 <= y1:
                    continue

                boxes.append([
                    x1,
                    y1,
                    x2 - x1,
                    y2 - y1
                ])
                scores.append(float(score))

        if not boxes:
            return []

        indices = cv2.dnn.NMSBoxes(
            boxes,
            scores,
            DETECTION_CONFIDENCE,
            NMS_THRESHOLD
        )

        if len(indices) == 0:
            return []

        flat_indices = np.array(indices).flatten()
        # Sort indices by score descending
        sorted_indices = sorted(flat_indices, key=lambda idx: scores[idx], reverse=True)

        faces = []
        for idx in sorted_indices:
            x, y, bw, bh = boxes[idx]
            face = image[y:y + bh, x:x + bw]
            if face.size > 0:
                faces.append({
                    "crop": face,
                    "score": scores[idx],
                    "box": [x, y, bw, bh]
                })

        return faces
