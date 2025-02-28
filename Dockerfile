FROM python:3.10 AS prod
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY ./src ./src
CMD ["python", "./src/main.py"]


FROM prod AS test
COPY ./tests ./tests
CMD ["python", "-m", "pytest"]
