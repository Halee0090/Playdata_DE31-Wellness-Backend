FROM python:3.11

WORKDIR /WELLNESS

COPY ./requirements.txt /WELLNESS/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /WELLNESS/requirements.txt

COPY ./app /WELLNESS/app

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80"]