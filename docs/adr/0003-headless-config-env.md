# 0006 — Configuración de modo headless mediante variable de entorno

- Date: 2026-05-01
- Status: Accepted
- Deciders: Proxy Team

## Contexto

El scraper debe poder ejecutarse tanto en entornos locales (para debug) como en entornos automatizados como CI o Kubernetes.

En entornos como CI/CD o Kubernetes no existe interfaz gráfica, por lo que el navegador debe ejecutarse en modo headless. En desarrollo local, en cambio, es útil poder ver el navegador para depurar errores.

Las alternativas consideradas fueron:
- Hardcodear headless siempre activo
- Hardcodear headless desactivado
- Detectar automáticamente el entorno
- Configurar headless mediante variable de entorno

## Decisión

Se decide controlar el modo headless mediante la variable de entorno `HEADLESS`, permitiendo activar o desactivar el modo sin modificar el código.

## Consecuencias

- Más fácil:
  - Flexibilidad entre desarrollo y producción
  - No requiere cambios de código para cambiar comportamiento
  - Compatible con Docker y Kubernetes ConfigMaps

- Más difícil:
  - Requiere documentación clara del comportamiento esperado
  - Posibles errores si la variable no está configurada correctamente

- Riesgos:
  - Configuraciones inconsistentes entre entornos pueden generar bugs difíciles de reproducir

## Referencias

- Twelve-Factor App: https://12factor.net/config
