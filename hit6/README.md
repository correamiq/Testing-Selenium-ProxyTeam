## README.md

### ¿Qué es el Hit #6?

El Hit #6 agrega calidad al proyecto:

* Permite ejecutar el navegador en modo **headless** (sin abrir ventana).
* Agrega **tests automáticos**.
* Verifica que los datos extraídos sean correctos.
* Mide **cobertura de código** (mínimo 70%).

---

### Archivos principales

* **scraper.py**
  Ejecuta todo el flujo: abre el navegador, busca productos y guarda los resultados.

* **extractors.py**
  Saca los datos de cada producto (título, precio, link, etc.).

* **selectors_ml.py**
  Contiene los selectores del HTML (qué buscar en la página).

* **retry_ml.py**
  Maneja reintentos cuando algo falla (timeouts, carga lenta).

* **logging_setup.py**
  Configura logs para ver errores y lo que pasa durante la ejecución.

---

### Tests

* **test_hit6_e2e.py**
  Prueba completa: corre el scraper y verifica que genere archivos.

* **tests/test_extractors.py**
  Verifica que los datos se extraigan correctamente.

* **tests/test_retry.py**
  Verifica que los reintentos funcionen.

* **tests/test_schema.py**
  Verifica que el JSON tenga el formato correcto.

* **conftest.py**
  Configuración común para los tests (mocks, helpers).

---

### Infra

* **Dockerfile**
  Define cómo se construye la imagen con todo lo necesario.

* **docker-compose.yml**
  Permite ejecutar todo con un solo comando.

* **requirements.txt**
  Librerías necesarias.

---

### Output

* **output/**
  Acá se guardan los JSON generados.

---

### Cómo correr

```bash
docker compose up
```

Esto ejecuta los tests y el scraper automáticamente.
