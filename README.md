# SSD-G29

## Prerequisites

Ensure the following are installed on **Windows** before proceeding

* [Python 3.13](https://www.python.org/downloads/)
* [Docker Desktop](https://www.docker.com/products/docker-desktop/)
* [PostgreSQL Client](https://www.postgresql.org/download/)

## Flask app

Create an environment

```bat
py -3 -m venv .venv
```

Activate the environment

```bat
.venv\Scripts\activate
```

OPTIONAL: export all install package into requirements.txt

```bat
pip freeze > requirements.txt
```

Install Dependencies from requirements.txt

```bat
pip install -r requirements.txt
```

Run the Flask app

```bat
python app.py
```

<hr style="width:100%; height:1px; border:none; background-color:#ccc;">
Setup environment variables

1. Create `.env` file using `.env.example` as a template.
2. Create `.env.production` file using `.env.example` as a template.

<hr style="width:100%; height:1px; border:none; background-color:#ccc;">

## Docker

**Ensure Docker Desktop is running**

Build and run container (Development)

```bat
docker compose --env-file .env up --build -d
```

Build and run container (Production)

```bat
docker compose --env-file .env.production up --build -d
```

Stop container

```bat
docker compose down
```

Stop container (Production)

```bat
 docker compose --env-file .env.production down
```

Completely remove everything (containers, networks, volumes, and images)

```bat
docker compose down --volumes --rmi all --remove-orphans
```

Connect to PostgreSQL database in container.

```bat
psql -h localhost -p 8888 -U postgres -d safe_companions_db
```

SSL Certificate

```bash
// Check Certbot Renewal Timer
systemctl list-timers | grep certbot

// Simulate Renewal Without Making Changes
sudo certbot renew --dry-run

// Check Certificate Expiry Date
sudo certbot certificates
```