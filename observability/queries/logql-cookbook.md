# LogQL Cookbook

## Básicos
- Ver todos los logs: `{job="observability/promtail"}`
- Filtrar por contenedor: `{container="scraper"}`
- Buscar errores: `{container="scraper"} |= "error" or |= "Error" or |= "ERROR"`

## Análisis
- Tasa de errores por minuto:
  `sum by (container) (rate({container="scraper"} |= "error" [1m]))`

## Filtros de Línea
- `|=` : Contiene
- `!=` : No contiene
- `|~` : Regex match
- `!~` : Regex no match
