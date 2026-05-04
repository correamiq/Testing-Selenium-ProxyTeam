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

## Hit #8 — Kubernetes con PostgreSQL

### Nuevas capacidades

| Capacidad | Descripción |
|---|---|
| Paginación | Hasta 30 resultados navegando 3 páginas por producto |
| Estadísticas | Tabla min/max/mediana/promedio/desvío en stdout + `output/stats.json` |
| Histórico | Resultados persistidos en PostgreSQL para acumular corridas del CronJob |

### Despliegue

# 1. Crear el Secret (NUNCA commitear este archivo)
```bash
# El archivo k8s/postgres-secret.yaml está en .gitignore.
# Crearlo manualmente o inyectarlo desde CI como GitHub Secret.
cat > hit8/k8s/postgres-secret.yaml <<'EOF'
apiVersion: v1
kind: Secret
metadata:
  name: postgres-credentials
  labels:
    app: postgres
type: Opaque
stringData:
  POSTGRES_DB: scraper_db
  POSTGRES_USER: scraper
  POSTGRES_PASSWORD: <tu-password-segura>
EOF

# 2. Importar imagen y aplicar manifests
docker build -t ml-scraper:latest hit8/
docker save ml-scraper:latest -o /tmp/ml-scraper.tar
sudo k3s ctr images import /tmp/ml-scraper.tar && rm /tmp/ml-scraper.tar
kubectl apply -f hit8/k8s/

# 3. Esperar Postgres y seguir logs
kubectl wait --for=condition=ready pod -l app=postgres --timeout=120s
kubectl logs -l job-type=one-off -f

# 4. Consultar histórico
kubectl exec -it $(kubectl get pod -l app=postgres -o jsonpath='{.items[0].metadata.name}') \
  -- psql -U scraper -d scraper_db -c \
  "SELECT producto, MIN(precio), MAX(precio), COUNT(*) FROM scrape_results GROUP BY producto;"

# 5. Limpiar
kubectl delete -f hit8/k8s/
kubectl delete secret postgres-credentials
```

## Prerrequisitos cumplidos

[README TP0](file:///home/valentin/Proyectos/testing/Testing-Selenium-ProxyTeam/tp0/README.md)
