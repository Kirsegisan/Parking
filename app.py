
#from roboflow import Roboflow
import cv2
import subprocess
import source as sr
import os
from vidgear.gears import VideoGear
import time
from RedZoneConvert import draw_red_zone
import numpy as np
import matplotlib.pyplot as plt  # <-- Добавлено



def show_image(image):
    plt.imshow(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))  # Конвертация BGR в RGB
    plt.axis('off')  # Скрыть оси
    plt.show()
#rf = Roboflow(api_key="kmdwHagZQlYas7gzGfw9")
#project = rf.workspace("parkingai-cyfy5").project("parking-utku6")
#model = project.version(13).model


def get_rtsp_frame(rtsp_url, timeout_sec=30):
    """Захватывает один кадр с RTSP-камеры через FFmpeg"""
    command = [
        'ffmpeg/bin/ffmpeg.exe',
        '-y',  # Перезапись без подтверждения
        '-timeout', str(timeout_sec),  # Таймаут подключения
        '-i', rtsp_url,  # URL камеры
        '-frames:v', '1',  # Только 1 кадр
        '-f', 'image2pipe',  # Вывод в pipe
        '-vcodec', 'png',  # Формат PNG
        '-loglevel', 'error',  # Только ошибки
        '-'
    ]

    try:
        result = subprocess.run(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True
        )
        image = cv2.imdecode(
            np.frombuffer(result.stdout, np.uint8),
            cv2.IMREAD_COLOR
        )
        return image
    except subprocess.CalledProcessError as e:
        print(f"Ошибка подключения к {rtsp_url}: {e.stderr.decode()}")
        return None


async def detect(camera, video_path, model):
    tO = time.time()
    print(camera, video_path)
    cadr = 1
    # stream = VideoGear(video_path).start()
    # frame = stream.read()
    # if frame is not None:
    #     cv2.imshow('Frame', frame)
    #     cv2.waitKey(0)
    video_capture = cv2.VideoCapture(video_path)
    # video_capture = cv2.VideoCapture("images/record/train.mp4")
    tN = time.time()
    print(camera, "Connect camera", tN - tO)
    tO = tN
    while cadr > 0:
        cadr -= 1
        ret, image_to_process = video_capture.read()
        # video_capture.release()
        # image_to_process = cv2.imread("images/image214.png")
        # image_to_process = cv2.imread("images/image234.png")
        # image_to_process = frame
        cv2.imwrite(f'{camera}_original_images.png', draw_red_zone(image_to_process, camera, 1))
        height, width, _ = image_to_process.shape
        if cadr == 0:
            count = len(os.listdir(r"generateDataset/imgbase")) + 1
            cv2.imwrite(f'generateDataset/imgbase/image{count}.png', image_to_process)
            print(camera, f"Images{count} is saved")
        blob = cv2.dnn.blobFromImage(image_to_process, 1 / 255, (320, 320),
                                     (0, 0, 0), swapRB=True, crop=False)

        class_indexes, class_scores, boxes = ([] for i in range(3))
        #results = model.predict(image_to_process, confidence=50, overlap=90).json()
        results = model.predict(source=draw_red_zone(image_to_process, camera), conf=0.50)
        annotated_image = results[0].plot()  # <-- Используем .plot() для визуализации

        # show_image(annotated_image)
        cv2.imwrite(f'generateDataset/imgPredict/{camera}image{count}.png', annotated_image)

        tN = time.time()
        print(camera, "Detect images", tN - tO)
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
        #print(data_boxes)
        #print(annot_lines)
        free_space = []
        shlak = []
        not_free_space = []
        overlaps = 0

        if annot_lines:
            [free_space, shlak, not_free_space] = await sr.compute_overlaps(annot_lines, camera)

        #print(overlaps)
        print(camera, "Update data")
        tN = time.time()
        print(camera, "Analysis", tN - tO)
        tO = tN
        #sr.draw_bbox(data_boxes[0], "test", image_to_process)

    #cv2.imshow('image', sr.draw_data(image_to_process))
    # sr.delete_shit_in_data()
    # cv2.imshow('image', sr.draw_data(image_to_process, sr.chek_free_space()))
    # cv2.waitKey(0)

    print(camera, "Complite detect")
    foto = await sr.draw_data(cv2.imread(f"{camera}_original_images.png"), [free_space, shlak, not_free_space])
    tN = time.time()
    print(camera, "Rendering", tN - tO)
    tO = tN
    cv2.imwrite(f'generateDataset/imgItog/{camera}image{count}.png', foto)
    return foto, free_space, not_free_space, shlak, camera
        #cv2.waitKey(0)


if __name__ == "main":
    #sr.delete_data()
    #sr.now_all_space_free()
    detect()
