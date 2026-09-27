FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . .

EXPOSE 5000

# Use environment variable OPENWEATHER_API_KEY to provide API key
CMD ["python", "backend/app.py"]
