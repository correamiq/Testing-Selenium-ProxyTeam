# 0007 — Estructuración de selectores en módulo separado

- Date: 2026-05-01
- Status: Accepted
- Deciders: Proxy Team

## Contexto

El scraping depende fuertemente de selectores CSS/XPath que pueden cambiar frecuentemente debido a actualizaciones del sitio objetivo.

Si los selectores están distribuidos dentro del código del scraper, cualquier cambio en el DOM obliga a modificar múltiples archivos, aumentando el riesgo de errores.

Las alternativas consideradas fueron:
- Selectores hardcodeados dentro del scraper
- Selectores distribuidos en funciones extractoras
- Centralizar selectores en un módulo dedicado
- Uso de atributos dinámicos o ML-based scraping (fuera de alcance del TP)

## Decisión

Se decidió centralizar todos los selectores en un módulo separado (`selectors_ml.py`), utilizando nombres semánticos para facilitar mantenimiento y actualización.

## Consecuencias

- Más fácil:
  - Cambios de DOM se corrigen en un solo lugar
  - Código más legible y mantenible
  - Separación clara entre lógica y definición de selectores

- Más difícil:
  - Requiere mantener sincronización entre scraper y módulo de selectores
  - Puede generar errores si se importan selectores incorrectos

- Riesgos:
  - Si el módulo no se actualiza correctamente, el scraper puede fallar silenciosamente

## Referencias

- Selenium Best Practices: https://www.selenium.dev/documentation/webdriver/elements/locators/
