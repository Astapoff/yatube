# YaTube - социальная сеть

## Описание

Cоциальная сеть для публикации личных дневников. 
После регистрации пользователь получает свой профайл, то есть получает свою страницу. 
После публикации каждая запись действительно доступна на странице автора.
Пользователи могут заходить на чужие страницы, подписываться на авторов и комментировать их записи. 
Автор может выбрать для своей страницы имя и уникальный адрес.
Реализована возможность модерировать записи и блокировать пользователей.
Записи можно отправлять в сообщество и смотреть там записи разных авторов.

## Технологии

SQL, HTML, CSS, Django, Bootstrap, Unittest, Pythonanywhere

## Установка

---

Необходимо клонировать проект, сформировать окружение, 
установить зависимости, произвести миграции, и запустить сервер.

**Клонируем репозиторий и заходим в его директорию:**

```shell
git clone https://github.com/Astapoff/yatube.git
cd api_yamdb
```

**Создание окружения:**

```shell
sudo apt install -y python3-venv
python3 -m venv venv
source venv/bin/activate
```

**Установка зависимостей:**

```shell
python -m pip install --upgrade pip
pip3 install -r requirements.txt
```

**Выполнение миграций:**

```shell
python3 manage.py migrate
```

**Запуск сервера:**

```shell
python3 manage.py runserver
```

