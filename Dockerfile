FROM python:3.12-slim-bullseye

WORKDIR /usr/src/app

ENV PYTHONMALLOC=pymalloc_debug

RUN mkdir data

COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

RUN echo -n 'SECRET_KEY="' > config.py
RUN python -c 'import secrets; print(secrets.token_hex(),end="")' >> config.py
RUN echo '"' >>config.py


ENTRYPOINT waitress-serve --threads $WAITRESS_THREADS --port 5000 wsgi:app >> ./flask.out 2>&1
#ENTRYPOINT python -m flask --app wsgi.py run --host=0.0.0.0 --debug >> ./flask.out 2>&1
