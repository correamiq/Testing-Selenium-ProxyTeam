# TP 2 · Parte 1 — Observabilidad: Logging centralizado con Loki + Promtail/Alloy + Grafana

**Seminario de Integración Profesional · UNLu DCB · 2026**  
**Docente:** Dr. David Petrocelli  
**Fecha de entrega:** 05/05/2026

---

## Contexto general

Este TP es la **Parte 1 de 4** sobre observabilidad. El recorrido completo:

- **Parte 1 (acá)** — Loki + Promtail/Alloy + Grafana (más simple, OSS, label-based)
- **Parte 2** — EFK: Elasticsearch + Fluentd/Fluent Bit + Kibana (full-text search)
- **Parte 3** — OpenTelemetry Collector + SDK (vendor-neutral, multi-signal)
- **Parte 4** — Cierre: decisiones arquitectónicas + ADR comparativo de los 3 stacks

> El objetivo no es "casarse" con un stack — es entender los **trade-offs** y elegir informados. La cátedra recomienda terminar con **OTel** como capa de abstracción + **Loki** como backend.

**Partes 1 y 2 se entregan el mismo día (05/05) en un solo push final.** Loki tarda ~30 min; EFK ~1 h. Recomendación: arrancar con Loki y dejarlo escribiendo logs en background mientras se monta EFK.

Este TP arranca donde terminó el **TP 1 · Parte 2**: el scraper ya corre como `Job` y `CronJob` en k3s, ya tiene `logging` estructurado básico en Python y ya escribe a Postgres. Lo que falta es **mirar lo que pasa**.

---

## Pre-requisitos

