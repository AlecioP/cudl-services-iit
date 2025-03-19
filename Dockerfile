FROM python:3.12-slim-bullseye

WORKDIR /usr/src/app

ENV PYTHONMALLOC=pymalloc_debug

RUN mkdir data

COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

RUN echo -n 'SECRET_KEY="' > config_key.py
RUN python -c 'import secrets; print(secrets.token_hex(),end="")' >> config_key.py
RUN echo '"' >>config_key.py
COPY config.py ./
# Append newline
RUN echo " " >> config.py 
RUN cat config_key.py >> config.py

COPY apiresource.py ./

ENTRYPOINT waitress-serve --threads $WAITRESS_THREADS --port 5000 wsgi:app >> ./flask.out 2>&1
#ENTRYPOINT python -m flask --app wsgi.py run --host=0.0.0.0 --debug >> ./flask.out 2>&1