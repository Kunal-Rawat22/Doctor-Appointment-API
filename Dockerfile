FROM python:3.12-slim

WORKDIR /app
# Install dependencies
RUN pip install --upgrade pip

# Install compatible passlib + bcrypt
RUN pip install "passlib[bcrypt]==1.7.4" "bcrypt==4.0.1"

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", "8000"]
