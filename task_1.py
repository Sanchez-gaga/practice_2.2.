import requests

urls = [
    "https://github.com/",
    "https://www.binance.com/en",
    "https://tomtit.tomsk.ru/",
    "https://jsonplaceholder.typicode.com/",
    "https://moodle.tomtit-tomsk.ru/"
]

def check_url_status(url):
    try:
        response = requests.get(url, timeout=10, allow_redirects=True)
        code = response.status_code
        if code == 200:
            status = "доступен"
        elif code == 403:
            status = "вход запрещен"
        elif code == 404:
            status = "не найден"
        else:
            status = "не доступен"
        return f"{url} – {status} – {code}"
    except requests.exceptions.RequestException as e:
        return f"{url} – не доступен – ошибка соединения"

def main():
    print("Результаты проверки доступности сайтов:\n")
    for url in urls:
        result = check_url_status(url)
        print(result)

if __name__ == "__main__":
    main()