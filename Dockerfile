FROM rapidfort/python-chromedriver:latest
WORKDIR /opt/airflow

# Install required system-level dependencies
# RUN apt-get update && \
#     apt-get install -y wget ca-certificates unzip curl gnupg jq --no-install-recommends && \
#     apt-get clean && rm -rf /var/lib/apt/lists/*
RUN apt-get update && apt-get install -y \
    gcc \
    libffi-dev \
    libssl-dev \
    python3-dev \
    build-essential

RUN pip install apache-airflow==2.10.3

# Install pip packages in stages to avoid conflicts
RUN pip install selenium bs4 azure-cli==2.65.0 webdriver_manager pandas

# Copy your application code
COPY ./ETL.py .
COPY ./dags ./dags

ENV AIRFLOW_HOME=/opt/airflow

# Command to execute the script
# CMD ["python3", "ETL.py"]
CMD ["airflow", "standalone"]