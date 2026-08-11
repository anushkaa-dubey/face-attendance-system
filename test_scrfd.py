import cv2
import numpy as np

MODEL_PATH = "models/scrfd_500m.onnx"
IMAGE_PATH = "images/0--Parade/0_Parade_marchingband_1_1004.jpg"

CONFIDENCE = 0.5
INPUT_SIZE = 640
STRIDES = [8, 16, 32]


net = cv2.dnn.readNetFromONNX(MODEL_PATH)

image = cv2.imread(IMAGE_PATH)

if image is None:
    print("Image not found")
    exit()

h, w = image.shape[:2]

scale = min(INPUT_SIZE / w, INPUT_SIZE / h)

new_w = int(w * scale)
new_h = int(h * scale)

resized = cv2.resize(image, (new_w, new_h))

canvas = np.zeros((INPUT_SIZE, INPUT_SIZE, 3), dtype=np.uint8)
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

boxes = []
scores = []

# First 3 outputs = scores
# Next 3 outputs = bounding boxes

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

        # SCRFD anchor center
        cx = col * stride
        cy = row * stride

        dx1, dy1, dx2, dy2 = boxes_out[i]

        x1 = cx - dx1 * stride
        y1 = cy - dy1 * stride
        x2 = cx + dx2 * stride
        y2 = cy + dy2 * stride

        # Back to original image coordinates
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

        boxes.append([x1, y1, x2 - x1, y2 - y1])
        scores.append(float(score))


# NMS
indices = cv2.dnn.NMSBoxes(
    boxes,
    scores,
    CONFIDENCE,
    0.4
)

count = 0

if len(indices) > 0:

    for index in indices.flatten():

        x, y, bw, bh = boxes[index]

        cv2.rectangle(
            image,
            (x, y),
            (x + bw, y + bh),
            (0, 255, 0),
            2
        )

        cv2.putText(
            image,
            f"{scores[index]:.2f}",
            (x, y - 5),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (0, 255, 0),
            1
        )

        count += 1


print("Faces detected:", count)

cv2.imwrite("scrfd_result.jpg", image)

print("Result saved as scrfd_result.jpg")