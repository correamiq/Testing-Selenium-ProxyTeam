# Hit #3 — Filtros y Screenshots

## Cómo ejecutar

```bash
pip install -r requirements.txt

pytest hit3/ -s --browser chrome
pytest hit3/ -s --browser firefox
```

Los screenshots se guardan en `screenshots/` con el formato `<producto>_<browser>.png`.

## Requisitos previos

- Python 3.10+
- Google Chrome y Mozilla Firefox instalados
- Selenium Manager descarga los drivers automáticamente

## Decisiones de diseño

**Filtros vía clicks reales:** Los tres filtros (Nuevo, Tienda oficial, Más relevantes) se aplican haciendo clicks sobre los elementos del DOM, no modificando la URL. Esto replica el comportamiento real de un usuario.

**Selectores XPath para filtros:** Los filtros no tienen atributos `id` ni clases estables, por lo que se usan XPaths que buscan por texto visible: `//span[normalize-space()='Nuevo']/ancestor::a`. Esto es más resistente a cambios de estructura que depender de clases CSS internas.

**Filtros opcionales:** Si un filtro no está disponible para un producto (por ejemplo, no hay tiendas oficiales para GeForce RTX 5090), el test no falla — la función `apply_filter` captura el `TimeoutException` y continúa. El assert final valida que haya al menos 1 resultado independientemente de qué filtros se aplicaron.

**Parametrize:** El test usa `@pytest.mark.parametrize` para correr el mismo flujo sobre los 3 productos objetivo sin duplicar código.

**Screenshot:** Se toma con `driver.save_screenshot()` después de aplicar los filtros, capturando el estado final de la página.
