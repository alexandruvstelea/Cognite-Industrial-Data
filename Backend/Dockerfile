FROM python:3.10

WORKDIR /Backend

COPY Backend/Requirements.txt .

RUN pip install --no-cache-dir -r Requirements.txt


EXPOSE 5000

COPY Backend/Flask/flask_backend.py .
COPY jsonFiles ./jsonFiles

CMD ["python", "./flask_backend.py"]