FROM python:3.11-slim
# Set working directory within the container
WORKDIR /app
# Copy the script into the container
COPY . /app
RUN apt-get update
RUN apt-get install -y libglib2.0-0 libnss3 libnspr4 libatk1.0-0 libcups2 libdbus-1-3 libxkbcommon0 libatspi2.0-0 libx11-6 libxcomposite1 libxdamage1 libxext6 libxfixes3 libxrandr2 libgbm1 libpango-1.0-0 libcairo2 libasound2 libatk-bridge2.0-0 fonts-wqy-zenhei fonts-noto-color-emoji
RUN pip install -r requirements.txt
# Playwright install browser dependencies and the browser itself.
RUN playwright install chromium
# Set the entry point to the script
ENTRYPOINT ["gunicorn", "-w", "4", "-k", "gevent", "-b", "0.0.0.0:14140", "--timeout", "120", "--max-requests", "500", "main:app"]