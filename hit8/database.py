import os
import psycopg2
from psycopg2.extras import execute_values
import logging

class Database:
    def __init__(self):
        self.host = os.getenv("DB_HOST", "localhost")
        self.port = os.getenv("DB_PORT", "5432")
        self.user = os.getenv("DB_USER", "postgres")
        self.password = os.getenv("DB_PASSWORD", "postgres")
        self.dbname = os.getenv("DB_NAME", "scraper_db")
        self.conn = None

    def connect(self):
        try:
            self.conn = psycopg2.connect(
                host=self.host,
                port=self.port,
                user=self.user,
                password=self.password,
                dbname=self.dbname
            )
            self.conn.autocommit = True
            logging.info("Connected to PostgreSQL database.")
        except Exception as e:
            logging.error(f"Error connecting to database: {e}")
            raise

    def run_migrations(self):
        migration_path = os.path.join(os.path.dirname(__file__), "migrations", "001_initial.sql")
        with open(migration_path, "r") as f:
            sql = f.read()
        
        with self.conn.cursor() as cur:
            cur.execute(sql)
            logging.info("Migrations executed successfully.")

    def save_results(self, product_name, results):
        if not self.conn:
            self.connect()
        
        query = """
            INSERT INTO scrape_results (producto, titulo, precio, link, tienda_oficial, envio_gratis)
            VALUES %s
        """
        data = [
            (
                product_name,
                r.get("titulo"),
                r.get("precio"),
                r.get("link"),
                r.get("tienda_oficial"),
                r.get("envio_gratis")
            )
            for r in results
        ]
        
        try:
            with self.conn.cursor() as cur:
                execute_values(cur, query, data)
                logging.info(f"Saved {len(data)} results for '{product_name}' to DB.")
        except Exception as e:
            logging.error(f"Error saving results to DB: {e}")

    def close(self):
        if self.conn:
            self.conn.close()
            logging.info("Database connection closed.")
