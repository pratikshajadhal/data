FROM python:3.9.7-slim 

COPY ./requirements.txt .
RUN pip3 --timeout=300  install -r requirements.txt

COPY . /app
WORKDIR /app/

# expose the port that uvicorn will run the app
EXPOSE 8000
CMD ["python3", "main.py"]
