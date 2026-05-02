# 0002 — Soporte multi-browser (Chrome y Firefox)

- Date: 2026-05-01
- Status: Accepted
- Deciders: Proxy Team

## Contexto

El scraper necesita ejecutarse en distintos entornos de ejecución (local, CI y Kubernetes). En estos entornos no siempre está garantizado que un único navegador esté disponible o que se comporte igual en todos los casos.

Además, diferentes navegadores pueden interpretar el DOM o los tiempos de carga de forma distinta, lo que puede afectar la estabilidad del scraping.

Las alternativas consideradas fueron:
- Usar solo Chrome (más simple pero menos flexible)
- Usar solo Firefox (menor soporte general en automatización)
- Soportar múltiples navegadores (Chrome y Firefox)
- Usar un navegador headless dedicado tipo Playwright (descartado por alcance del TP)

## Decisión

Se implementa soporte para **Chrome y Firefox utilizando Selenium WebDriver**, seleccionando el navegador mediante configuración (variable de entorno), con ejecución en modo headless cuando corresponde.

## Consecuencias

- Más fácil:
  - Mayor portabilidad del scraper en distintos entornos
  - Posibilidad de ejecutar en CI sin depender de un único browser
  - Mayor resiliencia ante fallos específicos de un navegador

- Más difícil:
  - Mayor complejidad en configuración del driver
  - Diferencias sutiles de comportamiento entre Chrome y Firefox
  - Necesidad de mantener compatibilidad en ambos entornos

- Riesgos:
  - Inconsistencias de rendering entre navegadores pueden generar resultados distintos
  - Mayor superficie de testing necesaria para asegurar consistencia

## Referencias

- Selenium WebDriver Documentation: https://www.selenium.dev/documentation/webdriver/
- W3C WebDriver Standard: https://www.w3.org/TR/webdriver2/
