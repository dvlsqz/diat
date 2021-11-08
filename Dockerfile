FROM python:3.6-alpine

# Copy in your requirements file
ADD requirements.txt /requirements.txt

# OR, if you’re using a directory for your requirements, copy everything (comment out the above and uncomment this if so):
# ADD requirements /requirements

# Install build deps, then run `pip install`, then remove unneeded build deps all in a single step. Correct the path to your production requirements file, if needed.
RUN set -ex \
    && apk add nginx \
	curl \
	supervisor\
    && apk add --no-cache --virtual .build-deps \
            gcc \
            make \
            libc-dev \
            musl-dev \
            linux-headers \
            pcre-dev \
            mysql-dev \
            libxslt-dev \
            libxml2-dev \
            python3-dev \
            libffi-dev \
            libressl-dev \
            # Zona Horaria se borra al establecerla
            tzdata \
            # Pillow
            jpeg-dev \
            zlib-dev \
            freetype-dev \
            lcms2-dev \
            openjpeg-dev \
            tiff-dev \
            tk-dev \
            tcl-dev \
            harfbuzz-dev \
            fribidi-dev \
    && pyvenv /venv \
    && /venv/bin/pip install -U pip \
    && /venv/bin/pip install -U uwsgi\
    && cp /usr/share/zoneinfo/America/Guatemala /etc/localtime \
    && echo "America/Guatemala" >  /etc/timezone \
    && LIBRARY_PATH=/lib:/usr/lib /bin/sh -c "/venv/bin/pip install --no-cache-dir -r /requirements.txt" \
    && runDeps="$( \
            scanelf --needed --nobanner --recursive /venv \
                    | awk '{ gsub(/,/, "\nso:", $2); print "so:" $2 }' \
                    | sort -u \
                    | xargs -r apk info --installed \
                    | sort -u \
    )" \
    && apk add --virtual .python-rundeps $runDeps \
    && apk del .build-deps

# Copy your application code to the container (make sure you create a .dockerignore file if any large files or directories should be excluded)
WORKDIR /var/html
ADD . /var/html

# Setup all the configfiles and nginx
ADD config/nginx.conf /etc/nginx/nginx.conf
ADD config/nginx-default.conf /etc/nginx/conf.d/default.conf
ADD config/nginx-app.conf /etc/nginx/sites-available/default
ADD config/supervisor-app.conf /etc/supervisor/conf.d/
RUN mkdir -p /run/nginx

# uWSGI will listen on this port
EXPOSE 80

# Add any custom, static environment variables needed by Django or your settings file here:
ENV DJANGO_SETTINGS_MODULE=nutricion_igss.settings

# Call collectstatic (customize the following line with the minimal environment variables needed for manage.py to run):
RUN DATABASE_URL=none /venv/bin/python manage.py collectstatic --noinput

# Entrypoint
ENTRYPOINT ["/var/html/config/docker-entrypoint.sh"]

# Start
CMD ["supervisord", "-n", "-c", "/var/html/config/supervisor-app.conf"]