from openpyxl import load_workbook
import app

usersFile = load_workbook("Cameras.xlsx")


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


def detAnalysisAddresses(address):
    freeSpace = []
    freeSpaceImg = []
    cameras = {}
    camerasList = []
    answer = []
    for i in range(1, usersFile[address].max_row + 1):
        camerasList.append(usersFile[address].cell(row=i, column=1).value)
        cameras[usersFile[address].cell(row=i, column=1).value] = usersFile[address].cell(row=i, column=2).value

    for camera in camerasList:
        detectResult = app.detect(camera, cameras[camera])
        answer.append(detectResult)
        freeSpaceImg.append(detectResult[0])
        freeSpace.append(detectResult[1])

    return answer


getAddressesString()
