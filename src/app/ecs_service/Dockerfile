FROM python:3.12-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code (must exist in build context)
COPY app.py ./app.py
COPY common ./common
COPY models ./models

# Make /app importable (so: import common works)
ENV PYTHONPATH=/app

EXPOSE 8080

CMD ["gunicorn", "-w", "2", "-b", "0.0.0.0:8080", "app:app"]
