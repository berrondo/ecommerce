FROM python:3.8
ENV PYTHONUNBUFFERED=1
RUN mkdir /code
WORKDIR /code
COPY requirements.txt /code/
RUN pip install -r requirements.txt
#RUN cp /ecommerce/contrib/env_sample /code/.env
#RUN python manage.py migrate
#RUN python manage.py createsuperuser --email a@a.com --no-input
#RUN python manage.py loaddata 'store.json'
COPY . /code/