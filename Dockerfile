FROM python:3.12


WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev gcc git \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip and setuptools with increased timeout and alternative mirror
RUN pip install --no-cache-dir --upgrade pip setuptools wheel --timeout=100 -i https://pypi.org/simple

# Copy the requirements file into the container
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt --timeout=100 -i https://pypi.org/simple

# Copy the rest of the application code
COPY . .

# Expose port for the Django development server
EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
