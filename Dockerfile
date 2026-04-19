FROM python:3.10

WORKDIR /workspace

# Copy the entire project spanning both backend and ai_engine, including .env
COPY . /workspace/

# Install dependencies
RUN pip install -r backend/requirements.txt

# Shift working directory to backend so `app.main` can be discovered properly
WORKDIR /workspace/backend

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
