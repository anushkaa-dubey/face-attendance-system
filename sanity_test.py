import cv2
import torch
import torch.nn.functional as F
import numpy as np
import onnxruntime as ort

from mobilefacenet_model import MobileFaceNet


# ============================================================
# PATHS
# ============================================================

MODEL_PATH = r".\models\mobilefacenet_model_best.pth"
SCRFD_PATH = r".\models\scrfd_500m.onnx"

ADITI = r".\Recognition Dataset\Kaggle Indian Face Dataset\Image_Test\Aditi\Aditi_15.jpeg"
ABHAY = r".\Recognition Dataset\Kaggle Indian Face Dataset\Image_Test\ABHAY\ABHAY_15.jpeg"


# ============================================================
# LOAD MOBILEFACENET
# ============================================================

model = MobileFaceNet()

checkpoint = torch.load(
    MODEL_PATH,
    map_location="cpu",
    weights_only=False
)

model.load_state_dict(checkpoint["state_dict"])

model.eval()

print("MobileFaceNet loaded.")


# ============================================================
# LOAD SCRFD
# ============================================================

session = ort.InferenceSession(
    SCRFD_PATH,
    providers=["CPUExecutionProvider"]
)

input_name = session.get_inputs()[0].name

print("SCRFD loaded.")


# ============================================================
# SCRFD DETECTION
# ============================================================

def detect_face(image_path):

    image = cv2.imread(image_path)

    if image is None:
        raise ValueError(f"Could not read image: {image_path}")

    h, w = image.shape[:2]

    INPUT_SIZE = 640
    STRIDES = [8, 16, 32]
    CONFIDENCE = 0.5

    # Same preprocessing used by our working SCRFD code
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

    outputs = session.run(
        None,
        {input_name: blob}
    )

    boxes = []
    scores = []

    # --------------------------------------------------------
    # Correct SCRFD decoding
    # --------------------------------------------------------

    for level, stride in enumerate(STRIDES):

        scores_out = outputs[level].reshape(-1)
        boxes_out = outputs[level + 3].reshape(-1, 4)

        feature_size = INPUT_SIZE // stride

        for i, score in enumerate(scores_out):

            if score < CONFIDENCE:
                continue

            # 2 anchors per location
            location = i // 2

            row = location // feature_size
            col = location % feature_size

            # Anchor center
            cx = col * stride
            cy = row * stride

            dx1, dy1, dx2, dy2 = boxes_out[i]

            x1 = cx - dx1 * stride
            y1 = cy - dy1 * stride
            x2 = cx + dx2 * stride
            y2 = cy + dy2 * stride

            # Convert back to original image coordinates
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
        raise ValueError(
            f"No face detected in {image_path}"
        )

    # --------------------------------------------------------
    # NMS
    # --------------------------------------------------------

    indices = cv2.dnn.NMSBoxes(
        boxes,
        scores,
        CONFIDENCE,
        0.4
    )

    if len(indices) == 0:
        raise ValueError(
            f"No face survived NMS in {image_path}"
        )

    # Pick highest-confidence detection
    best = max(
        indices.flatten(),
        key=lambda i: scores[i]
    )

    x, y, bw, bh = boxes[best]

    print("Detection score:", scores[best])
    print(
        "Face box:",
        x,
        y,
        bw,
        bh
    )

    # --------------------------------------------------------
    # Crop face
    # --------------------------------------------------------

    face = image[
        y:y + bh,
        x:x + bw
    ]

    if face.size == 0:
        raise ValueError(
            f"Empty face crop for {image_path}"
        )

    return face


# ============================================================
# GET MOBILEFACENET EMBEDDING
# ============================================================

def get_embedding(image_path):

    face = detect_face(image_path)

    # MobileFaceNet input = 112 x 112
    face = cv2.resize(
        face,
        (112, 112)
    )

    # BGR -> RGB
    face = cv2.cvtColor(
        face,
        cv2.COLOR_BGR2RGB
    )

    # Convert to tensor
    tensor = torch.from_numpy(
        face
    ).float()

    tensor = tensor.permute(
        2, 0, 1
    )

    tensor = tensor.unsqueeze(0)

    # ArcFace-style normalization
    tensor = (
        tensor - 127.5
    ) / 128.0

    # Generate embedding
    with torch.no_grad():

        embedding = model(
            tensor
        )

    # L2 normalize
    embedding = F.normalize(
        embedding,
        p=2,
        dim=1
    )

    return embedding


# ============================================================
# MAIN TEST
# ============================================================

print()
print("Generating embeddings...")

e_aditi = get_embedding(
    ADITI
)

print()

e_abhay = get_embedding(
    ABHAY
)


# ============================================================
# COSINE SIMILARITY
# ============================================================

same_similarity = F.cosine_similarity(
    e_aditi,
    e_aditi
).item()

different_similarity = F.cosine_similarity(
    e_aditi,
    e_abhay
).item()


# ============================================================
# RESULTS
# ============================================================

print()
print("==============================")
print("MobileFaceNet Sanity Test")
print("==============================")

print(
    "Embedding shape:",
    e_aditi.shape
)

print(
    "Embedding norm:",
    torch.norm(e_aditi).item()
)

print()

print(
    "Aditi vs Aditi :",
    same_similarity
)

print(
    "Aditi vs ABHAY :",
    different_similarity
)

print("==============================")