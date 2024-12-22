import cv2
from openpyxl import load_workbook
import os
import json

data_base = load_workbook("RunningYOLO/dataBase.xlsx")
camera_Pac = data_base["M_Kolomenskaya1_1_10_31_E"]

with open('RedZoneTest.txt') as file:
    data = json.load(file)
    for i in data["boxes"]:
        annotation = [float(i['x']) - float(i["width"]) / 2, float(i['y']) - float(i["height"]) / 2, float(i["width"]), float(i["height"])]
        n = camera_Pac.max_row + 1
        x = annotation[0]
        y = annotation[1]
        w = annotation[2]
        h = annotation[3]
        x, y, w, h = int(float(x)), int(float(y)), int(float(w)), int(float(h))
        annotation = [x, y, w, h]
        camera_Pac.cell(row=n, column=1).value = annotation[0]
        camera_Pac.cell(row=n, column=2).value = annotation[1]
        camera_Pac.cell(row=n, column=3).value = annotation[2]
        camera_Pac.cell(row=n, column=4).value = annotation[3]
        camera_Pac.cell(row=n, column=5).value = -1
        camera_Pac.cell(row=n, column=6).value = -1
        data_base.save("RunningYOLO/dataBase.xlsx")
        print(annotation)