import json
import os
import urllib.request
import urllib.error

URL = "https://www.cbr-xml-daily.ru/daily_json.js"
SAVE_FILE = "save.json"

def load_groups():
    if os.path.exists(SAVE_FILE):
        try:
            with open(SAVE_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return {}
    return {}

def save_groups(groups):
    with open(SAVE_FILE, 'w', encoding='utf-8') as f:
        json.dump(groups, f, indent=4, ensure_ascii=False)

def fetch_rates():
    try:
        req = urllib.request.Request(URL, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as response:
            if response.getcode() != 200:
                print(f"Ошибка HTTP: {response.getcode()}")
                return None
            data = json.loads(response.read().decode('utf-8'))
            return data['Valute']
    except urllib.error.URLError as e:
        print(f"Ошибка соединения: {e.reason}")
    except json.JSONDecodeError:
        print("Ошибка разбора JSON.")
    except KeyError:
        print("Некорректная структура данных.")
    return None

def show_all_rates(rates):
    if not rates:
        print("Нет данных для отображения.")
        return
    print("\n=== КУРСЫ ВАЛЮТ (за 1 единицу валюты) ===")
    for code, info in sorted(rates.items()):
        print(f"{code} ({info['Name']}): {info['Value']:.4f} руб.")
    print()

def show_single_rate(rates, code):
    if not rates:
        print("Нет данных.")
        return
    code_upper = code.upper()
    if code_upper in rates:
        info = rates[code_upper]
        print(f"{code_upper} ({info['Name']}): {info['Value']:.4f} руб.\n")
    else:
        print(f"Валюта с кодом {code} не найдена.\n")

def manage_groups(groups):
    while True:
        print("\n=== УПРАВЛЕНИЕ ГРУППАМИ ===")
        print("1. Создать новую группу")
        print("2. Просмотреть все группы")
        print("3. Изменить группу")
        print("4. Удалить группу")
        print("5. Вернуться в главное меню")
        choice = input("Выберите действие: ").strip()
        if choice == '1':
            create_group(groups)
        elif choice == '2':
            show_groups(groups)
        elif choice == '3':
            edit_group(groups)
        elif choice == '4':
            delete_group(groups)
        elif choice == '5':
            break
        else:
            print("Неверный выбор. Попробуйте снова.")

def create_group(groups):
    name = input("Введите название группы: ").strip()
    if not name:
        print("Название не может быть пустым.")
        return
    if name in groups:
        print(f"Группа с именем '{name}' уже существует.")
        return
    codes = input("Введите коды валют через пробел (например, USD EUR GBP): ").strip().upper().split()
    groups[name] = codes
    save_groups(groups)
    print(f"Группа '{name}' создана с валютами: {', '.join(codes)}")

def show_groups(groups):
    if not groups:
        print("Нет сохранённых групп.")
        return
    print("\n=== СПИСОК ГРУПП ===")
    for name, codes in groups.items():
        print(f"{name}: {', '.join(codes) if codes else '(пусто)'}")
    print()

def edit_group(groups):
    if not groups:
        print("Нет групп для редактирования.")
        return
    show_groups(groups)
    name = input("Введите название группы для редактирования: ").strip()
    if name not in groups:
        print("Группа не найдена.")
        return
    current_codes = groups[name]
    while True:
        print(f"\nРедактирование группы '{name}'")
        print(f"Текущие валюты: {', '.join(current_codes) if current_codes else '(пусто)'}")
        print("1. Добавить валюту")
        print("2. Удалить валюту")
        print("3. Завершить редактирование")
        sub = input("Выберите: ").strip()
        if sub == '1':
            add_code = input("Введите код валюты для добавления: ").strip().upper()
            if add_code not in current_codes:
                current_codes.append(add_code)
                print(f"Валюта {add_code} добавлена.")
            else:
                print(f"Валюта {add_code} уже есть в группе.")
            groups[name] = current_codes
            save_groups(groups)
        elif sub == '2':
            if not current_codes:
                print("В группе нет валют для удаления.")
                continue
            remove_code = input("Введите код валюты для удаления: ").strip().upper()
            if remove_code in current_codes:
                current_codes.remove(remove_code)
                print(f"Валюта {remove_code} удалена.")
            else:
                print(f"Валюта {remove_code} не найдена в группе.")
            groups[name] = current_codes
            save_groups(groups)
        elif sub == '3':
            break
        else:
            print("Неверный выбор.")

def delete_group(groups):
    if not groups:
        print("Нет групп для удаления.")
        return
    show_groups(groups)
    name = input("Введите название группы для удаления: ").strip()
    if name in groups:
        del groups[name]
        save_groups(groups)
        print(f"Группа '{name}' удалена.")
    else:
        print("Группа не найдена.")

def view_group_rates(groups, rates):
    if not groups:
        print("Нет сохранённых групп.")
        return
    show_groups(groups)
    name = input("Введите название группы для просмотра: ").strip()
    if name not in groups:
        print("Группа не найдена.")
        return
    codes = groups[name]
    if not codes:
        print("Группа пуста.")
        return
    print(f"\n=== КУРСЫ ВАЛЮТ ИЗ ГРУППЫ '{name}' ===")
    for code in codes:
        if code in rates:
            info = rates[code]
            print(f"{code} ({info['Name']}): {info['Value']:.4f} руб.")
        else:
            print(f"{code}: не найдена в текущих курсах")
    print()

def main():
    groups = load_groups()
    print("Загрузка курсов валют...")
    rates = fetch_rates()
    if rates is None:
        return

    while True:
        print("\n=== ГЛАВНОЕ МЕНЮ ===")
        print("1. Показать курсы всех валют")
        print("2. Показать курс конкретной валюты")
        print("3. Показать курсы валют из группы")
        print("4. Управление группами")
        print("5. Выход")
        choice = input("Выберите действие: ").strip()

        if choice == '1':
            show_all_rates(rates)
        elif choice == '2':
            code = input("Введите код валюты (например, USD): ").strip()
            show_single_rate(rates, code)
        elif choice == '3':
            view_group_rates(groups, rates)
        elif choice == '4':
            manage_groups(groups)
        elif choice == '5':
            print("До свидания!")
            break
        else:
            print("Неверный выбор. Попробуйте снова.")

if __name__ == "__main__":
    main()