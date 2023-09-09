# Use the official Python image as base
FROM python:3.9

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file to the container
COPY requirements.txt /app/

# Install the dependencies
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

RUN mkdir -p /app/newspigeon/static

# Copy the rest of the application code to the container
COPY . /app/

# Collect static files for nginx
RUN python manage.py collectstatic --noinput
# Expose the port your application runs on
EXPOSE 8000

# Start the application
CMD ["gunicorn", "--workers=4", "--bind=0.0.0.0:8000", "newspigeon.wsgi:application"]