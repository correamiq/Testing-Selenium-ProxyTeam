Hit #8 — Capacidad extendida

Extienda el scraper con las siguientes 3 capacidades:

    Paginación: traer los primeros 30 resultados en lugar de 10, navegando hasta 3 páginas.

    Comparación de precios: para cada producto, calcular precio mínimo, máximo, mediana y desvío estándar entre los resultados extraídos. Imprimir tabla resumen.

    Histórico con PostgreSQL: guardar los resultados en una instancia PostgreSQL con timestamp, para detectar cambios de precio entre corridas del CronJob (Hit #7). Implementación esperada: deployment de Postgres en el mismo cluster k3s (StatefulSet + PVC + Service), credenciales via Secret, schema migrations (Alembic / Flyway / Liquibase / SQL files versionados). Tabla mínima: (producto, titulo, precio, link, tienda_oficial, scraped_at).

    Schema mínimo (versionarlo en una migration):

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
    CREATE INDEX IF NOT EXISTS idx_scrape_results_producto_fecha
        ON scrape_results (producto, scraped_at DESC);

    Con este schema y un par de corridas del CronJob, una query como:

    SELECT producto, MIN(precio), MAX(precio), AVG(precio), COUNT(DISTINCT scraped_at) AS n_runs
    FROM scrape_results
    WHERE scraped_at > NOW() - INTERVAL '7 days'
    GROUP BY producto;

    les da una vista de la evolución de precios sin escribir código adicional.
