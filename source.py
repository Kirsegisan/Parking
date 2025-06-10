import cv2
import numpy as np
from openpyxl import load_workbook
import time
import asyncpg

_db_pool = None
data_base = load_workbook("dataBase.xlsx")
camera_Pac = []
camera_count = 1


class Place:
    def __init__(self, line):
        self.line = line
        self.x = int()
        self.y = int()
        self.h = int()
        self.w = int()
        self.free = bool()
        self.count = int()
        self.confidence = int()
        self.sub = int()

    def get(self):
        return [self.x, self.y, self.w, self.h, self.count, self.free, self.confidence, self.sub]

    def set(self, place, count=-1, confidence=-1, free=False, sub=-1):
        self.x, self.y, self.w, self.h, self.count, self.confidence, self.free, self.sub = place[0], place[1], place[2], \
                                                                                           place[
                                                                                               3], count, confidence, free, sub

    async def load(self, camera):
        tO = time.time()
        async with _db_pool.acquire() as conn:
            row = await conn.fetchrow(
                f"""SELECT "X", "Y", "H", "W", "COUNT", "CONFIDENCE", "FREE", "SUB" FROM parking."{camera}" WHERE ctid = '(0,{self.line})'::tid"""
            )
            if row:
                self.x = row["X"]
                self.y = row["Y"]
                self.h = row["H"]
                self.w = row["W"]
                self.free = row["FREE"]
                self.count = row["COUNT"]
                self.confidence = row["CONFIDENCE"]
                self.sub = row["SUB"]
                tN = time.time()
                #print(camera, "load place", tN - tO, row)

    async def push(self, camera):
        async with _db_pool.acquire() as conn:
            query = f"""
            UPDATE parking."{camera}" SET
                "X" = {self.x},
                "Y" = {self.y},
                "H" = {self.h},
                "W" = {self.w},
                "COUNT" = {self.count},
                "CONFIDENCE" = {self.confidence},
                "FREE" = {self.free},
                "SUB" = {self.sub}
            WHERE ctid = '(0,{self.line})'::tid;
            """
            await conn.execute(query)
            # await conn.execute(
            #     f'''
            #                 DO $$
            #             BEGIN
            #                 IF EXISTS (
            #                     SELECT 1 FROM parking."{camera}"
            #                     WHERE ctid = '(0,{self.line})'::tid
            #                 ) THEN
            #                     UPDATE parking."{camera}" SET
            #                         "X" = {self.x},
            #                         "Y" = {self.y},
            #                         "H" = {self.h},
            #                         "W" = {self.w},
            #                         "COUNT" = {self.count},
            #                         "CONFIDENCE" = {self.confidence},
            #                         "FREE" = {self.free},
            #                         "SUB" = {self.sub}
            #                     WHERE ctid = '(0,{self.line})'::tid;
            #                 ELSE
            #                     INSERT INTO parking."{camera}"
            #                         ("X", "Y", "H", "W", "COUNT", "CONFIDENCE", "FREE", "SUB")
            #                     VALUES (
            #                         {self.x}, {self.y}, {self.h}, {self.w},
            #                         {self.count}, {self.confidence}, {self.free}, {self.sub}
            #                     );
            #                 END IF;
            #             END $$;
            #     ''',
            #     self.x, self.y, self.h, self.w,
            #     self.count, self.confidence, self.free, self.sub
            # )

    async def add(self, camera):
        async with _db_pool.acquire() as conn:
            query = f"""
            INSERT INTO parking."{camera}"
                ("X", "Y", "H", "W", "COUNT", "CONFIDENCE", "FREE", "SUB")
            VALUES ({self.x}, {self.y}, {self.h}, {self.w}, {self.count}, {self.confidence}, {self.free}, {self.sub})
            """
            await conn.execute(query)

    def finde_midle(self, box):
        self.x = (self.x + box[0]) / 2
        self.y = (self.y + box[1]) / 2
        self.w = (self.w + box[2]) / 2
        self.h = (self.h + box[3]) / 2
        self.count += 1



    async def delete(self, camera):
        async with _db_pool.acquire() as conn:
            await conn.execute(
                f"""DELETE FROM parking."{camera}" WHERE ctid = '(0, {self.line})'::tid"""
            )


