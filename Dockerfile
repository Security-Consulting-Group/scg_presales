FROM python:3.12-alpine

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install system dependencies
RUN apk update \
    && apk add --no-cache gcc musl-dev postgresql-dev python3-dev libffi-dev \
    && apk add --no-cache cairo-dev pango-dev gdk-pixbuf-dev \
    && apk add --no-cache fontconfig ttf-dejavu \
    && pip install --upgrade pip

# Set work directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy project
COPY . .

# Create staticfiles directory
RUN mkdir -p staticfiles

# Expose port
EXPOSE 8000

# Make entrypoint executable
RUN chmod +x entrypoint.sh

# Run entrypoint script
CMD ["sh", "entrypoint.sh"]