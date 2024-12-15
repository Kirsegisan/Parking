import cv2
import numpy as np
from openpyxl import load_workbook

data_base = load_workbook("dataBase.xlsx")
camera_Pac = []
camera_count = 1


def nexStep():
    camera_Pac.cell(row=1, column=1).value += 1
    data_base.save("dataBase.xlsx")


def createData(annot_lines):
    if camera_Pac.cell(row=1, column=1).value == 0:
        for parkingInd in range(len(annot_lines)):
            camera_Pac.cell(row=parkingInd + 2, column=1).value = annot_lines[parkingInd][0]
            camera_Pac.cell(row=parkingInd + 2, column=2).value = annot_lines[parkingInd][1]
            camera_Pac.cell(row=parkingInd + 2, column=3).value = annot_lines[parkingInd][2]
            camera_Pac.cell(row=parkingInd + 2, column=4).value = annot_lines[parkingInd][3]
            camera_Pac.cell(row=parkingInd + 2, column=5).value = 1
            camera_Pac.cell(row=parkingInd + 2, column=6).value = 0
        camera_Pac.cell(row=1, column=1).value += 1
        data_base.save("dataBase.xlsx")
        return True
    return False


def setCameraPac(newCamera):
    global camera_Pac
    camera_Pac = data_base[newCamera]


def delete_data():
    camera_Pac.delete_rows(1, camera_Pac.max_row)
    # for i in range(camera_Pac.max_row):
    #     camera_Pac.cell(row=i + 2, column=1).value = None
    #     camera_Pac.cell(row=i + 2, column=2).value = None
    #     camera_Pac.cell(row=i + 2, column=3).value = None
    #     camera_Pac.cell(row=i + 2, column=4).value = None
    #     camera_Pac.cell(row=i + 2, column=5).value = None
    camera_Pac.cell(row=1, column=1).value = 0
    data_base.save("dataBase.xlsx")


def now_all_space_free():
    for i in range(2, camera_Pac.max_row + 1):
        if camera_Pac.cell(row=i, column=5).value:
            camera_Pac.cell(row=i, column=6).value = 1
    data_base.save("dataBase.xlsx")


def cheсk_free_space():
    free_space = []
    for i in range(2, camera_Pac.max_row):
        if camera_Pac.cell(row=i, column=6).value == 1:
            free_space.append([camera_Pac.cell(row=i, column=1).value,
                                camera_Pac.cell(row=i, column=2).value,
                                camera_Pac.cell(row=i, column=3).value,
                                camera_Pac.cell(row=i, column=4).value,
                                camera_Pac.cell(row=i, column=5).value,
                                camera_Pac.cell(row=i, column=6).value])
    print(free_space)
    return free_space


def cheсk_not_free_space():
    not_free_space = []
    for i in range(2, camera_Pac.max_row):
        if camera_Pac.cell(row=i, column=6).value == 0:
            if camera_Pac.cell(row=i, column=1).value and camera_Pac.cell(row=i, column=2).value and camera_Pac.cell(row=i, column=3).value and camera_Pac.cell(row=i, column=4).value:
                not_free_space.append([camera_Pac.cell(row=i, column=1).value,
                                    camera_Pac.cell(row=i, column=2).value,
                                    camera_Pac.cell(row=i, column=3).value,
                                    camera_Pac.cell(row=i, column=4).value,
                                    camera_Pac.cell(row=i, column=5).value,
                                    camera_Pac.cell(row=i, column=6).value])
    return not_free_space


def delete_shit_in_data():
    for i in range(2, camera_Pac.max_row):
        if camera_Pac.cell(row=i, column=5).value and int(camera_Pac.cell(row=i, column=5).value) < 5:
            #camera_Pac.delete_rows(i)
            camera_Pac.cell(row=i, column=1).value = None
            camera_Pac.cell(row=i, column=2).value = None
            camera_Pac.cell(row=i, column=3).value = None
            camera_Pac.cell(row=i, column=4).value = None
            camera_Pac.cell(row=i, column=5).value = None
            camera_Pac.cell(row=i, column=6).value = None
            print("One more shit was deleted")
            data_base.save("dataBase.xlsx")


def get_data():
    boxes = []
    for i in range(camera_Pac.max_row):
        if camera_Pac.cell(row=i + 2, column=1).value:
            boxes.append([camera_Pac.cell(row=i + 2, column=1).value,
                          camera_Pac.cell(row=i + 2, column=2).value,
                          camera_Pac.cell(row=i + 2, column=3).value,
                          camera_Pac.cell(row=i + 2, column=4).value,
                          camera_Pac.cell(row=i + 2, column=5).value,
                          camera_Pac.cell(row=i + 2, column=6).value])

    return boxes


