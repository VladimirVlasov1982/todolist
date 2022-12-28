FROM python:3.10-slim

WORKDIR /app/


RUN pip install "poetry"

COPY poetry.lock pyproject.toml ./
RUN poetry config virtualenvs.create false
RUN poetry install --no-dev --no-interaction --no-ansi --no-root

COPY . .


CMD python3 manage.py runserver 0.0.0.0:8000
