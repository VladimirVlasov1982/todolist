# Планировщик задач
***
Поможет создавать задачи и контролировать сроки их выполнения

* стек (python3.10.4, Django, Postgres)
***
### Подготовка проекта
Установите зависимости проекта
```
pip install -r requirements.txt
```
Установите docker-контейнер с уже готовой и настроенной СУБД:
```
docker run --name todolist-skypro -e POSTGRES_PASSWORD=postgres -p 5432:5432 -d postgres
```