async def init_db(camera="M_Kolomenskaya1_1_10_31_W"):
    # 'postgresql://parking_admin:ParkinG!23@185.250.44.14:5432/parking_db'
    global _db_pool
    _db_pool = await asyncpg.create_pool(
        f'postgresql://{camera}_admin:ParkinG!23@localhost/parking_db'
    )
    try:
        async with _db_pool.acquire() as conn:
            await conn.fetch("SELECT 1")
        print("successful connect")
    except:
        print("failed connect")


async def now_all_space_free(camera):
    async with _db_pool.acquire() as conn:
        await conn.execute(
            f'UPDATE parking."{camera}" SET "FREE" = True'
        )


async def cheсk_free_space(camera):
    free_space = []
    shlak_but_space = []
    not_free_space = []
    async with _db_pool.acquire() as conn:
        lenth = await conn.fetchval(f'SELECT COUNT(*) FROM parking."{camera}"')
    for i in range(1, lenth + 1):
        place = Place(i)
        await place.load(camera)
        if place.free and place.confidence > 5:
            free_space.append(place)
        elif place.free:
            shlak_but_space.append(place)
        elif not place.free:
            not_free_space.append(place)
    return free_space, shlak_but_space, not_free_space


async def reduced_reliability(camera):
    async with _db_pool.acquire() as conn:
        i = await conn.fetchval(f'SELECT COUNT(*) FROM parking."{camera}"')
    while i > 0:
        place = Place(i)
        await place.load(camera)
        if place.free:
            place.confidence -= 0.5
            if place.confidence < 0:
                await place.delete(camera)
        i -= 1
    async with _db_pool.acquire() as conn:
        await conn.fetchval(f'VACUUM FULL parking."{camera}"')


def same_box(box1, box2):
    n = 0
    for i in range(4):
        n += abs(box1[i] - box2[i])
    return n < 30


def delete_shit_in_data():
    i = 2
    max_row = camera_Pac.max_row
    while i <= max_row - 1:
        j = i + 1
        while j <= max_row:
            box1 = [
                camera_Pac.cell(row=i, column=1).value,
                camera_Pac.cell(row=i, column=2).value,
                camera_Pac.cell(row=i, column=3).value,
                camera_Pac.cell(row=i, column=4).value
            ]
            box2 = [
                camera_Pac.cell(row=j, column=1).value,
                camera_Pac.cell(row=j, column=2).value,
                camera_Pac.cell(row=j, column=3).value,
                camera_Pac.cell(row=j, column=4).value
            ]
            if same_box(box1, box2):
                camera_Pac.delete_rows(j)
                max_row -= 1
                print("One more shit was deleted ", camera_Pac.cell(row=i, column=5).value,
                      camera_Pac.cell(row=i, column=6).value)
                data_base.save("dataBase.xlsx")
            else:
                j += 1
        i += 1


