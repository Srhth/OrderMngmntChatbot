FROM python:3.6.1-alpine
RUN pip install Django
RUN pip install ibm_watson
RUN mkdir /ordermngmnt
COPY ordermngmnt /ordermngmnt
WORKDIR /ordermngmnt
EXPOSE 8000
CMD ["python","manage.py", "runserver", "0.0.0.0:8000"]