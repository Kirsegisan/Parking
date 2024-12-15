from roboflow import Roboflow
import cv2
import os


rf = Roboflow(api_key="kmdwHagZQlYas7gzGfw9")
project = rf.workspace("parkingai-cyfy5").project("parking-utku6")
model = project.version(9).model


def delete_files_in_folder(folder_path):
    for root, dirs, files in os.walk(folder_path):
        for file_name in files:
            file_path = os.path.join(root, file_name)
            try:
                os.unlink(file_path)
            except Exception as e:
                print(f"Error deleting file: {file_path} -- {e}")

directory = r"imgbase"
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
    results = model.predict(image_to_process, confidence=50, overlap=90).json()
    
    annot_lines = []
    for i in results["predictions"]:
            annotation = [i['x'] - i["width"]/2, i['y'] - i["height"]/2, i["width"], i["height"]]
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
