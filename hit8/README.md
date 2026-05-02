# Hit #8 — Capacidad Extendida

Este hit extiende el scraper con capacidades avanzadas de paginación, análisis de datos y persistencia histórica.

## Nuevas Capacidades

1. **Paginación**: El scraper ahora navega hasta 3 páginas para obtener los primeros 30 resultados de cada búsqueda.
2. **Comparación de Precios**: Se calcula automáticamente el precio mínimo, máximo, mediana y desvío estándar de los productos extraídos. Se imprime una tabla resumen al finalizar cada búsqueda.
3. **Histórico con PostgreSQL**: Los resultados se guardan en una base de datos PostgreSQL con un timestamp para seguimiento histórico.

---

## Estructura del Proyecto (Hit #8)

* **scraper.py**: Ahora incluye lógica de paginación y generación de estadísticas.
* **database.py**: Gestiona la conexión y operaciones con PostgreSQL.
* **migrations/**: Contiene scripts SQL para la creación del esquema de base de datos.
* **k8s/**:
    * **postgres.yaml**: Despliegue de PostgreSQL (StatefulSet, Service, PVC).
    * **secrets.yaml**: Credenciales de base de datos cifradas.
    * **configmap.yaml**: Configuración de conexión.
    * **cronjob.yaml**: Ejecución periódica integrada con la DB.

---

## Requisitos

Se agregaron las siguientes dependencias:
* `psycopg2-binary`: Para conectar con PostgreSQL.
* `pandas` & `tabulate`: Para el cálculo y visualización de estadísticas de precios.

---

## Cómo ejecutar en Kubernetes (k3s)

1. **Namespace y Secretos**:
   ```bash
   kubectl apply -f k8s/namespace.yaml
   kubectl apply -f k8s/secrets.yaml
   ```

2. **Base de Datos**:
   ```bash
   kubectl apply -f k8s/postgres.yaml
   ```

3. **Configuración y Scraper**:
   ```bash
   kubectl apply -f k8s/configmap.yaml
   kubectl apply -f k8s/pvc.yaml
   kubectl apply -f k8s/cronjob.yaml
   ```

4. **Ejecutar una vez manualmente**:
   ```bash
   kubectl apply -f k8s/job.yaml
   ```

---

## Esquema de Base de Datos

```sql
CREATE TABLE IF NOT EXISTS scrape_results (
    id           BIGSERIAL PRIMARY KEY,
    producto     TEXT      NOT NULL,
    titulo       TEXT      NOT NULL,
    precio       NUMERIC(12,2),
    link         TEXT,
    tienda_oficial TEXT,
    envio_gratis BOOLEAN,
    scraped_at   TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```
