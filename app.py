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


class NoImgError(Exception):
    pass


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
    # Засекаем время начала операции
    tO = time.time()
    print(camera, video_path)

    # Инициализация захвата видео
    video_capture = cv2.VideoCapture(video_path)

    # Замер времени подключения к камере
    tN = time.time()
    print(camera, "Connect camera", tN - tO)
    tO = tN

    # Чтение первого кадра из видео
    ret, image_to_process = video_capture.read()

    # Сохранение оригинального изображения с нарисованной красной зоной
    cv2.imwrite(f'{camera}_original_images.png', draw_red_zone(image_to_process, camera, 1))

    # Получение размеров изображения
    height, width, _ = image_to_process.shape

    # Подсчет существующих файлов для генерации уникального имени
    count = len(os.listdir(r"generateDataset/imgbase")) + 1

    # Сохранение оригинального изображения в базу
    cv2.imwrite(f'generateDataset/imgbase/image{count}.png', image_to_process)
    print(camera, f"Images{count} is saved")

    # Инициализация списков для хранения результатов детекции
    class_indexes, class_scores, boxes = ([] for i in range(3))

    # Выполнение предсказания модели YOLO на обработанном изображении
    results = model.predict(source=draw_red_zone(image_to_process, camera), conf=0.50)

    # Визуализация результатов детекции
    annotated_image = results[0].plot()  # <-- Используем .plot() для визуализации

    # Сохранение аннотированного изображения
    cv2.imwrite(f'generateDataset/imgPredict/{camera}image{count}.png', annotated_image)

    # Замер времени выполнения детекции
    tN = time.time()
    print(camera, "Detect images", tN - tO)
    tO = tN

    # Извлечение bounding boxes в формате [xmin, ymin, xmax, ymax]
    bboxes_ = results[0].boxes.xyxy.tolist()
    bboxes = list(map(lambda x: list(map(lambda y: int(y), x)), bboxes_))

    # Извлечение уверенностей и приведение к процентам
    confs_ = results[-1].boxes.conf.tolist()
    confs = list(map(lambda x: int(x * 100), confs_))

    # Извлечение классов объектов
    classes_ = results[-1].boxes.cls.tolist()
    classes = list(map(lambda x: int(x), classes_))

    # Получение словаря имен классов
    cls_dict = results[-1].names
    class_names = list(map(lambda x: cls_dict[x], classes))

    # Подготовка данных для аннотаций
    annot_lines = []
    for index, val in enumerate(class_names):
        # Извлечение координат bounding box
        xmin, ymin, xmax, ymax = int(bboxes[index][0]), int(bboxes[index][1]), int(bboxes[index][2]), int(
            bboxes[index][3])

        # Вычисление размеров и центра bounding box
        widthBox = xmax - xmin
        heightBox = ymax - ymin
        center_x = xmin + (widthBox / 2)
        center_y = ymin + (heightBox / 2)

        # Формирование аннотации в формате [x, y, width, height]
        annotation = [center_x - (widthBox / 2), center_y - (heightBox / 2), widthBox, heightBox]
        annot_lines.append(annotation)

    # Инициализация списков для классификации пространства
    free_space = []
    shlak = []
    not_free_space = []
    # Логирование времени анализа)
    tN = time.time()
    if annot_lines:
        # Анализ пересечений bounding boxes
        free_space, shlak, not_free_space = await sr.compute_overlaps(annot_lines, camera)


    print(camera, "Analysis", tN - tO)
    tO = tN

    # Финализация процесса детекции
    print(camera, "Complite detect")

    # Визуализация результатов классификации пространства
    foto = await sr.draw_data(cv2.imread(f"{camera}_original_images.png"), free_space, shlak, not_free_space)

    # Замер времени рендеринга
    tN = time.time()
    print(camera, "Rendering", tN - tO)
    tO = tN

    # Сохранение итогового изображения
    cv2.imwrite(f'generateDataset/imgItog/{camera}image{count}.png', foto)

    # Возврат результатов
    return foto, free_space, not_free_space, shlak, camera


if __name__ == "main":
    #sr.delete_data()
    #sr.now_all_space_free()
    detect()
