import cv2
import os

MODEL_PATH = "models/face_detection_yunet_2026may.onnx"
ANNOTATION_FILE = "wider_face_val_bbx_gt.txt"
IMAGE_DIR = "images"

CONFIDENCE = 0.3
IOU_THRESHOLD = 0.5


def calculate_iou(box1, box2):
    x1, y1, w1, h1 = box1
    x2, y2, w2, h2 = box2

    xa = max(x1, x2)
    ya = max(y1, y2)
    xb = min(x1 + w1, x2 + w2)
    yb = min(y1 + h1, y2 + h2)

    intersection_w = max(0, xb - xa)
    intersection_h = max(0, yb - ya)

    intersection = intersection_w * intersection_h

    area1 = w1 * h1
    area2 = w2 * h2

    union = area1 + area2 - intersection

    if union == 0:
        return 0

    return intersection / union


# Load YuNet
detector = cv2.FaceDetectorYN.create(
    MODEL_PATH,
    "",
    (320, 320),
    CONFIDENCE,
    0.3,
    5000
)


# Read WIDER FACE annotations
with open(ANNOTATION_FILE, "r") as f:
    lines = [line.strip() for line in f.readlines()]

i = 0

true_positives = 0
false_positives = 0
false_negatives = 0

total_images = 0

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

        # Ignore invalid ground-truth annotations
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

    height, width = image.shape[:2]

    detector.setInputSize((width, height))

    _, faces = detector.detect(image)

    predictions = []

    if faces is not None:
        for face in faces:
            x, y, w, h = face[:4]
            score = face[-1]

            predictions.append(
                [x, y, w, h, score]
            )

    # Match predictions with ground truth
    matched_gt = set()

    for prediction in predictions:

        pred_box = prediction[:4]

        best_iou = 0
        best_gt = -1

        for gt_index, gt_box in enumerate(ground_truth):

            if gt_index in matched_gt:
                continue

            iou = calculate_iou(pred_box, gt_box)

            if iou > best_iou:
                best_iou = iou
                best_gt = gt_index

        if best_iou >= IOU_THRESHOLD:
            true_positives += 1
            matched_gt.add(best_gt)
        else:
            false_positives += 1

    false_negatives += len(ground_truth) - len(matched_gt)

    total_images += 1

    if total_images % 100 == 0:
        print(f"Processed {total_images} images...")


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


print("\n========== YuNet Evaluation ==========")
print("Images processed:", total_images)
print("True Positives:", true_positives)
print("False Positives:", false_positives)
print("False Negatives:", false_negatives)

print(f"\nPrecision: {precision:.4f}")
print(f"Recall:    {recall:.4f}")
print(f"F1 Score:  {f1:.4f}")
print("======================================")