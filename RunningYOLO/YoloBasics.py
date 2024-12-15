from ultralytics import YOLO
import cv2

model = YOLO('../YOLO-weights/last.pt')
results = model.predict("images/03.jpg", show=True)
#!yolo task=detect mode=predict model={HOME}/runs/detect/train/weights/best.pt conf=0.25 source={dataset.location}/test/images save=True
cv2.waitKey(0)
