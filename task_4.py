import urllib.request
import urllib.error
import json
import sys

GITHUB_API_URL = "https://api.github.com"
API_VERSION = "2022-11-28"

def make_request(url, token=None):
    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": API_VERSION,
        "User-Agent": "Python-GitHub-Client"
    }
    if token:
        headers["Authorization"] = f"token {token}"
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode('utf-8'))
            return data
    except urllib.error.HTTPError as e:
        print(f"Ошибка HTTP {e.code}: {e.reason}")
        return None
    except urllib.error.URLError as e:
        print(f"Ошибка соединения: {e.reason}")
        return None
    except json.JSONDecodeError:
        print("Ошибка разбора JSON.")
        return None

def get_user_profile(username, token=None):
    url = f"{GITHUB_API_URL}/users/{username}"
    data = make_request(url, token)
    if not data:
        return
    if "message" in data and data["message"] == "Not Found":
        print(f"Пользователь '{username}' не найден.")
        return
    print(f"\n=== ПРОФИЛЬ ПОЛЬЗОВАТЕЛЯ: {username} ===")
    print(f"Имя: {data.get('name', 'не указано')}")
    print(f"Ссылка на профиль: {data.get('html_url', 'нет')}")
    print(f"Количество репозиториев: {data.get('public_repos', 0)}")
    print(f"Количество обсуждений (дискуссий): {data.get('public_gists', 0)}")
    print(f"Количество подписок (кто отслеживает пользователя): {data.get('following', 0)}")
    print(f"Количество подписчиков: {data.get('followers', 0)}")
    print()

def get_user_repos(username, token=None):
    url = f"{GITHUB_API_URL}/users/{username}/repos?per_page=100&sort=updated"
    repos = make_request(url, token)
    if not repos:
        return
    if isinstance(repos, dict) and "message" in repos:
        print(f"Ошибка: {repos.get('message')}")
        return
    if not repos:
        print("У пользователя нет публичных репозиториев.")
        return
    print(f"\n=== РЕПОЗИТОРИИ ПОЛЬЗОВАТЕЛЯ: {username} ===")
    for repo in repos:
        name = repo.get('name')
        html_url = repo.get('html_url')
        language = repo.get('language', 'не указан')
        visibility = "приватный" if repo.get('private') else "публичный"
        default_branch = repo.get('default_branch')
        views = "недоступно"
        if token:
            views_url = f"{GITHUB_API_URL}/repos/{username}/{name}/traffic/views"
            views_data = make_request(views_url, token)
            if views_data and 'count' in views_data:
                views = views_data['count']
            elif views_data and 'message' in views_data:
                views = f"ошибка: {views_data['message']}"
        print(f"\nНазвание: {name}")
        print(f"Ссылка: {html_url}")
        print(f"Просмотров (за 14 дней): {views}")
        print(f"Язык: {language}")
        print(f"Видимость: {visibility}")
        print(f"Ветка по умолчанию: {default_branch}")
        print("-" * 40)
    print()

def search_repos(query, token=None):
    import urllib.parse
    encoded_query = urllib.parse.quote(query)
    url = f"{GITHUB_API_URL}/search/repositories?q={encoded_query}&per_page=10"
    data = make_request(url, token)
    if not data:
        return
    if "message" in data:
        print(f"Ошибка поиска: {data['message']}")
        return
    items = data.get('items', [])
    total = data.get('total_count', 0)
    print(f"\n=== РЕЗУЛЬТАТЫ ПОИСКА ПО ЗАПРОСУ: '{query}' ===")
    print(f"Найдено: {total} репозиториев (показываю первые 10)\n")
    if not items:
        print("Ничего не найдено.")
        return
    for repo in items:
        name = repo.get('full_name')
        html_url = repo.get('html_url')
        language = repo.get('language', 'не указан')
        visibility = "приватный" if repo.get('private') else "публичный"
        print(f"Название: {name}")
        print(f"Ссылка: {html_url}")
        print(f"Язык: {language}")
        print(f"Видимость: {visibility}")
        print("-" * 40)
    print()

def get_token():
    print("Для доступа к некоторым данным (например, количество просмотров) рекомендуется использовать токен.")
    print("Вы можете получить токен на https://github.com/settings/tokens")
    choice = input("Хотите ввести токен? (y/n): ").strip().lower()
    if choice == 'y':
        return input("Введите токен: ").strip()
    return None

def main():
    print("=== GitHub API Клиент ===")
    token = get_token()
    if token:
        print("Токен загружен.")
    else:
        print("Работаем без токена (некоторые функции могут быть ограничены).")

    while True:
        print("\n=== МЕНЮ ===")
        print("1. Просмотр профиля пользователя")
        print("2. Получение репозиториев пользователя")
        print("3. Поиск репозиториев по названию")
        print("4. Выход")
        choice = input("Выберите действие: ").strip()

        if choice == '1':
            username = input("Введите имя пользователя GitHub: ").strip()
            if username:
                get_user_profile(username, token)
            else:
                print("Имя не может быть пустым.")
        elif choice == '2':
            username = input("Введите имя пользователя GitHub: ").strip()
            if username:
                get_user_repos(username, token)
            else:
                print("Имя не может быть пустым.")
        elif choice == '3':
            query = input("Введите название (или часть названия) репозитория: ").strip()
            if query:
                search_repos(query, token)
            else:
                print("Запрос не может быть пустым.")
        elif choice == '4':
            print("До свидания!")
            break
        else:
            print("Неверный выбор. Попробуйте снова.")

if __name__ == "__main__":
    main()