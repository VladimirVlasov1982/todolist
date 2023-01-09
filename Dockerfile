FROM python:3.10-slim

WORKDIR /opt/

EXPOSE 8000

RUN pip install "poetry==1.3.1"
COPY poetry.lock pyproject.toml ./
RUN poetry config virtualenvs.create false \
    && poetry install --no-dev --no-root
COPY . .
ENTRYPOINT ["bash", "entrypoint.sh"]

CMD ["gunicorn", "todolist.wsgi", "-w", "4", "-b", "0.0.0.0:8000"]
