FROM python:3.10.1-alpine3.15

ADD . /app/

RUN apk add --no-cache --virtual .build-deps build-base postgresql-libs libpq libpq-dev linux-headers && \
    pip --no-cache-dir install -r /app/requirements.txt && \
    apk del .build-deps && rm -rf /var/cache/apk/*

USER nobody:nogroup

WORKDIR /app

EXPOSE 9999

CMD ["hypercorn", "src/main", "-b", "0.0.0.0:8080"]
