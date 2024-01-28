FROM python:3.11-slim-bullseye

WORKDIR /app

ENV PATH=/venv/bin:$PATH

RUN :\
    && python -m venv /venv \
    && pip install --no-cache-dir pip -U wheel setuptools \
    && :

COPY setup.cfg setup.py top_plays.py ./

RUN :\
    && pip install --no-cache-dir /app/ \
    && :

CMD ["top-plays"]