- **TP 1 · Parte 2 entregado y aprobado**: scraper corriendo como `Job` + `CronJob` en k3s, con `logging_setup.py` (Hit #5) y Postgres en cluster (Hit #8).
- Cluster k3s/k3d operativo con al menos **6 GB de RAM libre** y **8 GB de disco**.
- Familiaridad con `kubectl`, `helm` y manifests.
- **Helm 3 instalado** (`helm version` ≥ 3.16):
  ```bash
  curl -fsSL https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash
  ```

---

## Requisitos, consideraciones y formato de entrega

### Infra base obligatoria — bloqueante

> 🚧 Sin esto la entrega no se puede evaluar. Si el stack no levanta → **nota 0**.

#### Estructura de carpeta `observability/`

```
observability/
├── README.md                    ← cómo levantar el stack en una corrida
├── helm/
│   ├── loki-values.yaml
│   ├── promtail-values.yaml     ← (o alloy-values.yaml)
│   └── grafana-values.yaml
├── manifests/
│   ├── namespace.yaml
│   ├── grafana-secret.yaml      ← SOLO con placeholder, NO el secret real
│   └── grafana-nodeport.yaml
├── dashboards/
│   └── scraper-overview.json
├── queries/
│   └── logql-cookbook.md
└── install.sh                   ← script idempotente, todos los pasos
```

#### `install.sh` reproducible

Debe levantar el stack completo desde cero con un solo comando. Output esperado al final:

```
✓ Loki running
✓ Promtail/Alloy running (DaemonSet con 1 pod por nodo)
✓ Grafana running (NodePort 30000 abierto)
✓ Datasource Loki configurado y validado
✓ Dashboard 'Scraper Overview' provisionado
→ Abrir http://<node-ip>:30000  (admin / <ver secret>)
```

#### Versiones de charts pinneadas (no `latest`)

| Componente | Chart | Versión chart | App version | Repo |
|---|---|---|---|---|
| Loki (single-binary) | `grafana/loki` | `6.16.x` | Loki 3.x | https://grafana.github.io/helm-charts |
| Promtail | `grafana/promtail` | `6.16.x` | Promtail 3.x | https://grafana.github.io/helm-charts |
| Alloy (alternativa) | `grafana/alloy` | `0.9.x` | Alloy 1.5.x | https://grafana.github.io/helm-charts |
| Grafana | `grafana/grafana` | `8.5.x` | Grafana 11.x | https://grafana.github.io/helm-charts |

> ⚠️ **NO usar `grafana/loki-stack`** — deprecado desde 2024, no recibe updates de Loki 3.x.

#### Secret de admin de Grafana

Nunca commiteado en `values.yaml`. El `install.sh` lo crea desde env var:

```bash
: "${GRAFANA_ADMIN_PASSWORD:?Set GRAFANA_ADMIN_PASSWORD before running}"
kubectl -n observability create secret generic grafana-admin \
  --from-literal=admin-user=admin \
  --from-literal=admin-password="$GRAFANA_ADMIN_PASSWORD" \
  --dry-run=client -o yaml | kubectl apply -f -
```

El `grafana-values.yaml` referencia el secret con `admin.existingSecret: grafana-admin`.

#### `gitleaks` en pre-commit y CI

Igual que en TP 1 · Parte 2. Si se commitea la password por error, el push debe fallar.

---

### Otros requisitos

- **Mínimo 1 ADR obligatorio** en `docs/adr/`: `0007-stack-de-logging.md` justificando por qué Loki + Promtail/Alloy y no ELK / Splunk / Datadog. Formato Michael Nygard (Contexto · Decisión · Consecuencias). En la **Parte 4** este ADR va a ser revisitado y desafiado.

- **Bonus opcional**: ADR `0008-promtail-vs-alloy.md` si eligen Alloy.

- **NO tocar el código del scraper** en Hit #1 y Hit #2. Recién en Hit #3 se modifica.

- **Resources limitados** — cualquier `values.yaml` que pida más de lo siguiente se considera mal calibrado:

| Componente | Requests | Limits | Storage |
|---|---|---|---|
| Loki (single-binary) | 256Mi RAM, 100m CPU | 512Mi RAM, 500m CPU | 5Gi PVC `local-path` |
| Promtail (DaemonSet) | 64Mi RAM, 50m CPU | 128Mi RAM, 200m CPU | — |
| Alloy (DaemonSet) | 128Mi RAM, 100m CPU | 256Mi RAM, 300m CPU | — |
| Grafana | 128Mi RAM, 100m CPU | 256Mi RAM, 300m CPU | 1Gi PVC `local-path` |

- **Mantener buenas prácticas del TP 1**: explicit waits + selectores en módulo aparte. No regresionar.

---

## Contenidos del programa relacionados

- Observabilidad: los 3 pilares (logs, métricas, traces). Esta Parte 1 cubre solo logs.
- Arquitectura de logging centralizado: agente por nodo (DaemonSet) + collector + storage + visualizador.
- Loki: modelo "label-first" (igual que Prometheus) vs modelo "full-text index" de ELK.
- LogQL: selector de streams + filtros + agregaciones.
- Logs estructurados: JSON line-delimited, campos enriquecidos, niveles, correlación.
- Grafana: datasources, dashboards as-code, alerting básico.
- Helm: charts, values, releases, dependencias.
- Patrones operativos: retention, sizing, backpressure, sampling.

---

## Por qué necesitamos logging centralizado

Hoy, si el `CronJob` falla, la única forma de saber qué pasó es:

```bash
kubectl get pods -n ml-scraper -l job-name=scraper-hourly-28473215
kubectl logs <pod> -n ml-scraper
```

Esto se vuelve **inutilizable** rápidamente por tres razones:

1. **Los pods se borran.** k8s los recolecta cuando el `Job` termina. Si llegás 30 minutos tarde, el log ya no existe.
2. **No se pueden buscar.** "¿Cuántas veces falló el scraping de iPhone en las últimas 24h?" → imposible con `kubectl logs`.
3. **No se pueden correlacionar.** "El error de Postgres ocurrió 200 ms después del error de Selenium" → necesitás los dos streams en una misma timeline.

La solución: **Loki + Promtail/Alloy + Grafana**.

---

## Práctica

---

### Hit #1 — Deploy del stack Loki + Promtail + Grafana

#### 1.1 — Namespace y repo Helm

```bash
kubectl create namespace observability

helm repo add grafana https://grafana.github.io/helm-charts
helm repo update
```

#### 1.2 — Loki en modo single-binary con storage local

Loki tiene 3 modos: monolithic (single binary), simple-scalable, microservices. Para un cluster local **siempre** elegir **single-binary**.

`observability/helm/loki-values.yaml`:

```yaml
deploymentMode: SingleBinary

singleBinary:
  replicas: 1
  resources:
    requests: { cpu: 100m, memory: 256Mi }
    limits:   { cpu: 500m, memory: 512Mi }
  persistence:
    enabled: true
    size: 5Gi
    storageClass: local-path  # viene en k3s out-of-the-box

loki:
  auth_enabled: false
  commonConfig:
    replication_factor: 1
  storage:
    type: filesystem
  schemaConfig:
    configs:
      - from: 2025-01-01
        store: tsdb
        object_store: filesystem
        schema: v13
        index:
          prefix: loki_index_
          period: 24h
  limits_config:
    retention_period: 168h          # 7 días
    reject_old_samples: true
    reject_old_samples_max_age: 168h
    max_query_length: 721h
  compactor:
    retention_enabled: true
    delete_request_store: filesystem

# Apagar todo lo que no se usa en single-binary
read:    { replicas: 0 }
write:   { replicas: 0 }
backend: { replicas: 0 }
chunksCache:   { enabled: false }
resultsCache:  { enabled: false }
test: { enabled: false }
monitoring:
  selfMonitoring:    { enabled: false, grafanaAgent: { installOperator: false } }
  lokiCanary:        { enabled: false }
gateway: { enabled: false }
```

```bash
helm install loki grafana/loki \
  --version 6.16.0 \
  --namespace observability \
  --values observability/helm/loki-values.yaml
```

Verificar:

```bash
kubectl -n observability rollout status statefulset/loki --timeout=180s
kubectl -n observability get pvc   # tiene que estar Bound
```

#### 1.3 — Promtail (o Alloy) como DaemonSet

Recomendado: **Promtail**. Si eligen **Alloy**, documentar en ADR `0008-promtail-vs-alloy.md`.

`observability/helm/promtail-values.yaml`:

```yaml
config:
  clients:
    - url: http://loki.observability.svc.cluster.local:3100/loki/api/v1/push

resources:
  requests: { cpu: 50m, memory: 64Mi }
  limits:   { cpu: 200m, memory: 128Mi }

tolerations:
  - effect: NoSchedule
    operator: Exists
```

```bash
helm install promtail grafana/promtail \
  --version 6.16.0 \
  --namespace observability \
  --values observability/helm/promtail-values.yaml
```

Verificar:

```bash
kubectl -n observability get ds promtail        # DESIRED == READY
kubectl -n observability logs ds/promtail | head -30
# Deben aparecer líneas tipo: "Adding target ... namespace=ml-scraper pod=scraper-..."
```

#### 1.4 — Grafana con datasource Loki provisionado

`observability/helm/grafana-values.yaml`:

```yaml
admin:
  existingSecret: grafana-admin
  userKey: admin-user
  passwordKey: admin-password

persistence:
  enabled: true
  size: 1Gi
  storageClassName: local-path

resources:
  requests: { cpu: 100m, memory: 128Mi }
  limits:   { cpu: 300m, memory: 256Mi }

service:
  type: NodePort
  nodePort: 30000

datasources:
  datasources.yaml:
    apiVersion: 1
    datasources:
      - name: Loki
        type: loki
        access: proxy
        url: http://loki.observability.svc.cluster.local:3100
        isDefault: true
        jsonData:
          maxLines: 1000

dashboardProviders:
  dashboardproviders.yaml:
    apiVersion: 1
    providers:
      - name: 'sip2026'
        orgId: 1
        folder: 'SIP 2026'
        type: file
        disableDeletion: false
        options:
          path: /var/lib/grafana/dashboards/sip2026
```

```bash
helm install grafana grafana/grafana \
  --version 8.5.0 \
  --namespace observability \
  --values observability/helm/grafana-values.yaml
```

Verificar:

```bash
kubectl -n observability rollout status deploy/grafana --timeout=120s
kubectl -n observability get svc grafana   # debe mostrar 30000:xxxxx
echo "Abrir http://$(hostname -I | awk '{print $1}'):30000"
```

#### Output esperado del Hit #1

```
$ kubectl -n observability get pods
NAME                       READY   STATUS    RESTARTS   AGE
loki-0                     1/1     Running   0          3m
promtail-7d5fb             1/1     Running   0          3m
grafana-69b8f8c4d4-xxxxx   1/1     Running   0          2m

$ kubectl -n observability get svc
NAME       TYPE        CLUSTER-IP    EXTERNAL-IP   PORT(S)
grafana    NodePort    10.43.x.x     <none>        80:30000/TCP
loki       ClusterIP   10.43.x.x     <none>        3100/TCP,9095/TCP
```

En `http://<node-ip>:30000` → login → Explore → datasource Loki → query `{namespace="observability"}` → **deben aparecer logs del propio stack**. Eso prueba que el pipeline Promtail → Loki → Grafana está cerrado end-to-end.

---

### Hit #2 — Recolección de logs del scraper con labels Kubernetes

Refinar el `scrape_configs` de Promtail para:

- Filtrar solo el namespace del scraper (`ml-scraper`).
- Enriquecer cada línea con labels: `app`, `pod`, `container`, `namespace`, `job_name`, `node`.

Agregar al `promtail-values.yaml`:

```yaml
config:
  clients:
    - url: http://loki.observability.svc.cluster.local:3100/loki/api/v1/push

  snippets:
    extraScrapeConfigs: |
      - job_name: ml-scraper-pods
        kubernetes_sd_configs:
          - role: pod
            namespaces:
              names: [ml-scraper]
        relabel_configs:
          - source_labels: [__meta_kubernetes_pod_label_app]
            regex: scraper
            action: keep
          - source_labels: [__meta_kubernetes_namespace]
            target_label: namespace
          - source_labels: [__meta_kubernetes_pod_name]
            target_label: pod
          - source_labels: [__meta_kubernetes_pod_container_name]
            target_label: container
          - source_labels: [__meta_kubernetes_pod_label_app]
            target_label: app
          - source_labels: [__meta_kubernetes_pod_label_job_name]
            target_label: job_name
          - source_labels: [__meta_kubernetes_node_name]
            target_label: node
          - source_labels:
              - __meta_kubernetes_pod_uid
              - __meta_kubernetes_pod_container_name
            target_label: __path__
            separator: /
            replacement: /var/log/pods/*$1/*.log
```

> 💡 **Por qué pocos labels**: cada combinación única de labels crea un **stream** y los streams son la unidad de costo de RAM. Regla práctica: **menos de 10 labels totales, ninguno con cardinalidad alta** (no usar IDs random como label).

Aplicar:

```bash
helm upgrade promtail grafana/promtail \
  --version 6.16.0 \
  --namespace observability \
  --values observability/helm/promtail-values.yaml

kubectl -n observability rollout status ds/promtail
```

Disparar tráfico para validar:

```bash
kubectl -n ml-scraper create job --from=cronjob/scraper-hourly scraper-test-1
kubectl -n ml-scraper wait --for=condition=complete job/scraper-test-1 --timeout=600s
```

#### Output esperado del Hit #2

En Grafana → Explore → Loki:

```
{namespace="ml-scraper", app="scraper"}
{namespace="ml-scraper", app="scraper", job_name="scraper-test-1"}
```

**Screenshot requerido:** `observability/screenshots/hit2-labels.png`

---

### Hit #3 — Migrar el scraper a logs JSON estructurados

El `logging_setup.py` actual emite texto plano, que es pobre para queryar en LogQL. Con JSON estructurado, Loki extrae los campos automáticamente.

Agregar `python-json-logger>=3.2.0` a `requirements.txt`.

```python
# logging_setup.py
import logging
from logging.handlers import RotatingFileHandler
from pythonjsonlogger.json import JsonFormatter

def setup_logging(log_file: str = "output/scraper.log") -> None:
    json_formatter = JsonFormatter(
        "%(asctime)s %(levelname)s %(name)s %(message)s",
        rename_fields={"asctime": "timestamp", "levelname": "level", "name": "logger"},
        timestamp=True,
    )

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(json_formatter)

    file_formatter = logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
    )
    file_handler = RotatingFileHandler(
        log_file, maxBytes=2_000_000, backupCount=3, encoding="utf-8"
    )
    file_handler.setFormatter(file_formatter)

    logging.basicConfig(level=logging.INFO, handlers=[stream_handler, file_handler])
```

Enriquecer los call-sites con `extra=`:

```python
logger.info(
    "Scrape iniciado",
    extra={"producto": producto, "browser": browser, "page": page},
)
logger.warning(
    "Precio ausente, devuelvo null",
    extra={"producto": producto, "field": "precio", "result_index": idx},
)
logger.error(
    "Timeout tras 3 reintentos",
    extra={"producto": producto, "selector": selector, "attempts": 3},
    exc_info=True,
)
```

> ⚠️ **No mezclar `%`-formatting con `extra=`**. Si usás `logger.info("Producto %s", producto)`, el valor queda en el `message` y no es queryable como campo.

#### Equivalentes en otros stacks

| Stack | Librería | Nota |
|---|---|---|
| Node.js | `pino` | Ya emite JSON nativo. Verificar que `transport` no esté en `pino-pretty` en producción. |
| Java | SLF4J + Logback + `logstash-logback-encoder` | Reemplazar `<encoder>` por `LogstashEncoder`. |

Validar con LogQL:

```
{namespace="ml-scraper", app="scraper"} | json
```

En **Detected fields** deben aparecer: `level`, `producto`, `browser`, `logger`, `message`, `timestamp`.

**Consigna obligatoria:** en el `README.md` de `observability/`, mostrar un **antes/después** con screenshots: log line plain text (Hit #2) vs log line JSON con campos extraídos (Hit #3).

---

### Hit #4 — LogQL cookbook: 5+ queries útiles

Documentar en `observability/queries/logql-cookbook.md` al menos 5 queries. Cada una debe incluir: pregunta de negocio, query, ejemplo de output y explicación de por qué está escrita así.

#### Q1 — Top errores por producto en las últimas 24h

```logql
sum by (producto) (
  count_over_time(
    {namespace="ml-scraper", app="scraper"} | json | level="ERROR" [24h]
  )
)
```

**Pregunta:** ¿qué producto está fallando más? Útil para priorizar bugfixes de selectores.

#### Q2 — Tasa de WARNINGs por minuto en la última hora

```logql
sum by (producto) (
  rate({namespace="ml-scraper", app="scraper"} | json | level="WARNING" [1m])
)
```

**Pregunta:** ¿hubo un pico de errores de retry hace 30 min?

#### Q3 — Conteo de filtros que no aparecieron por producto

```logql
sum by (producto) (
  count_over_time(
    {namespace="ml-scraper", app="scraper"}
      | json
      | message =~ "Filtro .* no disponible"
    [7d]
  )
)
```

**Pregunta:** ¿qué productos pierden el filtro `tienda_oficial`?

#### Q4 — Duración media entre intentos de retry

```logql
avg_over_time(
  {namespace="ml-scraper", app="scraper"}
    | json
    | message=~"intento.*backoff"
    | unwrap delay_ms
  [1h]
)
```

**Pregunta:** ¿el backoff exponencial está disparando como se espera? Requiere que el Hit #3 emita el campo `delay_ms` como número.

#### Q5 — Última corrida exitosa por producto

```logql
topk(1,
  {namespace="ml-scraper", app="scraper"}
    | json
    | level="INFO"
    | message="Scrape completado"
) by (producto)
```

**Pregunta:** ¿hace cuánto que no se scrapea exitosamente cada producto? Base para una alerta del Hit #6.

> 📚 Documentación canónica de LogQL: https://grafana.com/docs/loki/latest/query/

---

### Hit #5 — Dashboard Grafana provisionado as-code

Construir un dashboard en Grafana con:

- **Stat panels (parte superior):** total de scrapes hoy, % de éxito, productos con más errores en 24h.
- **Time series (parte media):** queries Q2 y Q3 del Hit #4.
- **Table (parte inferior):** última corrida exitosa por producto (Q5) + top errores (Q1).

Exportarlo como JSON (Share → Export → Save to file) y commitearlo en `observability/dashboards/scraper-overview.json`.

#### Provisioning del dashboard via ConfigMap

```bash
kubectl -n observability create configmap scraper-overview-dashboard \
  --from-file=scraper-overview.json=observability/dashboards/scraper-overview.json \
  --dry-run=client -o yaml | kubectl apply -f -
```

Agregar el mount en `grafana-values.yaml`:

```yaml
extraConfigmapMounts:
  - name: scraper-overview-dashboard
    configMap: scraper-overview-dashboard
    mountPath: /var/lib/grafana/dashboards/sip2026
    readOnly: true
```

#### Output esperado del Hit #5

- En Grafana → Dashboards → carpeta **SIP 2026** → aparece **Scraper Overview**.
- Los 3 stat panels muestran números reales.
- Los time-series muestran las últimas 6 horas de actividad.
- La tabla muestra los 3 productos con timestamps recientes.

**Screenshot requerido:** `observability/screenshots/hit5-dashboard.png`

---

### Hit #6 — Alertas (opcional, bonus +5%)

Configurar **una alerta Grafana Alerting** que notifique a un **webhook de Discord** cuando:

- El `CronJob` falla **2 veces seguidas** (basado en logs `level=ERROR` con `event=scrape_failed`).
- Un producto **no se logra scrapear en 24h** (basado en Q5).

#### Contact point Discord

Grafana → Alerting → Contact points → New → Discord webhook URL.

> 🔒 El URL del webhook es un secret. No commitearlo. Usar un k8s `Secret` y referenciarlo desde Grafana via env var. El `install.sh` debe leer `DISCORD_WEBHOOK_URL` de env vars locales.

#### Alert rule provisionada as-code

`observability/manifests/alert-rules.yaml`:

```yaml
apiVersion: 1
groups:
  - orgId: 1
    name: scraper-health
    folder: SIP 2026
    interval: 5m
    rules:
      - uid: scrape-stale-24h
        title: "Producto no scrapeado en 24h"
        condition: A
        data:
          - refId: A
            datasourceUid: <UID-de-Loki>
            model:
              expr: |
                (time() - max(last_over_time(
                  {namespace="ml-scraper", app="scraper"}
                    | json | message="Scrape completado"
                    | unwrap timestamp [25h]
                )) by (producto)) > 86400
        noDataState: Alerting
        execErrState: Alerting
        for: 10m
        annotations:
          summary: "El producto {{ $labels.producto }} no se scrapea hace más de 24h"
        labels:
          severity: warning
```

Test: simular el fallo con `suspend: true` en el CronJob, o bajar el threshold a `> 600` (10 min) para la corrida de evaluación. Documentar en `observability/README.md` cómo setear `DISCORD_WEBHOOK_URL` y validar la alerta.

**Screenshot requerido:** `observability/screenshots/hit6-discord-alert.png`

---

## Cómo entregar

- **Push final al repo público** (mismo repo del TP 1) antes del **05/05/2026 23:59 ART**.
- **README raíz actualizado** con sección "TP 2 · Parte 1" que explique cómo correr `install.sh`, variables de entorno requeridas y link a `observability/README.md`.
- **Carpeta `observability/`** completa.
- **`docs/adr/0007-stack-de-logging.md`** (y opcionalmente `0008-promtail-vs-alloy.md`).
- **`observability/screenshots/`** con mínimo:
  - `hit2-labels.png` — Grafana Explore con logs filtrados por labels k8s.
  - `hit3-json-fields.png` — Grafana Explore con campos JSON extraídos.
  - `hit5-dashboard.png` — dashboard provisionado con datos reales.
  - (bonus) `hit6-discord-alert.png` — captura de la notificación en Discord.
- **Video corto (3-5 min):** `install.sh` corriendo de cero, Grafana en `:30000`, demo de las 5 queries, dashboard con datos.
- **Mensaje en Discord** con link al repo y al video.

> 📡 Canal Discord: https://discord.com/channels/1482135908508500148/1482135909456679139

---

## Auto-verificación previa a la entrega

> Si algo falla acá, no entregar — son puntos seguros que se pierden con 5 minutos de checklist.

### 1) `install.sh` corre limpio en cluster vacío

```bash
kubectl delete namespace observability --wait=true
export GRAFANA_ADMIN_PASSWORD='<algo-random>'
cd observability && ./install.sh
# Debe terminar con exit 0 y los 5 ✓
```

### 2) Los 3 pods + DaemonSet están Running

```bash
kubectl -n observability get pods,ds,svc,pvc
# loki-0 Running, promtail-xxxx Running, grafana-xxxxx Running
# ds/promtail con DESIRED == READY
# svc/grafana con NodePort 30000
# PVCs Bound
```

### 3) Loki responde a queries via HTTP

```bash
kubectl -n observability port-forward svc/loki 3100:3100 &
sleep 2
curl -sG http://localhost:3100/loki/api/v1/labels | jq '.data | length > 0'
# Esperado: true
```

### 4) Grafana resuelve el datasource Loki

```bash
curl -u admin:"$GRAFANA_ADMIN_PASSWORD" \
  http://localhost:30000/api/datasources/name/Loki | jq '.type'
# Esperado: "loki"
```

### 5) Las 5 queries del Hit #4 corren sin error

Grafana → Explore → pegar cada query del cookbook. Debe devolver datos o `No data`, **nunca** error de sintaxis LogQL.

### 6) Dashboard provisionado aparece en la UI

```bash
kubectl -n observability rollout restart deploy/grafana
sleep 30
# Grafana → Dashboards → buscar "Scraper Overview" en carpeta "SIP 2026"
```

### 7) Logs del scraper son JSON parseados

Query: `{namespace="ml-scraper", app="scraper"} | json`

En **Detected fields** deben aparecer: `level`, `producto`, `logger`, `timestamp`. Si solo aparece `message`, el Hit #3 no está bien.

### 8) `gitleaks` no detecta el password de Grafana

```bash
gitleaks detect --no-git --verbose
# Esperado: 0 leaks
```

---

## Common pitfalls

### `loki-stack` chart deprecado

El primer resultado de Google dice `grafana/loki-stack`. **No usarlo.** Está deprecado desde 2024, viene con Loki 2.x (no 3.x). Usar los charts separados.

### Cardinality explosion → Loki OOM

Si pusieron un label `request_id` o `trace_id`, **Loki va a OOM-killearse** en pocos minutos. Esos campos van **dentro del JSON**, no como label. Ningún label debe tener más de ~100 valores únicos por día.

### Promtail no encuentra logs (`__path__` vacío)

Posibles causas: el path en el host es distinto en k3d vs k3s, el pod ya terminó hace mucho y el log file fue rotado, o el `serviceAccount` de Promtail no tiene permisos (si se overrideó el `securityContext`). Disparar un Job nuevo y mirar los logs en vivo.

### `python-json-logger` cambió de API en v3

```python
from pythonjsonlogger.json import JsonFormatter   # ✓ correcto (v3.x)
# NO: from pythonjsonlogger import jsonlogger      # deprecado (v2.x)
```

### Grafana muestra `No data` aunque hay logs en Loki

Casi siempre es **time range**: por default Grafana arranca en "Last 1 hour". Cambiar a "Last 24 hours" antes de preocuparse.

### El dashboard JSON se rompe al cambiar de versión de Grafana

El JSON de dashboards es compatible solo dentro de la misma minor. Mitigación: poner `"schemaVersion": 39` en el JSON exportado y no usar features experimentales.

---

## Criterios de evaluación

### Requisitos bloqueantes (nota 0 si falta cualquiera)

- TP 1 · Parte 2 entregado y aprobado (mínimo 60/100).
- `observability/install.sh` funciona en cluster limpio con un solo comando.
- Helm charts pinneados a versiones específicas. `loki-stack` **NO** usado.
- Sin secrets en el repo (`gitleaks detect` da 0 leaks).
- Auto-verificación completa ejecutada antes del push final.

### Tabla de puntaje (100%)

| Criterio | Peso |
|---|---|
| Hit #1 — stack Loki + Promtail + Grafana corriendo + datasource validado | 20% |
| Hit #2 — Promtail/Alloy refinado a namespace `ml-scraper` con labels k8s útiles | 15% |
| Hit #3 — scraper migrado a JSON line-delimited + campos extraíbles via `\| json` | 20% |
| Hit #4 — `logql-cookbook.md` con las 5 queries documentadas | 15% |
| Hit #5 — dashboard `scraper-overview.json` provisionado as-code con datos reales | 20% |
| ADR `0007-stack-de-logging.md` justificando la elección | 10% |
| **Bonus** Hit #6 — alerta a Discord funcionando + screenshot | +5% |

---

## Material de apoyo

### Tabla comparativa de stacks de logging centralizado

| Stack | Storage | Query | Pro | Contra | Costo |
|---|---|---|---|---|---|
| **Loki + Promtail + Grafana** | Filesystem / S3 | LogQL (label-first) | Simple, bajo costo, integración nativa Grafana | Full-text grep lento | OSS, $0 |
| **Loki + Alloy + Grafana** | Idem | LogQL | Alloy unifica logs + métricas + traces (GA 2024) | Menos documentación que Promtail | OSS, $0 |
| **Vector + Loki + Grafana** | Idem | LogQL | Vector más performante (Rust) | Más componentes | OSS, $0 |
| **OTel Collector + Loki** | Idem | LogQL | Vendor-neutral (CNCF) | Más config, OTel logs en evolución | OSS, $0 |
| **EFK** | Elasticsearch | KQL / Lucene | Full-text search rápida, ecosistema maduro | ES pide 2 GB RAM mínimo | OSS, **abordado en Parte 2** |
| **Datadog Logs** | SaaS cloud | Datadog QL | Zero-ops | Vendor lock-in, **paid** ($0.10/GB) | $$$ — descartar |
| **Splunk Cloud** | SaaS o on-prem | SPL | Standard enterprise | Caro, complejo on-prem | — descartar |

**Opciones aceptables para esta Parte 1:** Loki + Promtail o Loki + Alloy (con ADR). Vector se acepta con ADR adicional. Datadog / Splunk no se aceptan.

---

### Esqueleto de `install.sh`

```bash
#!/usr/bin/env bash
set -euo pipefail

NAMESPACE=observability
: "${GRAFANA_ADMIN_PASSWORD:?Set GRAFANA_ADMIN_PASSWORD before running}"

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "→ Namespace + Helm repo"
kubectl create namespace "$NAMESPACE" --dry-run=client -o yaml | kubectl apply -f -
helm repo add grafana https://grafana.github.io/helm-charts >/dev/null 2>&1 || true
helm repo update >/dev/null

echo "→ Secret de admin de Grafana"
kubectl -n "$NAMESPACE" create secret generic grafana-admin \
  --from-literal=admin-user=admin \
  --from-literal=admin-password="$GRAFANA_ADMIN_PASSWORD" \
  --dry-run=client -o yaml | kubectl apply -f -

echo "→ Loki (single-binary, filesystem)"
helm upgrade --install loki grafana/loki \
  --version 6.16.0 \
  --namespace "$NAMESPACE" \
  --values "$DIR/helm/loki-values.yaml" \
  --wait --timeout 5m

echo "→ Promtail (DaemonSet)"
helm upgrade --install promtail grafana/promtail \
  --version 6.16.0 \
  --namespace "$NAMESPACE" \
  --values "$DIR/helm/promtail-values.yaml" \
  --wait --timeout 3m

echo "→ Dashboard ConfigMap"
kubectl -n "$NAMESPACE" create configmap scraper-overview-dashboard \
  --from-file="scraper-overview.json=$DIR/dashboards/scraper-overview.json" \
  --dry-run=client -o yaml | kubectl apply -f -

echo "→ Grafana"
helm upgrade --install grafana grafana/grafana \
  --version 8.5.0 \
  --namespace "$NAMESPACE" \
  --values "$DIR/helm/grafana-values.yaml" \
  --wait --timeout 3m

NODE_IP=$(kubectl get nodes -o jsonpath='{.items[0].status.addresses[?(@.type=="InternalIP")].address}')
echo ""
echo "✓ Loki running"
echo "✓ Promtail running"
echo "✓ Grafana running"
echo "✓ Datasource Loki configurado"
echo "✓ Dashboard 'Scraper Overview' provisionado"
echo "→ Abrir http://${NODE_IP}:30000   (admin / \$GRAFANA_ADMIN_PASSWORD)"
```

> Hacer `chmod +x install.sh` antes de commitearlo.

---

### Esqueleto de ADR `0007-stack-de-logging.md`

```markdown
# 0007 — Adoptamos Loki + Promtail + Grafana para logging centralizado

- Date: 2026-05-12
- Status: Accepted
- Deciders: <equipo>

## Contexto

El scraper corre como CronJob en k3s y emite logs a stdout. `kubectl logs` se vuelve
inutilizable en cuanto los pods son recolectados. Necesitamos un backend de logs con
retención mínima 7 días, queryable, y visualizable. Restricciones:
- Cluster local k3s single-node, ~6 GB RAM disponibles.
- Sin cloud / sin servicios pagos.
- Equipo familiarizado con Grafana.

Alternativas consideradas: Loki+Promtail, Loki+Alloy, Vector+Loki, OTel+Loki,
EFK, Datadog, Splunk. Tabla comparativa en Material de apoyo.

## Decisión

Adoptamos **Loki + Promtail + Grafana** (charts separados, versiones pinneadas).

## Consecuencias

- Más fácil: setup en ~10 min con Helm; integración nativa con Grafana; costo $0;
  modelo label-first simple y suficiente para nuestro volumen.
- Más difícil: full-text grep es lento (Loki indexa labels, no el cuerpo del log).
- Sacrificio: no se pueden hacer queries complejas tipo SQL.
- Riesgo: cardinality explosion si se labelea mal. Mitigado en Hit #2 con regla de
  ≤10 labels totales y ninguno de cardinalidad alta.

## Referencias

- Loki architecture: https://grafana.com/docs/loki/latest/get-started/architecture/
- Tabla comparativa: TP 2 / Material de apoyo
```

---

## Referencias y bibliografía

### Hit #1 — Deploy del stack
- Grafana Loki — Get started: https://grafana.com/docs/loki/latest/get-started/
- Loki Helm chart — single-binary: https://grafana.com/docs/loki/latest/setup/install/helm/install-monolithic/
- Grafana Helm chart docs: https://github.com/grafana/helm-charts/tree/main/charts/grafana
- Helm 3 — Best practices: https://helm.sh/docs/chart_best_practices/

### Hit #2 — Promtail / Alloy + scrape configs Kubernetes
- Promtail — Scrape configs reference: https://grafana.com/docs/loki/latest/send-data/promtail/configuration/#scrape_configs
- Promtail — Pipeline stages: https://grafana.com/docs/loki/latest/send-data/promtail/stages/
- Grafana Alloy documentation: https://grafana.com/docs/alloy/latest/
- Loki — Cardinality best practices: https://grafana.com/docs/loki/latest/get-started/labels/cardinality/

### Hit #3 — Logs estructurados JSON
- `python-json-logger` 3.x: https://github.com/nhairs/python-json-logger
- Twelve-Factor App — XI. Logs: https://12factor.net/logs

### Hit #4 — LogQL
- LogQL — Log queries: https://grafana.com/docs/loki/latest/query/log_queries/
- LogQL — Metric queries: https://grafana.com/docs/loki/latest/query/metric_queries/
- LogQL — Examples cheatsheet: https://grafana.com/docs/loki/latest/query/query_examples/

### Hit #5 — Dashboards as-code
- Grafana — Provisioning dashboards: https://grafana.com/docs/grafana/latest/administration/provisioning/#dashboards
- Grafana — Dashboard JSON model: https://grafana.com/docs/grafana/latest/dashboards/build-dashboards/view-dashboard-json-model/

### Hit #6 — Alertas (bonus)
- Grafana Alerting — Provision alert rules: https://grafana.com/docs/grafana/latest/alerting/set-up/provision-alerting-resources/
- Grafana — Discord contact point: https://grafana.com/docs/grafana/latest/alerting/configure-notifications/manage-contact-points/integrations/configure-discord/

### Observabilidad — fundamentos
- Distributed Systems Observability (Cindy Sridharan, O'Reilly 2018): https://www.oreilly.com/library/view/distributed-systems-observability/9781492033431/
- Google SRE Book — Cap. 6: https://sre.google/sre-book/monitoring-distributed-systems/
- CNCF Observability Whitepaper (2023): https://github.com/cncf/tag-observability/blob/main/whitepaper.md

### Comparación Loki vs alternativas
- "Like Prometheus, but for logs" (Grafana Labs, 2018): https://grafana.com/blog/2018/12/12/loki-prometheus-inspired-open-source-logging-for-cloud-natives/
- Dapper (Google, 2010): https://research.google/pubs/pub36356/