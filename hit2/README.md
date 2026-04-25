# Hit #2 — Browser Factory

## Cómo ejecutar

```bash
pip install -r requirements.txt

# Con argumento de línea de comandos
pytest hit2/ -s --browser chrome
pytest hit2/ -s --browser firefox

# Con variable de entorno
BROWSER=firefox pytest hit2/ -s
```

## Requisitos previos

- Python 3.10+
- Google Chrome y Mozilla Firefox instalados
- Selenium Manager descarga ChromeDriver y GeckoDriver automáticamente

## Decisiones de diseño

**Browser Factory:** La función `create_driver(browser)` en `conftest.py` recibe el nombre del browser y devuelve la instancia de WebDriver configurada. Centralizar esto en un solo lugar significa que agregar un tercer browser solo requiere un nuevo bloque ahí.

**Prioridad del parámetro:** El fixture lee primero `--browser` de la CLI y si no está definido cae a la variable de entorno `BROWSER`. Si ninguna está presente, usa Chrome por defecto.

**Diferencias encontradas entre browsers:**

| Aspecto | Chrome | Firefox |
| `--start-maximized` | Funciona como argumento de ChromeOptions | Firefox requiere `maximize_window()` o no aplica |
| Selectores CSS | Idénticos resultados | Idénticos resultados |
| Velocidad de carga | Ligeramente más rápido | Ligeramente más lento en la página inicial |
