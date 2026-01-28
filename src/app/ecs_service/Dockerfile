FROM public.ecr.aws/docker/library/python:3.12-slim
WORKDIR /app

COPY src/app/ecs_service/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY src/app/ecs_service/app.py ./app.py
COPY src/common ./common
COPY src/models ./models

ENV PYTHONPATH=/app
EXPOSE 8080

CMD ["gunicorn", "-w", "2", "-b", "0.0.0.0:8080", "app:app"]
