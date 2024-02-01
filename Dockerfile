FROM python:3.11-slim as requirements-stage

WORKDIR /tmp

RUN pip install pdm

COPY ./pyproject.toml ./pdm.lock* /tmp/

RUN pdm export --dev --without-hashes -f requirements -o requirements.txt 

FROM python:3.11-slim

WORKDIR /code

COPY --from=requirements-stage /tmp/requirements.txt /code/requirements.txt

RUN pip install -U --no-cache-dir -r /code/requirements.txt

COPY . /code

COPY ./start-dev /start-dev
RUN chmod +x /start-dev

ENV PYTHONPATH /code

CMD ["./start-dev"]
