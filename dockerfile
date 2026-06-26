FROM python:3.14-slim-bookworm
WORKDIR /usr/Documents/img_vote

RUN apt-get update && \
    apt-get install -y nodejs npm && \
    rm -rf /var/lib/apt/lists/*

# Install the application dependencies
COPY python_dependencies.txt ./
RUN pip install --no-cache-dir -r python_dependencies.txt

# Copy in the source code
COPY . .
WORKDIR static
RUN npm install jquery viewerjs tailwindcss @tailwindcss/cli

EXPOSE 5000

WORKDIR /usr/Documents/img_vote

# Setup an app user so the container doesn't run as the root user
RUN useradd -m test && chown -R test:test /usr/Documents/img_vote
USER test

RUN python -c 'import secrets; fx = open("./private_key.txt", "x"); fx.close(); fw = open("./private_key.txt", "w"); fw.write(secrets.token_hex()); fw.close()'

CMD ["flask", "--app", "Home", "run", "--host", "0.0.0.0"]
