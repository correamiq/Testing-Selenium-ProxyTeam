# README — Proyecto Scraper

## Requisitos previos TP0

- Docker instalado y funcionando
- Python 3.13 con entorno virtual
- Selenium configurado con Chrome y Firefox
- Pytest con cobertura (pytest-cov)
- Pre-commit configurado:
    - Ruff (lint + format)
    - Gitleaks (secrets)
- Estructura modular del scraper (extractores, selectores, retry, logging)
- Imagen Docker del scraper lista para ejecución
- Kubernetes (k3s o k3d) funcional
---

## Hits 1, 2 y 3 — Ejecución local

```bash
pip install -r requirements.txt

# Hit 1
pytest hit1/ -s

# Hit 2
pytest hit2/ -s --browser chrome
pytest hit2/ -s --browser firefox

# Hit 3
pytest hit3/ -s --browser chrome
pytest hit3/ -s --browser firefox
```

---

## Hits 4, 5 y 6 — Docker Compose

```bash
docker compose up --build
```

---

## Hit 7 — Kubernetes

```bash
cd hit6
docker build -t ml-scraper:latest .
k3d cluster create scraper
k3d image import ml-scraper:latest -c scraper
kubectl apply -f ../hit7/k8s/namespace.yaml
kubectl apply -f ../hit7/k8s/

# Verificar
kubectl get jobs -n ml-scraper
kubectl logs -l job-name=scraper-once -n ml-scraper -f
kubectl get cronjobs -n ml-scraper
```

---

## Hit 8 — Kubernetes con PostgreSQL

```bash
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/secrets.yaml
kubectl apply -f k8s/postgres.yaml
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/pvc.yaml
kubectl apply -f k8s/cronjob.yaml

# Ejecutar una vez manualmente
kubectl apply -f k8s/job.yaml
```

## Prerrequisitos cumplidos

[README TP0](file:///home/valentin/Proyectos/testing/Testing-Selenium-ProxyTeam/tp0/README.md)