async def calculate_iou(box, camera, push=True):
    t = 0
    totalIOU = 0
    maxIOU = 0
    flag = 1

    async with _db_pool.acquire() as conn:
        length = await conn.fetchval(f'SELECT COUNT(*) FROM parking."{camera}"')
    #print(camera, box, end='\n')
    for i in range(1, length + 1):
        place = Place(i)
        await place.load(camera)
        #print(i, place.get(), end=' ')
        y1 = np.maximum(box[0], place.x)
        y2 = np.minimum(box[2] + box[0], place.w + place.x)
        x1 = np.maximum(box[1], place.y)
        x2 = np.minimum(box[3] + box[1], place.h + place.y)
        intersection = np.maximum(x2 - x1, 0) * np.maximum(y2 - y1, 0)
        union = box[2] * box[3] + place.h * place.w - intersection
        iou = intersection / union
        totalIOU += iou
        #print(iou, end=' ')
        if iou > 0.6:
            place.finde_midle(box)
            tO = time.time()
            place.sub = iou
            place.confidence += 1
            tN = time.time()
            t += tO - tN
            flag = 0
            #print("correct", end=" ")
        if iou > 0.15:
            place.free = False
            flag = 0
            #print("mark", end=" ")
        else:
            if place.sub + iou > 0.15:
                place.free = False
            place.sub += iou
            #print("free", end=" ")
        #print("\n")
        if push:
            await place.push(camera)
    async with _db_pool.acquire() as conn:
        await conn.fetchval(f'VACUUM FULL parking."{camera}"')

    if flag:
        place = Place(length)
        place.set(box, 0, 5, False, 0)
        if push:
            #print("add")
            await place.add(camera)
    #print('\n')
    return True


async def getOne():
    tables = await get_all_tables()
    for table in tables:
        if table != "CAMERAS":
            async with _db_pool.acquire() as conn:
                rows = await conn.fetch(f'SELECT ctid, * FROM parking."{table}"')
                for row in rows:
                    print(f"{table}--- CTID: {row['ctid']}, Data: {dict(row)}")



async def compute_overlaps(boxes, camera):
    await init_db(camera)
    #print(await get_all_tables())
    await setIOU(camera)
    await now_all_space_free(camera)
    await calculate_iou(boxes[0], camera, False)
    for box in boxes:
        place = Place(-1)
        place.set(box)
        await calculate_iou(box, camera)
    await reduced_reliability(camera)
    await getOne()
    return await cheсk_free_space(camera)


async def setIOU(camera):
    async with _db_pool.acquire() as conn:
        await conn.execute(
            f'UPDATE parking."{camera}" SET "SUB" = 0'
        )


async def draw_data(image_to_process, boxes, parking_color=(0, 255, 0)):
    color = parking_color
    width = 2
    for i in boxes:
        for place in i:
            x, y, w, h = int(place.x), int(place.y), int(place.w), int(place.h)
            start = (x, y)
            end = (x + w, y + h)
            if place.free and place.confidence > 5:
                color = (0, 255, 0)
            elif place.free and place.confidence <= 5:
                color = (0, 165, 255)
            else:
                color = (255, 0, 0)
            image_to_process = cv2.rectangle(image_to_process, start, end, color, width)
    return image_to_process


async def get_all_tables():
    async with _db_pool.acquire() as conn:
        tables = await conn.fetch(
            "SELECT table_name FROM information_schema.tables "
            "WHERE table_schema = 'parking' AND table_type = 'BASE TABLE'"
        )
        return [table['table_name'] for table in tables]


async def delete_data():
    await init_db()
    tables = await get_all_tables()
    for table in tables:
        if table != "CAMERAS":
            async with _db_pool.acquire() as conn:
                await conn.execute(f'DELETE FROM parking."{table}"')
                await conn.fetchval(f'VACUUM FULL parking."{table}"')

