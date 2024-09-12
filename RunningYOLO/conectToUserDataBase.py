from openpyxl import load_workbook


usersFile = load_workbook("users.xlsx")


class User:
    def __init__(self, userID):
        self.userID = userID
        self.userSheet = usersFile[self.userID]

    def addACameraToTheUser(self, cameraID, cameraName):
        for i in range(1, self.userSheet.max_row + 1):
            if cameraID == self.userSheet.cell(row=i, column=1).value:
                return False
        else:
            self.userSheet.cell(row=self.userSheet.max_row + 1, column=1).value = cameraID
            self.userSheet.cell(row=self.userSheet.max_row + 1, column=2).value = cameraName
        return True

    def getUserCameras(self):
        userCameras = []
        for i in range(1, self.userSheet.max_row + 1):
            userCameras[self.userSheet.cell(row=self.userSheet.max_row + 1, column=1).value] = \
                self.userSheet.cell(row=self.userSheet.max_row + 1, column=2).value
        return userCameras


def userInDB(userID):
    sheets = usersFile.get_sheet_names()
    if userID in sheets:
        return True
    return False


def addUserToBD(userID):
    usersFile.create_sheet(userID)
    usersFile.save("users.xlsx")
