FROM python:3.11 AS prod

ENV PYTHONUNBUFFERED 1
ENV DJANGO_SETTINGS_MODULE=InsuranceClaimsAPI.settings

WORKDIR /app

# Copy requirements and install them
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the full project (including MLModel folder)
COPY . .

# Install the ML module
RUN pip install -e .

# Train the model before launching the app
RUN python MLModel/model_trainer.py

# Collect static files
RUN python manage.py collectstatic --noinput

# Start Django
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "InsuranceClaimsAPI.wsgi:application"]
