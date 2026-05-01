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
