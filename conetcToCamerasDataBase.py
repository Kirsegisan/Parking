import asyncio

from openpyxl import load_workbook
from concurrent.futures import ProcessPoolExecutor
import functools
import app
from ultralytics import YOLO
import time

usersFile = load_workbook("Cameras.xlsx")
model = YOLO('YOLO-weights/best_v36.pt')

def getAddressesList():
    return usersFile.get_sheet_names()



def getAddressesString():
    addresses = usersFile.get_sheet_names()
    result = ''
    for address in addresses:
        result += f", {address}"
    return result


def getAddresses():
    inData = usersFile.get_sheet_names()
    outData = []
    for i in range(len(inData)):
        outData.append([inData[i]])
    return outData


# def detAnalysisAddresses(address):
#     freeSpace = []
#     freeSpaceImg = []
#     cameras = {}
#     camerasList = []
#     answer = []
#     for i in range(1, usersFile[address].max_row + 1):
#         camerasList.append(usersFile[address].cell(row=i, column=1).value)
#         cameras[usersFile[address].cell(row=i, column=1).value] = usersFile[address].cell(row=i, column=2).value
#
#     for camera in camerasList:
#         detectResult = app.detect(camera, cameras[camera])
#         answer.append(detectResult)
#         freeSpaceImg.append(detectResult[0])
#         freeSpace.append(detectResult[1])
#
#     return answer


def detAnalysisAddresses(address):
    # Подготовка данных
    cameras = {}
    camerasList = []
    for i in range(1, usersFile[address].max_row + 1):
        camera = usersFile[address].cell(row=i, column=1).value
        camerasList.append(camera)
        cameras[camera] = usersFile[address].cell(row=i, column=2).value

    # Частичная функция для передачи дополнительных аргументов
    detect_partial = functools.partial(run_detect_in_process, cameras=cameras)

    # Используем ProcessPoolExecutor для параллельного выполнения в процессах
    with ProcessPoolExecutor() as executor:
        # Запускаем все задачи
        futures = [
            executor.submit(detect_partial, camera)
            for camera in camerasList
        ]

        # Собираем результаты
        answer = []
        freeSpaceImg = []
        freeSpace = []
        for future in futures:
            detectResult = future.result()
            answer.append(detectResult)
            freeSpaceImg.append(detectResult[0])
            freeSpace.append(detectResult[1])

    return answer

def run_detect_in_process(camera, cameras):
    """Функция-обертка для запуска в отдельном процессе"""
    return asyncio.run(app.detect(camera, cameras[camera], model))


getAddressesString()
