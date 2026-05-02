# README — Hit #7 (Kubernetes)

## Dónde pararte

Parate en la carpeta del hit6 (ahí está el Dockerfile):

```bash
cd hit6
```

## Pasos para ejecutar

1. Construir la imagen Docker:

```bash
docker build -t ml-scraper:latest .
```

2. Crear el cluster (solo la primera vez):

```bash
k3d cluster create scraper
```

3. Cargar la imagen en el cluster:

```bash
k3d image import ml-scraper:latest -c scraper
```

4. Crear el namespace:

```bash
kubectl apply -f ../hit7/k8s/namespace.yaml
```

5. Aplicar el resto de manifiestos Kubernetes:

```bash
kubectl apply -f ../hit7/k8s/
```

6. Ver el Job:

```bash
kubectl get jobs -n ml-scraper
```

7. Ver logs:

```bash
kubectl logs -l job-name=scraper-once -n ml-scraper -f
```

8. Ver archivos generados:

```bash
kubectl get pods -n ml-scraper
kubectl exec -it <POD_NAME> -n ml-scraper -- ls /app/output
```

9. Ver el CronJob:

```bash
kubectl get cronjobs -n ml-scraper
```

**Evidencia de ejecución**
```bash
(venv) valentin@Debian:~/Proyectos/testing/Testing-Selenium-ProxyTeam/hit6$ kubectl get jobs -n ml-scraper
NAME                      STATUS     COMPLETIONS   DURATION   AGE
scraper-hourly-29628000   Complete   1/1           10s        33m
scraper-once              Complete   1/1           12s        34m

(venv) valentin@Debian:~/Proyectos/testing/Testing-Selenium-ProxyTeam/hit6$ kubectl logs -l job-name=scraper-once -n ml-scraper -f
tests/test_coverage_boost.py      29      0   100%
tests/test_extractors.py          10      0   100%
tests/test_retry.py               10      0   100%
tests/test_schema.py               6      0   100%
--------------------------------------------------
TOTAL                            179     16    91%

Required test coverage of 70% reached. Total coverage: 91.06%

============================== 8 passed in 6.40s ===============================

(venv) valentin@Debian:~/Proyectos/testing/Testing-Selenium-ProxyTeam/hit6$ kubectl get cronjobs -n ml-scraper
NAME             SCHEDULE    TIMEZONE   SUSPEND   ACTIVE   LAST SCHEDULE   AGE
scraper-hourly   0 * * * *   <none>     False     0        34m             61m
```