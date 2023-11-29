FROM python:3.10-slim-bullseye

WORKDIR /app

ENV PATH=/venv/bin:$PATH

COPY setup.cfg setup.py .

RUN :\
    && python -m venv /venv \
    && pip install --no-cache-dir pip -U wheel setuptools /app/ \
    && :

COPY top_plays.py start.py rollback.py .

RUN ./start.py

CMD ["python",  "top_plays.py"]
