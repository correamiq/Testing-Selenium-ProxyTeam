# 0005 — Estrategia de retries con backoff exponencial en scraping

- Date: 2026-05-01
- Status: Accepted
- Deciders: Proxy Team

## Contexto

El scraping de MercadoLibre está sujeto a fallos transitorios como:
- timeouts de carga
- elementos que aparecen de forma tardía
- variabilidad en el DOM o respuestas incompletas
- carga parcial de resultados

Sin una estrategia de resiliencia, el scraper falla frecuentemente ante errores temporales.

Las alternativas consideradas fueron:
- fail-fast (no reintentar)
- retries simples sin espera
- retries con backoff lineal
- retries con backoff exponencial
- circuit breaker (más complejo, estilo microservicios)

## Decisión

Se implementa una estrategia de **reintentos con backoff exponencial**, con hasta 3 intentos y delays crecientes (2s, 4s, 8s), registrando errores en logs estructurados y continuando la ejecución cuando es posible.

## Consecuencias

- Más fácil:
  - Mayor estabilidad del scraper frente a fallos temporales
  - Menos pérdidas de datos por problemas transitorios
  - Mejor tolerancia a latencia de red o DOM lento

- Más difícil:
  - Mayor tiempo total de ejecución en caso de fallos
  - Complejidad adicional en manejo de estado de errores
  - Posible duplicación de intentos innecesarios en fallos permanentes

- Riesgos:
  - Retries excesivos pueden aumentar carga sobre el sitio objetivo
  - Si el error es estructural (selector roto), los retries no lo solucionan

## Referencias

- AWS Architecture Blog — Exponential Backoff and Jitter
  https://aws.amazon.com/blogs/architecture/exponential-backoff-and-jitter/

- Google SRE Book — Handling transient failures
  https://sre.google/sre-book/handling-overload/
