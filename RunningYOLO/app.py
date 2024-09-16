from ultralytics import YOLO
import cv2
import sourse as sr
import os
import numpy as np

import pandas as pd
from art import tprint
import matplotlib.pylab as plt
import requests


model = YOLO('../YOLO-weights/best_v9.pt')

# Инициализируем работу с видео



# Пока не нажата клавиша q функция будет работать
def detect(camera, video_path):
    print(camera, video_path)
    sr.setCameraPac(camera)
    cadr = 10
    video_capture = cv2.VideoCapture(video_path)
    while cadr > 0:
        cadr -= 1
        ret, image_to_process = video_capture.read()

        # Препроцессинг изображения и работа YOLO
        height, width, _ = image_to_process.shape
        if cadr == 9:
            count = len(os.listdir(r"D:/MyApp/Parking/generateDataset/imgbase"))
            cv2.imwrite(f'../generateDataset/imgbase/image{count}.png', image_to_process)
            print(f"Images{count} is saved")
        blob = cv2.dnn.blobFromImage(image_to_process, 1 / 255, (640, 640),
                                     (0, 0, 0), swapRB=True, crop=False)

        class_indexes, class_scores, boxes = ([] for i in range(3))
        results = model.predict(source=image_to_process, conf=0.50, show=True)
        #print(results)
        # расшифровываем объект results
        bboxes_ = results[0].boxes.xyxy.tolist()
        bboxes = list(map(lambda x: list(map(lambda y: int(y), x)), bboxes_))
        confs_ = results[0].boxes.conf.tolist()
        confs = list(map(lambda x: int(x * 100), confs_))
        classes_ = results[0].boxes.cls.tolist()
        classes = list(map(lambda x: int(x), classes_))
        cls_dict = results[0].names
        class_names = list(map(lambda x: cls_dict[x], classes))

        #print(bboxes)

        annot_lines = []
        for index, val in enumerate(class_names):
            xmin, ymin, xmax, ymax = int(bboxes[index][0]), int(bboxes[index][1]), int(bboxes[index][2]), int(bboxes[index][3])
            widthBox = xmax - xmin
            heightBox = ymax - ymin
            center_x = xmin + (widthBox / 2)
            center_y = ymin + (heightBox / 2)
            annotation = [xmin, ymin, widthBox, heightBox]
            annot_lines.append(annotation)
        #print(annot_lines[1], annot_lines[3])
        #print(sr.finde_midle(annot_lines[1], annot_lines[3]))
        #print(sr.compute_overlaps(annot_lines[1], annot_lines[3]))

        if sr.createData(annot_lines):
            print("Create new data")
        else:
            data_boxes = sr.get_data()
            sr.now_all_space_free()
            # print(data_boxes)
            # print(annot_lines)
            free_space = []
            overlaps = 0
            if data_boxes and annot_lines:
                overlaps = sr.compute_overlaps(np.array(data_boxes), np.array(annot_lines), image_to_process)
            print(overlaps)
            sr.nexStep()
            print("Update data")
            #sr.draw_bbox(data_boxes[0], "test", image_to_process)
    #cv2.imshow('image', sr.draw_data(image_to_process))
    sr.delete_shit_in_data()
    # cv2.imshow('image', sr.draw_data(image_to_process, sr.chek_free_space()))
    # cv2.waitKey(0)
    free_space = sr.chek_free_space()
    return sr.draw_data(image_to_process, free_space), free_space
        #cv2.waitKey(0)


if __name__ == "main":
    #sr.delete_data()
    #sr.now_all_space_free()
    detect()
