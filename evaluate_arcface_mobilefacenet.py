import os
import cv2
import numpy as np
import onnxruntime as ort


# ============================================================
# PATHS
# ============================================================

ARC_FACE_MODEL = r".\models\w600k_mbf.onnx"
SCRFD_MODEL = r".\models\scrfd_500m.onnx"

DATASET_ROOT = r".\Recognition Dataset\Kaggle Indian Face Dataset"

TRAIN_DIR = os.path.join(DATASET_ROOT, "Image_Train")
TEST_DIR = os.path.join(DATASET_ROOT, "Image_Test")


# ============================================================
# SETTINGS
# ============================================================

INPUT_SIZE = 640
STRIDES = [8, 16, 32]
DETECTION_CONFIDENCE = 0.5


# ============================================================
# LOAD MODELS
# ============================================================

arcface = ort.InferenceSession(
    ARC_FACE_MODEL,
    providers=["CPUExecutionProvider"]
)

scrfd = ort.InferenceSession(
    SCRFD_MODEL,
    providers=["CPUExecutionProvider"]
)

arcface_input = arcface.get_inputs()[0].name
scrfd_input = scrfd.get_inputs()[0].name

print("ArcFace MobileFaceNet loaded.")
print("SCRFD loaded.")


# ============================================================
# SCRFD DETECTION
# ============================================================

def detect_face(image_path):

    image = cv2.imread(image_path)

    if image is None:
        return None

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

    # IMPORTANT: same preprocessing that worked
    # with our corrected SCRFD pipeline
    blob = cv2.dnn.blobFromImage(
        canvas,
        1.0 / 128.0,
        (INPUT_SIZE, INPUT_SIZE),
        (127.5, 127.5, 127.5),
        swapRB=True
    )

    outputs = scrfd.run(
        None,
        {scrfd_input: blob}
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
        return None

    indices = cv2.dnn.NMSBoxes(
        boxes,
        scores,
        DETECTION_CONFIDENCE,
        0.4
    )

    if len(indices) == 0:
        return None

    # Pick highest-confidence face
    best = max(
        indices.flatten(),
        key=lambda i: scores[i]
    )

    x, y, bw, bh = boxes[best]

    face = image[
        y:y + bh,
        x:x + bw
    ]

    if face.size == 0:
        return None

    return face


# ============================================================
# ARC FACE EMBEDDING
# ============================================================

def get_embedding(image_path):

    face = detect_face(image_path)

    if face is None:
        return None

    # ArcFace MobileFaceNet expects 112x112
    face = cv2.resize(
        face,
        (112, 112)
    )

    # BGR -> RGB
    face = cv2.cvtColor(
        face,
        cv2.COLOR_BGR2RGB
    )

    # uint8 -> float32
    face = face.astype(np.float32)

    # ArcFace preprocessing
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

    embedding = arcface.run(
        None,
        {arcface_input: face}
    )[0]

    # L2 normalization
    norm = np.linalg.norm(
        embedding,
        axis=1,
        keepdims=True
    )

    embedding = embedding / (
        norm + 1e-12
    )

    return embedding[0]


# ============================================================
# COSINE SIMILARITY
# ============================================================

def cosine_similarity(a, b):

    return float(
        np.dot(a, b) /
        (
            np.linalg.norm(a) *
            np.linalg.norm(b)
            + 1e-12
        )
    )


# ============================================================
# BUILD GALLERY
# ============================================================

print()
print("Building gallery...")

gallery = {}

gallery_images = 0
gallery_skipped = 0

for person in sorted(os.listdir(TRAIN_DIR)):

    person_dir = os.path.join(
        TRAIN_DIR,
        person
    )

    if not os.path.isdir(person_dir):
        continue

    embeddings = []

    for filename in sorted(
        os.listdir(person_dir)
    ):

        image_path = os.path.join(
            person_dir,
            filename
        )

        embedding = get_embedding(
            image_path
        )

        if embedding is None:

            gallery_skipped += 1
            continue

        embeddings.append(
            embedding
        )

        gallery_images += 1

    if embeddings:

        # Average training embeddings
        person_embedding = np.mean(
            embeddings,
            axis=0
        )

        # Normalize averaged embedding
        person_embedding = (
            person_embedding /
            (
                np.linalg.norm(
                    person_embedding
                ) + 1e-12
            )
        )

        gallery[person] = person_embedding


print()
print("Gallery identities :", len(gallery))
print("Gallery images     :", gallery_images)
print("Gallery skipped    :", gallery_skipped)


# ============================================================
# TEST
# ============================================================

print()
print("Testing...")

correct = 0
incorrect = 0
skipped = 0

total_similarity = 0.0
tested = 0


for person in sorted(
    os.listdir(TEST_DIR)
):

    person_dir = os.path.join(
        TEST_DIR,
        person
    )

    if not os.path.isdir(person_dir):
        continue

    if person not in gallery:
        continue

    for filename in sorted(
        os.listdir(person_dir)
    ):

        image_path = os.path.join(
            person_dir,
            filename
        )

        embedding = get_embedding(
            image_path
        )

        if embedding is None:

            skipped += 1
            continue

        best_person = None
        best_score = -1.0

        for identity, gallery_embedding in gallery.items():

            score = cosine_similarity(
                embedding,
                gallery_embedding
            )

            if score > best_score:

                best_score = score
                best_person = identity

        tested += 1
        total_similarity += best_score

        if best_person == person:

            correct += 1

        else:

            incorrect += 1

            print(
                f"WRONG: {filename} | "
                f"Actual: {person} | "
                f"Predicted: {best_person} | "
                f"Score: {best_score:.4f}"
            )


# ============================================================
# RESULTS
# ============================================================

accuracy = (
    correct / tested * 100
    if tested > 0
    else 0
)

average_similarity = (
    total_similarity / tested
    if tested > 0
    else 0
)


print()
print("========================================")
print("ArcFace MobileFaceNet Results")
print("========================================")

print(
    "Gallery identities :",
    len(gallery)
)

print(
    "Test images tested  :",
    tested
)

print(
    "Correct             :",
    correct
)

print(
    "Incorrect           :",
    incorrect
)

print(
    "Skipped             :",
    skipped
)

print(
    f"Accuracy            : {accuracy:.2f}%"
)

print(
    f"Average similarity  : {average_similarity:.4f}"
)

print("========================================")