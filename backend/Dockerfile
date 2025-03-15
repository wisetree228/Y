FROM python:3.12-slim

WORKDIR /app

RUN pip install --upgrade setuptools

COPY requirements.txt .
RUN pip install -r requirements.txt
RUN pip install websockets

COPY . .

EXPOSE 8000

CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]