"""
import cv2
import numpy as np
from openpyxl import load_workbook
import time
import asyncpg

_db_pool = None
data_base = load_workbook("dataBase.xlsx")
camera_Pac = []
camera_count = 1


class Place:
    def __init__(self, line):
        self.line = line
        self.x = int()
        self.y = int()
        self.h = int()
        self.w = int()
        self.free = bool()
        self.count = int()
        self.confidence = int()
        self.sub = int()

    def get(self):
        return [self.x, self.y, self.h, self.w, self.count, self.free, self.confidence, self.sub]

    def set(self, place, count=-1, confidence=-1, free=False, sub=-1):
        self.x, self.y, self.h, self.w, self.count, self.confidence, self.free, self.sub = place[0], place[1], place[2], place[3], count, confidence, free, sub

    def load(self, camera):
        tO = time.time()
        async with _db_pool.acquire() as conn:
            row = await conn.fetchrow(
                f'SELECT x, y, h, w, count, confidence, free, sub FROM {camera} WHERE id = $1',
                self.line  # ID нужной строки
            )
            await conn.close()
            self.x = row['x']
            self.y = row['y']
            self.h = row['h']
            self.w = row['w']
            self.free = row['free']
            self.count = row['count']
            self.confidence = row['confidence']
            self.sub = row['sub']
            tN = time.time()
            print(camera, "load place", tN - tO)

    async def push(self, camera):
        async with _db_pool.acquire() as conn:
            await conn.execute(
                f'''
                INSERT INTO {camera} (id, x, y, h, w, count, confidence, free, sub)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
                ON CONFLICT (id) DO UPDATE
                SET
                    x = EXCLUDED.x,
                    y = EXCLUDED.y,
                    h = EXCLUDED.h,
                    w = EXCLUDED.w,
                    count = EXCLUDED.count,
                    confidence = EXCLUDED.confidence,
                    free = EXCLUDED.free,
                    sub = EXCLUDED.sub
                ''',
                self.line, self.x, self.y, self.h, self.w,
                self.count, self.confidence, self.free, self.sub
            )

    def finde_midle(self, box):
        self.x = (self.x + box[0]) / 2
        self.y = (self.y + box[1]) / 2
        self.h = (self.h + box[2]) / 2
        self.w = (self.w + box[3]) / 2
        self.count += 1

    def delete(self, camera):
        async with _db_pool.acquire() as conn:
            row = await conn.fetchrow(
                f"DELETE FROM {camera} WHERE id = $1",
                self.line  # ID нужной строки
            )


async def init_db():
    global _db_pool
    #'postgresql://parking_admin:ParkinG!23@localhost/parking_db'
    _db_pool = await asyncpg.create_pool(
        'postgresql://parking_admin:ParkinG!23@185.250.44.14:5432/parking_db'
    )


def nexStep():
    camera_Pac.cell(row=1, column=1).value += 1
    data_base.save("dataBase.xlsx")


def createData(annot_lines):
    if camera_Pac.cell(row=1, column=1).value == 0:
        m = camera_Pac.max_row - 1
        for parkingInd in range(m, len(annot_lines) + m):
            camera_Pac.cell(row=parkingInd + 2, column=1).value = annot_lines[parkingInd - m][0]
            camera_Pac.cell(row=parkingInd + 2, column=2).value = annot_lines[parkingInd - m][1]
            camera_Pac.cell(row=parkingInd + 2, column=3).value = annot_lines[parkingInd - m][2]
            camera_Pac.cell(row=parkingInd + 2, column=4).value = annot_lines[parkingInd - m][3]
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



def now_all_space_free(camera):
    async with _db_pool.acquire() as conn:
        await conn.execute(
            f"UPDATE {camera} SET free = True"
        )


def cheсk_free_space(camera):
    free_space = []
    shlak_but_space = []
    not_free_space = []
    async with _db_pool.acquire() as conn:
        lenth = await conn.fetchval(f"SELECT COUNT(*) FROM {camera}")
    for i in range(lenth):
        place = Place(i)
        place.load()
        if place.free and place.confidence > 5:
            free_space.append(place)
        elif place.free:
            shlak_but_space.append(place)
        elif not place.free:
            not_free_space.append(place)

    return free_space, shlak_but_space, not_free_space


def reduced_reliability(camera):
    async with _db_pool.acquire() as conn:
        i = await conn.fetchval(f"SELECT COUNT(*) FROM {camera}")
    while i > 0:
        place = Place(i)
        place.load()
        if place.free:
            place.confidence -= 0.5
            if place.confidence < 0:
                place.delete()
        i -= 1


def same_box(box1, box2):
    n = 0
    for i in range(4):
        n += abs(box1[i] - box2[i])
    return n < 30


def delete_shit_in_data():
    i = 2
    max_row = camera_Pac.max_row
    while i <= max_row - 1:
        j = i + 1
        while j <= max_row:
            box1 = [
                camera_Pac.cell(row=i, column=1).value,
                camera_Pac.cell(row=i, column=2).value,
                camera_Pac.cell(row=i, column=3).value,
                camera_Pac.cell(row=i, column=4).value
            ]
            box2 = [
                camera_Pac.cell(row=j, column=1).value,
                camera_Pac.cell(row=j, column=2).value,
                camera_Pac.cell(row=j, column=3).value,
                camera_Pac.cell(row=j, column=4).value
            ]
            if same_box(box1, box2):
                camera_Pac.delete_rows(j)
                max_row -= 1
                # camera_Pac.cell(row=i, column=1).value = None
                # camera_Pac.cell(row=i, column=2).value = None
                # camera_Pac.cell(row=i, column=3).value = None
                # camera_Pac.cell(row=i, column=4).value = None
                # camera_Pac.cell(row=i, column=5).value = None
                # camera_Pac.cell(row=i, column=6).value = None
                print("One more shit was deleted ", camera_Pac.cell(row=i, column=5).value,
                      camera_Pac.cell(row=i, column=6).value)
                data_base.save("dataBase.xlsx")
            else:
                j += 1
        i += 1


# Функции для подсчета Intersection over Union (IoU)
def calculate_iou(box, camera):
    # Считаем IoU
    t = 0
    totalIOU = 0
    maxIOU = 0
    flag = 1
    async with _db_pool.acquire() as conn:
        lenth = await conn.fetchval(f"SELECT COUNT(*) FROM {camera}")
    x = 1
    for i in range(lenth):
        place = Place(i)
        place.load(camera)
        y1 = np.maximum(box[0], place.x)
        y2 = np.minimum(box[2] + box[0], place.h + place.x)
        x1 = np.maximum(box[1], place.y)
        x2 = np.minimum(box[3] + box[1], place.w + place.y)
        intersection = np.maximum(x2 - x1, 0) * np.maximum(y2 - y1, 0)
        union = box[2] * box[3] + place.h * place.w - intersection
        iou = intersection / union
        totalIOU += iou
        if iou > 0.6:
            place.finde_midle(box)
            tO = time.time()
            place.sub = iou
            tN = time.time()
            t += tO - tN
            flag = 0
        if iou > 0.15:
            place.free = False
            flag = 0
        else:
            if place.sub + iou > 0.15:
                place.free = False
            place.sub += iou
        place.load(camera)

    if flag:
        place = Place(lenth + x)
        x += 1
        place.set(box, 0, 0, False, 0)
        place.push(camera)
    return iou


# Функция для расчета персечения всех со всеми через IoU
def compute_overlaps(boxes, camera):
    setIOU(camera)
    init_db()
    now_all_space_free(camera)
    for box in boxes:
        place = Place(-1)
        place.set(box)
        calculate_iou(box, camera)
    return


def setIOU(camera):
    async with _db_pool.acquire() as conn:
        await conn.execute(
            f"UPDATE {camera} SET sub = 0"
        )


def draw_data(image_to_process, boxes, parking_color=(0, 255, 0)):
    color = parking_color
    width = 2
    for i in boxes:
        for place in i:
            x, y, w, h = int(place.x), int(place.y), int(place.w), int(place.h)
            start = (x, y)
            end = (x + w, y + h)
            if place.free and place.confidence > 5:
                color = (0, 255, 0)

            elif place.free and place.confidence <= 5:
                color = (0, 165, 255)
            else:
                color = (255, 0, 0)
            image_to_process = cv2.rectangle(image_to_process, start, end, color, width)
    return image_to_process"""
