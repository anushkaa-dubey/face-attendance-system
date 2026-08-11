import cv2
import os

MODEL_PATH = "models/face_detection_yunet_2026may.onnx"
IMAGE_PATH = "images/0--Parade/0_Parade_marchingband_1_1004.jpg"
detector = cv2.FaceDetectorYN.create(
    MODEL_PATH,
    "",
    (320, 320),
    0.8,
    0.3,
    5000
)

image = cv2.imread(IMAGE_PATH)

if image is None:
    print("Image not found:", IMAGE_PATH)
    exit()

height, width = image.shape[:2]

detector.setInputSize((width, height))

_, faces = detector.detect(image)

if faces is None:
    print("No faces detected")
else:
    print("Faces detected:", len(faces))

    for face in faces:
        x, y, w, h = face[:4].astype(int)
        print(f"Face: x={x}, y={y}, w={w}, h={h}")

        cv2.rectangle(
            image,
            (x, y),
            (x + w, y + h),
            (0, 255, 0),
            2
        )

cv2.imwrite("yunet_result.jpg", image)

print("Result saved as yunet_result.jpg")