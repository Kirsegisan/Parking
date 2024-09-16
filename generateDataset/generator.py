import cv2
import os
from ultralytics import YOLO

model = YOLO('../YOLO-weights/best (1).pt')


def delete_files_in_folder(folder_path):
    for root, dirs, files in os.walk(folder_path):
        for file_name in files:
            file_path = os.path.join(root, file_name)
            try:
                os.unlink(file_path)
            except Exception as e:
                print(f"Error deleting file: {file_path} -- {e}")

directory = r"D:/MyApp/Parking/generateDataset/imgbase"
train_images_path = 'images/train/images'
train_labels_path = 'images/labels/images'
img_list = os.listdir(directory)
print(f"В папке имеется {len(img_list)} изображений")

delete_files_in_folder('images/train/images')
delete_files_in_folder('images/train/labels')

for img_name in img_list:
    img_filepath = directory + "\\" + img_name
    print(img_filepath)
    img = cv2.imread(img_filepath)
    img_copy = img

    # предобработка изображения как перед обучением
    # gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # gray_three = cv2.merge([gray,gray,gray])
    # img = gray_three

    # получаем ширину и высоту картинки
    h, w, _ = img.shape

    # получаем предсказания по картинке
    results = model.predict(source=img, conf=0.50)

    # расшифровываем объект results
    bboxes_ = results[0].boxes.xyxy.tolist()
    bboxes = list(map(lambda x: list(map(lambda y: int(y), x)), bboxes_))
    confs_ = results[0].boxes.conf.tolist()
    confs = list(map(lambda x: int(x * 100), confs_))
    classes_ = results[0].boxes.cls.tolist()
    classes = list(map(lambda x: int(x), classes_))
    cls_dict = results[0].names
    class_names = list(map(lambda x: cls_dict[x], classes))

    # приводим дешифрированные данные в удобный вид
    annot_lines = []
    for index, val in enumerate(class_names):
        xmin, ymin, xmax, ymax = int(bboxes[index][0]), int(bboxes[index][1]), int(bboxes[index][2]), int(
            bboxes[index][3])
        width = xmax - xmin
        height = ymax - ymin
        center_x = xmin + (width / 2)
        center_y = ymin + (height / 2)
        annotation = f"{classes[index]} {center_x / w} {center_y / h} {width / w} {height / h}"
        annot_lines.append(annotation)

    # копируем картинку в папку базы изображений для импорта
    cv2.imwrite(os.path.join(train_images_path, img_name), img_copy)


    # записываем файл аннотации в папку базы изображений для импорта
    if "jpg" in img_name:
        txt_name = img_name.replace(".jpg", ".txt")
    if "png" in img_name:
        txt_name = img_name.replace(".png", ".txt")
    #cv2.imwrite(os.path.join(train_labels_path, txt_name), img_copy)

    with open(f'images/train/labels/{txt_name}', 'w') as f:
        for line in annot_lines:
            f.write(line)
            f.write('\n')
