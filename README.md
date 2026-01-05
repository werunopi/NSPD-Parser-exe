#### Данная программа создана для парсинга выгруженных объектов **К**адастровых **Н**омеров

> [!WARNING]
> 
> 
> Данный скрипт создан с помощью вайбкодинга.
> 
> Данный скрипт создан исключительно в образовательных целях.

## Установка:

Скачать [NSPD_Parser_DragDrop.exe]([https://github.com/werunopi/NSPD-Parser-api/releases/tag/Stable](https://github.com/werunopi/NSPD-Parser-exe/releases/tag/stable))


## Как использовать:

Сначало выгружаем данные в формате ZIP.

![](https://raw.githubusercontent.com/werunopi/NSPD-Parser-exe/refs/heads/master/zagr.png)

После ZIP-файл перетаскиваем на exe.

Вывод будет CSV-файл в виде:
```
"КН";<перечисление что парсить через точку с запятой в кавычках>
"77:00:0000000:00";<данные объекта в кавычках через точку с запятой>
"77:00:0000000:00";<данные объекта в кавычках через точку с запятой>
```

Пример:
```
"Запрос КН";"Вид объекта недвижимости";"Вид земельного участка"
"77:00:0000000:00";"Земельный участок";"Землепользование"
"77:00:0000000:00";"Земельный участок";"Землепользование"
```
Если данных нет, скрипт запишет в поля `-`.


## Собрать exe самому:
```
pip install -r requirements.txt
pip install pyinstaller
python -m PyInstaller --onefile --console --name NSPD-Parser main.py
```

Скрипт использует библиотеку [NSPD Request](https://github.com/Logar1t/NSPD-request) авторством [Konstantin Telenkov](https://github.com/Logar1t) на лицензии MIT.
