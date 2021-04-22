FROM python:3.8.3-slim-buster
RUN pip install --upgrade pip
RUN pip install Django
RUN pip install ibm_watson
RUN mkdir /ordermngmnt
COPY ordermngmnt /ordermngmnt
WORKDIR /ordermngmnt
RUN python manage.py makemigrations orders
RUN python manage.py migrate 
EXPOSE 8000
CMD ["python","manage.py", "runserver", "0.0.0.0:8000"]