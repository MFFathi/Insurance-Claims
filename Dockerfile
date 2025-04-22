FROM python:3.11 AS prod

ENV PYTHONUNBUFFERED 1

WORKDIR /app

# Copy requirements and install them
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the full project (including MLModel folder)
COPY . .

# Train the model before launching the app
RUN python MLModel/model_trainer.py

# Start Django
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "InsuranceClaims.wsgi:application"]
