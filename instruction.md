# Инструкция к использованию
---

## Добавление новой камеры
---
  - Создать новый лист в файл .xlsx назвав его по имени камеры
  - В файле Cameras.xlsx в лист адреса камеры в первый столбец первой свободной строки написать название камеры (точно также как и файл .xlsx)
  - Если листа нет, предворительно его создать
  - Во второй столбец этой же строки вставить URL стрима камеры
  - Не забыть все сохранить
  - И особенно важно чтобы название камеры точно совпадало с названием созданного файла .xlsx
---
## Первый этап лечения - перезапустить
---
На сервере есть 2 ключевых файла, reinstall.sh и init.sh
Первы отвечает за полную переустановку проекта, а второй за запуск проекта
    В bash строку вбить
  - pkill -f bot.py  -  для завершения работы бота
  - nohup bash init.sh для запуска бота (nohup для запуска в фоне)
  - bash reinstall.sh или bash init.sh для запуска соответствующего файла
---
## Обнуление базы данных через бота
---
  - Обратится к адресу, базу данного которого нужно обнулить, написав его
  - Написать боту dalata dete
---
## О Roboflow
---
      Roboflow выполняет функцию системы контроля версии датасета и нейросети. На этом сайте создан проект, открытый к просмотру, но
    для редактирования нужно зарегестрироваться и получить права на редактирования от владельца проекта. Для этого:
      - Зайти на сайт (https://roboflow.com) и зарегестрироваться
      Со стороны держателя проекта:
      - Дать права на редактирование

[ссылка на проект] (https://app.roboflow.com/parkingai-cyfy5/parking-utku6)
---
## Дополнение датасета
---
  - Cкачать фотографии ч червера из папки (/Parking/parking/generateDataset/imgbase/)
  - Зайти на сайт (https://app.roboflow.com/parkingai-cyfy5/parking-utku6/)
  - В вкладке (Upload data) вставить фото в центральное окно
  - Сохранить (Синяя кнопка справой стороны окна)
  - Перейти во вкладку (Annotate)
  - Выбрать функцию автоматической анатации
  - Подтвердить новоразмеченные фотографиии
  - Во вкладке (Versions) создть новую версию датасета
---
## Обучение нейросети
---
  - Открыть Google colab / Anaconda ну или еще что-то подобное
  - Последовательно выполнить строки
---
    !nvidia-smi
---
    import os
    HOME = os.getcwd()
    print(HOME)
---
    !pip install ultralytics==8.2.103 -q
    from IPython import display
    display.clear_output()
    import ultralytics
    ultralytics.checks()
---
    from ultralytics import YOLO
    from IPython.display import display, Image
---
### Вставить код подкачки последней версии датасета
  - зайти на (https://app.roboflow.com/parkingai-cyfy5/parking-utku6/)
  - Во вкладке (Versions) (Download dataset)
---
    %cd {HOME}
    !yolo task=detect mode=train model=yolov8s.pt data={dataset.location}/data.yaml epochs=25 imgsz=640 plots=True
---
    project.version(dataset.version).deploy(model_type="yolov8", model_path=f"{HOME}/runs/detect/train/")
---













