# Hit #1 — Búsqueda básica en MercadoLibre

## Cómo ejecutar

```bash
pip install -r requirements.txt
pytest hit1/ -s
```

## Requisitos previos

- Python 3.10+
- Google Chrome instalado
- Selenium Manager

## Decisiones de diseño

**Selector de resultados:** `li.ui-search-layout__item` identifica cada tarjeta de producto en la grilla. Es la clase más estable que expone MercadoLibre para este propósito.

**Selector de título:** `a.poly-component__title` es el enlace que contiene el texto del producto. Se verificó inspeccionando el DOM real — la estructura anterior (`h2.ui-search-item__title`) ya no existe en el sitio.

**Explicit waits:** Se usa `WebDriverWait` + `expected_conditions` en dos momentos: al localizar el campo de búsqueda y al esperar que carguen los resultados. No se usa `time.sleep()`.
