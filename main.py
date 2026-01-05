import sys
import csv
import time
import os
import re
import zipfile
import io
from nspd_request import NSPD

FIELDS = [
    "Вид объекта недвижимости", "Вид земельного участка", "Дата присвоения",
    "Кадастровый номер", "Кадастровый квартал", "Адрес",
    "Площадь уточненная", "Площадь декларированная", "Площадь",
    "Статус", "Категория земель", "Вид разрешенного использования",
    "Форма собственности", "Кадастровая стоимость"
]


def clean_value(val):
    """Заменяет пустые значения и 'н/д' на дефис"""
    if not val or val == "н/д" or val is None:
        return "-"
    return str(val)


def parse_api_response(data, kn):
    """Превращает ответ API в список для CSV"""
    if not data or "error" in data or "data" not in data or not data["data"].get("features"):
        row = ["-"] * len(FIELDS)
        row[3] = kn
        return row

    try:
        feature = data["data"]["features"][0]
        props = feature.get("properties", {})
        opt = props.get("options", {})

        meta_cat = ""
        if data.get("meta") and len(data["meta"]) > 0:
            meta_cat = data["meta"][0].get("categoryName", "")

        mapping = {
            "Вид объекта недвижимости": opt.get("land_record_type") or meta_cat or props.get("categoryName") or "-",
            "Вид земельного участка": opt.get("land_record_subtype") or "-",
            "Дата присвоения": opt.get("land_record_reg_date") or "-",
            "Кадастровый номер": opt.get("cad_num") or data.get("kad_number") or kn,
            "Кадастровый квартал": opt.get("quarter_cad_number") or opt.get("kvartal") or "-",
            "Адрес": opt.get("readable_address") or props.get("address") or "-",
            "Площадь уточненная": opt.get("specified_area") or "-",
            "Площадь декларированная": opt.get("declared_area") or "-",
            "Площадь": opt.get("area_value") or opt.get("specified_area") or "-",
            "Статус": opt.get("status") or opt.get("state_cd") or "-",
            "Категория земель": opt.get("land_record_category_type") or opt.get("category_code") or "-",
            "Вид разрешенного использования": opt.get("permitted_use_established_by_document") or opt.get(
                "util_code") or "-",
            "Форма собственности": opt.get("ownership_type") or opt.get("right_form") or "-",
            "Кадастровая стоимость": f"{opt['cost_value']} руб." if opt.get("cost_value") else "-"
        }

        return [clean_value(mapping[f]) for f in FIELDS]

    except Exception as e:
        print(f"Ошибка обработки JSON для {kn}: {e}")
        return ["Error"] * len(FIELDS)


def extract_kns_from_stream(f_obj):
    """Ищет кадастровые номера в текстовом потоке"""
    kns = []
    content = f_obj.read()
    f_obj.seek(0)

    reader = csv.DictReader(io.StringIO(content))
    target_col = None

    if reader.fieldnames:
        if "Наименование объекта" in reader.fieldnames:
            target_col = "Наименование объекта"
        elif "Кадастровый номер" in reader.fieldnames:
            target_col = "Кадастровый номер"

    if target_col:
        for row in reader:
            if row.get(target_col):
                kns.append(row[target_col].strip())
    else:
        kns = re.findall(r'\d{2}:\d{2}:\d{6,7}:\d+', content)

    return kns


def process_csv(input_path):
    print(f"--- ЗАПУСК ПАРСЕРА ---")
    print(f"Входной путь: {input_path}")

    api = NSPD()
    kns = []

    is_zip = input_path.lower().endswith('.zip')

    try:
        if is_zip:
            with zipfile.ZipFile(input_path, 'r') as z:
                csv_in_zip = [name for name in z.namelist() if name.lower().endswith('.csv')]
                if not csv_in_zip:
                    print("В архиве не найдено CSV файлов!")
                    return

                print(f"Обработка файла из архива: {csv_in_zip[0]}")
                with z.open(csv_in_zip[0]) as f_raw:
                    # Оборачиваем байтовый поток в текст
                    with io.TextIOWrapper(f_raw, encoding='utf-8-sig') as f_text:
                        kns = extract_kns_from_stream(f_text)
        else:
            with open(input_path, 'r', encoding='utf-8-sig') as f:
                kns = extract_kns_from_stream(f)

    except Exception as e:
        print(f"Ошибка при чтении файла: {e}")
        input("Нажмите Enter...")
        return

    if not kns:
        print("Кадастровые номера не найдены.")
        input("Нажмите Enter...")
        return

    unique_kns = list(dict.fromkeys(kns))
    print(f"Найдено уникальных номеров: {len(unique_kns)}")

    dir_name = os.path.dirname(input_path)
    base_name = os.path.basename(input_path).rsplit('.', 1)[0]
    output_file = os.path.join(dir_name, f"{base_name}_PARSED.csv")

    print("Начинаем парсинг через API...")
    with open(output_file, 'w', encoding='utf-8-sig', newline='') as f_out:
        writer = csv.writer(f_out, delimiter=';', quoting=csv.QUOTE_ALL)
        writer.writerow(FIELDS)

        for i, kn in enumerate(unique_kns):
            kn = kn.strip()
            print(f"[{i + 1}/{len(unique_kns)}] {kn}", end=" ... ")

            data = api.get_object_info(kn)
            row = parse_api_response(data, kn)

            writer.writerow(row)
            print("OK")
            time.sleep(0.05)

    print("-" * 30)
    print("ГОТОВО!")
    print(f"Результат сохранен в: {output_file}")
    print("-" * 30)
    input("Нажмите Enter, чтобы закрыть это окно...")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        process_csv(sys.argv[1])
    else:
        print("Инструкция: перетащите CSV или ZIP файл на этот EXE.")
        input("Нажмите Enter для выхода...")