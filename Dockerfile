# FROM python:3
# ENV PYTHONUNBUFFERED 1
# RUN mkdir /code
# WORKDIR /code
# ADD requirements.txt /code/
# RUN pip install -r requirements.txt
# ADD . /code/


# WORKDIR /usr/src/app
# COPY . .
# RUN chmod o+x web-app/runserver.sh \
#     && chmod o+x web-app/initserver.sh \
#     && chmod 777 web-app/token.json
#RUN python3 manage.py makemigrations
#RUN python3 manage.py migrate

# FROM python:3
# WORKDIR /code
# ENV PYTHONUNBUFFERED 1
# ADD requirements.txt /code/
# RUN pip install -r requirements.txt
# ADD . /code/
# RUN chmod o+x web-app/runserver.sh \
#     && chmod o+x web-app/initserver.sh \
#     && chmod 777 web-app/token.json

FROM python:3
ENV PYTHONUNBUFFERED 1
RUN mkdir /code
WORKDIR /code
ADD requirements.txt /code/
RUN pip install -r requirements.txt
ADD . /code/

USER root
# Set permissions
RUN chmod o+x web-app/runserver.sh \
    && chmod o+x web-app/initserver.sh \
    && chmod 777 web-app/token.json

# Run migrations (Uncomment if needed)
# RUN python3 manage.py makemigrations
# RUN python3 manage.py migrate

# Run the application
CMD ["web-app/runserver.sh"]
