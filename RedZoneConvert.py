import cv2
from openpyxl import load_workbook
import os
import json
def draw_red_zone(img, camera, t=-1):
    with open("RedZone/" + camera + ".txt") as file:
        data = json.load(file)
        if data != None:
            for i in data["boxes"]:
                annotation = [float(i['x']) - float(i["width"]) / 2, float(i['y']) - float(i["height"]) / 2, float(i["width"]), float(i["height"])]
                x = annotation[0]
                y = annotation[1]
                w = annotation[2]
                h = annotation[3]
                x, y, w, h = int(float(x)), int(float(y)), int(float(w)), int(float(h))
                start = (x, y) 
                end = (x + w, y + h)
                img = cv2.rectangle(img, start, end, (0, 0, 255), t)
                annotation = [x, y, w, h]
                print(annotation)
            return img