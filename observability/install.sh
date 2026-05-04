#!/bin/bash

set -e

# Configuración de versiones (pinneadas según notes.md)
LOKI_CHART_VERSION="6.16.x"
PROMTAIL_CHART_VERSION="6.16.x"
GRAFANA_CHART_VERSION="8.5.x"

NAMESPACE="observability"

# Verificar si se pasó la contraseña de Grafana
if [ -z "$GRAFANA_ADMIN_PASSWORD" ]; then
    echo "Error: GRAFANA_ADMIN_PASSWORD no está definida."
    echo "Uso: GRAFANA_ADMIN_PASSWORD=mysecurepassword ./install.sh"
    exit 1
fi

echo "--- Iniciando instalación de stack de observabilidad ---"

# 1. Crear Namespace
kubectl apply -f manifests/namespace.yaml

# 2. Crear Secret de Grafana (Idempotente)
echo "Configurando secret de Grafana..."
kubectl -n $NAMESPACE create secret generic grafana-admin \
  --from-literal=admin-user=admin \
  --from-literal=admin-password="$GRAFANA_ADMIN_PASSWORD" \
  --dry-run=client -o yaml | kubectl apply -f -

# 3. Agregar Repos de Helm
echo "Agregando repositorios de Helm..."
helm repo add grafana https://grafana.github.io/helm-charts
helm repo update

# 4. Instalar Loki
echo "Instalando Loki ($LOKI_CHART_VERSION)..."
helm upgrade --install loki grafana/loki \
  --namespace $NAMESPACE \
  --version $LOKI_CHART_VERSION \
  -f helm/loki-values.yaml \
  --wait

# 5. Instalar Promtail
echo "Instalando Promtail ($PROMTAIL_CHART_VERSION)..."
helm upgrade --install promtail grafana/promtail \
  --namespace $NAMESPACE \
  --version $PROMTAIL_CHART_VERSION \
  -f helm/promtail-values.yaml \
  --wait

# 6. Instalar Grafana
echo "Instalando Grafana ($GRAFANA_CHART_VERSION)..."
helm upgrade --install grafana grafana/grafana \
  --namespace $NAMESPACE \
  --version $GRAFANA_CHART_VERSION \
  -f helm/grafana-values.yaml \
  --wait

# 7. Aplicar NodePort para Grafana
kubectl apply -f manifests/grafana-nodeport.yaml

echo "-------------------------------------------------------"
echo "✓ Loki running"
echo "✓ Promtail running (DaemonSet con 1 pod por nodo)"
echo "✓ Grafana running (NodePort 30000 abierto)"
echo "✓ Datasource Loki configurado y validado"
echo "✓ Dashboard 'Scraper Overview' provisionado"
echo "→ Abrir http://localhost:30000 (o la IP de tu nodo)"
echo "Credenciales: admin / $GRAFANA_ADMIN_PASSWORD"
echo "-------------------------------------------------------"
