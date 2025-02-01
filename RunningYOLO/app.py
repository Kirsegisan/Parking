from ultralytics import YOLO
#from roboflow import Roboflow
import cv2
import source as sr
import os
import time
from RedZoneConvert import draw_red_zone
import numpy as np

model = YOLO('../YOLO-weights/best_v18.pt')

#rf = Roboflow(api_key="kmdwHagZQlYas7gzGfw9")
#project = rf.workspace("parkingai-cyfy5").project("parking-utku6")
#model = project.version(13).model

def detect(camera, video_path):
    tO = time.time()
    print(camera, video_path)
    sr.setCameraPac(camera)
    cadr = 5
    video_capture = cv2.VideoCapture(video_path)
    tN = time.time()
    print("Connect camera", tN - tO)
    tO = tN
    while cadr > 0:
        cadr -= 1
        ret, image_to_process = video_capture.read()
        cv2.imwrite(f'original_images.png', image_to_process)
        image_to_process = draw_red_zone(image_to_process, camera, 2)
        height, width, _ = image_to_process.shape
        if cadr == 4:
            count = len(os.listdir(r"../generateDataset/imgbase")) + 1
            cv2.imwrite(f'../generateDataset/imgbase/image{count}.png', image_to_process)
            print(f"Images{count} is saved")
        blob = cv2.dnn.blobFromImage(image_to_process, 1 / 255, (320, 320),
                                     (0, 0, 0), swapRB=True, crop=False)

        class_indexes, class_scores, boxes = ([] for i in range(3))
        #results = model.predict(image_to_process, confidence=50, overlap=90).json()
        results = model.predict(source=draw_red_zone(image_to_process, camera), conf=0.50)
        tN = time.time()
        print("Detect images", tN - tO)
        tO = tN
        #print(results)

        bboxes_ = results[0].boxes.xyxy.tolist()
        bboxes = list(map(lambda x: list(map(lambda y: int(y), x)), bboxes_))
        confs_ = results[-1].boxes.conf.tolist()
        confs = list(map(lambda x: int(x * 100), confs_))
        classes_ = results[-1].boxes.cls.tolist()
        classes = list(map(lambda x: int(x), classes_))
        cls_dict = results[-1].names
        class_names = list(map(lambda x: cls_dict[x], classes))

        #print(bboxes)

        annot_lines = []
        for index, val in enumerate(class_names):
            xmin, ymin, xmax, ymax = int(bboxes[index][0]), int(bboxes[index][1]), int(bboxes[index][2]), int(bboxes[index][3])
            widthBox = xmax - xmin
            heightBox = ymax - ymin
            center_x = xmin + (widthBox / 2)
            center_y = ymin + (heightBox / 2)
            annotation = [center_x - (widthBox / 2), center_y - (heightBox / 2), widthBox, heightBox]
            annot_lines.append(annotation)
        #

        # for i in results["predictions"]:
        #     annotation = [i['x'] - i["width"]/2, i['y'] - i["height"]/2, i["width"], i["height"]]
        #     annot_lines.append(annotation)
        #print(annot_lines[1], annot_lines[3])
        #print(sr.finde_midle(annot_lines[1], annot_lines[3]))
        #print(sr.compute_overlaps(annot_lines[1], annot_lines[3]))

        if sr.createData(annot_lines):
            print("Create new data")
        else:
            data_boxes = sr.get_data()
            sr.now_all_space_free()
            #print(data_boxes)
            #print(annot_lines)
            free_space = []
            overlaps = 0
            if data_boxes and annot_lines:
                overlaps = sr.compute_overlaps(np.array(data_boxes), np.array(annot_lines), image_to_process)
            #print(overlaps)
            sr.nexStep()
            print("Update data")
            tN = time.time()
            print("Analysis", tN - tO)
            tO = tN
            #sr.draw_bbox(data_boxes[0], "test", image_to_process)
    #cv2.imshow('image', sr.draw_data(image_to_process))
    sr.delete_shit_in_data()
    # cv2.imshow('image', sr.draw_data(image_to_process, sr.chek_free_space()))
    # cv2.waitKey(0)
    free_space = sr.cheсk_free_space()
    not_free_space = sr.cheсk_not_free_space()
    print("Complite detect")
    foto = sr.draw_data(cv2.imread("original_images.png"), sr.get_data(), (0, 0, 255))
    foto = sr.draw_data(sr.draw_data(foto, not_free_space, (255, 0, 0)), free_space)
    tN = time.time()
    print("Rendering", tN - tO)
    tO = tN
    return foto, free_space
        #cv2.waitKey(0)


if __name__ == "main":
    #sr.delete_data()
    #sr.now_all_space_free()
    detect()
