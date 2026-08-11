import cv2
import os
import numpy as np

MODEL_PATH = "models/scrfd_500m.onnx"
ANNOTATION_FILE = "wider_face_val_bbx_gt.txt"
IMAGE_DIR = "images"

CONFIDENCE = 0.5
IOU_THRESHOLD = 0.5
INPUT_SIZE = 640

STRIDES = [8, 16, 32]
NUM_ANCHORS = 2


def calculate_iou(box1, box2):
    x1, y1, w1, h1 = box1
    x2, y2, w2, h2 = box2

    xa = max(x1, x2)
    ya = max(y1, y2)
    xb = min(x1 + w1, x2 + w2)
    yb = min(y1 + h1, y2 + h2)

    inter_w = max(0, xb - xa)
    inter_h = max(0, yb - ya)

    intersection = inter_w * inter_h

    union = (w1 * h1) + (w2 * h2) - intersection

    if union <= 0:
        return 0

    return intersection / union


def nms(boxes, scores, threshold=0.4):
    if len(boxes) == 0:
        return []

    boxes_xywh = np.array(boxes, dtype=np.float32)

    x1 = boxes_xywh[:, 0]
    y1 = boxes_xywh[:, 1]
    x2 = x1 + boxes_xywh[:, 2]
    y2 = y1 + boxes_xywh[:, 3]

    areas = (x2 - x1) * (y2 - y1)

    order = np.argsort(scores)[::-1]

    keep = []

    while len(order) > 0:
        i = order[0]
        keep.append(i)

        xx1 = np.maximum(x1[i], x1[order[1:]])
        yy1 = np.maximum(y1[i], y1[order[1:]])
        xx2 = np.minimum(x2[i], x2[order[1:]])
        yy2 = np.minimum(y2[i], y2[order[1:]])

        w = np.maximum(0, xx2 - xx1)
        h = np.maximum(0, yy2 - yy1)

        intersection = w * h

        union = areas[i] + areas[order[1:]] - intersection

        iou = np.divide(
            intersection,
            union,
            out=np.zeros_like(intersection),
            where=union > 0
        )

        remaining = np.where(iou <= threshold)[0]

        order = order[remaining + 1]

    return keep


# --------------------------------------------------
# Load model
# --------------------------------------------------

net = cv2.dnn.readNetFromONNX(MODEL_PATH)

print("SCRFD model loaded.")


# --------------------------------------------------
# SCRFD detection
# --------------------------------------------------

def detect_faces(image):

    original_h, original_w = image.shape[:2]

    # Resize while keeping aspect ratio
    scale = min(
        INPUT_SIZE / original_w,
        INPUT_SIZE / original_h
    )

    new_w = int(original_w * scale)
    new_h = int(original_h * scale)

    resized = cv2.resize(image, (new_w, new_h))

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

    net.setInput(blob)

    outputs = net.forward(
        net.getUnconnectedOutLayersNames()
    )

    # Outputs:
    # 0,1,2 = scores
    # 3,4,5 = bounding boxes
    # 6,7,8 = landmarks

    scores_outputs = outputs[0:3]
    bbox_outputs = outputs[3:6]

    boxes = []
    scores = []

    for level in range(3):

        stride = STRIDES[level]

        scores_level = scores_outputs[level].reshape(-1)
        bbox_level = bbox_outputs[level].reshape(-1, 4)

        feature_size = INPUT_SIZE // stride

        for index, score in enumerate(scores_level):

            if score < CONFIDENCE:
                continue

            # Two anchors per spatial location
            anchor_index = index % NUM_ANCHORS
            location_index = index // NUM_ANCHORS

            row = location_index // feature_size
            col = location_index % feature_size

            # Anchor center
            anchor_cx = (col + 0.5) * stride
            anchor_cy = (row + 0.5) * stride

            dx1, dy1, dx2, dy2 = bbox_level[index]

            # SCRFD box distances
            x1 = anchor_cx - dx1 * stride
            y1 = anchor_cy - dy1 * stride
            x2 = anchor_cx + dx2 * stride
            y2 = anchor_cy + dy2 * stride

            # Convert back to original image coordinates
            x1 /= scale
            y1 /= scale
            x2 /= scale
            y2 /= scale

            x1 = max(0, min(x1, original_w - 1))
            y1 = max(0, min(y1, original_h - 1))
            x2 = max(0, min(x2, original_w - 1))
            y2 = max(0, min(y2, original_h - 1))

            w = x2 - x1
            h = y2 - y1

            if w <= 0 or h <= 0:
                continue

            boxes.append([x1, y1, w, h])
            scores.append(float(score))

    # Remove duplicate detections
    keep = nms(boxes, scores, 0.4)

    return [
        boxes[i] + [scores[i]]
        for i in keep
    ]


# --------------------------------------------------
# Read WIDER FACE annotations
# --------------------------------------------------

with open(ANNOTATION_FILE, "r") as f:
    lines = [line.strip() for line in f.readlines()]

i = 0

true_positives = 0
false_positives = 0
false_negatives = 0

total_images = 0


# --------------------------------------------------
# Evaluate complete validation set
# --------------------------------------------------

while i < len(lines):

    image_name = lines[i]
    i += 1

    if not image_name:
        continue

    number_of_faces = int(lines[i])
    i += 1

    ground_truth = []

    for _ in range(number_of_faces):

        values = list(map(int, lines[i].split()))
        i += 1

        x, y, w, h = values[:4]

        # WIDER FACE invalid flag
        invalid = values[7]

        if invalid == 0:
            ground_truth.append([x, y, w, h])

    image_path = os.path.join(
        IMAGE_DIR,
        image_name.replace("/", os.sep)
    )

    image = cv2.imread(image_path)

    if image is None:
        print("Could not read:", image_path)
        continue

    predictions = detect_faces(image)

    matched_gt = set()

    for prediction in predictions:

        pred_box = prediction[:4]

        best_iou = 0
        best_gt = -1

        for gt_index, gt_box in enumerate(ground_truth):

            if gt_index in matched_gt:
                continue

            iou = calculate_iou(
                pred_box,
                gt_box
            )

            if iou > best_iou:
                best_iou = iou
                best_gt = gt_index

        if best_iou >= IOU_THRESHOLD:

            true_positives += 1
            matched_gt.add(best_gt)

        else:

            false_positives += 1

    false_negatives += (
        len(ground_truth) - len(matched_gt)
    )

    total_images += 1

    if total_images % 100 == 0:
        print(
            f"Processed {total_images} images..."
        )


# --------------------------------------------------
# Metrics
# --------------------------------------------------

precision = (
    true_positives /
    (true_positives + false_positives)
    if true_positives + false_positives > 0
    else 0
)

recall = (
    true_positives /
    (true_positives + false_negatives)
    if true_positives + false_negatives > 0
    else 0
)

f1 = (
    2 * precision * recall /
    (precision + recall)
    if precision + recall > 0
    else 0
)


print("\n========== SCRFD Evaluation ==========")

print("Images processed:", total_images)

print("True Positives:", true_positives)
print("False Positives:", false_positives)
print("False Negatives:", false_negatives)

print(f"\nPrecision: {precision:.4f}")
print(f"Recall:    {recall:.4f}")
print(f"F1 Score:  {f1:.4f}")

print("======================================")