#Функции для подсчета Intersection over Union (IoU)
def calculate_iou(box, boxes, box_area, boxes_area, image_to_process):
    #Считаем IoU
    y1 = np.maximum(box[0], boxes[:, 0])
    y2 = np.minimum(box[2]+box[0], boxes[:, 2]+boxes[:, 0])
    x1 = np.maximum(box[1], boxes[:, 1])
    x2 = np.minimum(box[3]+box[1], boxes[:, 3]+boxes[:, 1])
    intersection = np.maximum(x2 - x1, 0) * np.maximum(y2 - y1, 0)
    union = box_area + boxes_area[:] - intersection[:]
    iou = intersection / union
    flag = 1
    for i in range(len(iou)):
        if iou[i] > 0.6:
            #draw_two_box(image_to_process, [box, boxes[i]])
            #print(iou[i], box, boxes[i])
            midle = finde_midle(box, boxes[i])
            camera_Pac.cell(row=i + 2, column=1).value = midle[0]
            camera_Pac.cell(row=i + 2, column=2).value = midle[1]
            camera_Pac.cell(row=i + 2, column=3).value = midle[2]
            camera_Pac.cell(row=i + 2, column=4).value = midle[3]
            camera_Pac.cell(row=i + 2, column=5).value = midle[4]
            camera_Pac.cell(row=i + 2, column=6).value = 0
            data_base.save("dataBase.xlsx")
            flag = 0
        if iou[i] > 0.2 :
            camera_Pac.cell(row=i + 2, column=6).value = 0
            data_base.save("dataBase.xlsx")
    if flag:
        row = camera_Pac.max_row
        camera_Pac.cell(row=row, column=1).value = box[0]
        camera_Pac.cell(row=row, column=2).value = box[1]
        camera_Pac.cell(row=row, column=3).value = box[2]
        camera_Pac.cell(row=row, column=4).value = box[3]
        camera_Pac.cell(row=row, column=5).value = 1
        camera_Pac.cell(row=row, column=6).value = 0
    data_base.save("dataBase.xlsx")
    return iou

#Функция для расчета персечения всех со всеми через IoU
def compute_overlaps(boxes1, boxes2, image_to_process):
    #Areas of anchors and GT boxes
    #print(boxes1, "\n", boxes2)
    area1 = boxes1[:, 2] * boxes1[:, 3]
    area2 = boxes2[:, 2] * boxes2[:, 3]
    overlaps = np.zeros((boxes1.shape[0], boxes2.shape[0]))
    for i in range(overlaps.shape[1]):
        box2 = boxes2[i]
        overlaps[:, i] = calculate_iou(box2, boxes1, area2[i], area1, image_to_process)


    return overlaps


def finde_midle(box1, box2):
    new_box = [(box1[0] + box2[0]) / 2, (box1[1] + box2[1]) / 2, (box1[2] + box2[2]) / 2, (box1[3] + box2[3]) / 2, box2[4] +1]
    return new_box


# Функция для отрисовки Bounding Box в кадре
def draw_bbox(box, image_to_process, parking_color=(0, 255, 0)):
    x, y, w, h = box[:4]
    start = (x, y)
    end = (x + w, y + h)
    color = parking_color
    width = 2
    final_image = cv2.rectangle(image_to_process, start, end, color, width)
    cv2.imshow('image', final_image)
    cv2.waitKey(0)

    # Подпись BB
    start = (x, y - 10)
    font_size = 0.4
    font = cv2.FONT_HERSHEY_SIMPLEX
    width = 1
    text = "parking_text"
    final_image = cv2.putText(final_image, text, start, font, font_size, color, width, cv2.LINE_AA)
    return final_image


def draw_data(image_to_process, boxes, parking_color=(0, 255, 0)):
    color = parking_color
    width = 2
    for box in boxes:
        # print(box)
        x, y, w, h = box[0], box[1], box[2], box[3]
        x, y, w, h = int(x), int(y), int(w), int(h)
        start = (x, y)
        end = (x + w, y + h)
        image_to_process = cv2.rectangle(image_to_process, start, end, color, width)
        # cv2.imshow('image', image_to_process)
    return image_to_process


def draw_two_box(image_to_process, boxes):
    final_image = image_to_process
    for box in boxes:
        #print(box)
        x, y, w, h = box[0], box[1], box[2], box[3]
        start = (x, y)
        end = (x + w, y + h)
        color = (0, 255, 0)
        width = 2
        #final_image = cv2.rectangle(final_image, start, end, color, width)
        cv2.imshow('image', cv2.rectangle(final_image, start, end, color, width))
    #cv2.imshow('image', image_to_process)
    cv2.waitKey(0)
