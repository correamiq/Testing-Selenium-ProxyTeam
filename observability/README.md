# Observability Stack (Loki + Promtail + Grafana)

Este directorio contiene la configuración para desplegar un stack de observabilidad básico en k3s.

## Estructura
- `helm/`: Archivos de valores para los charts de Grafana, Loki y Promtail.
- `manifests/`: Manifiestos de Kubernetes (Namespace, NodePort, etc).
- `dashboards/`: Definiciones JSON de dashboards de Grafana.
- `queries/`: Guía rápida de LogQL.
- `install.sh`: Script de instalación automática.

## Requisitos
- Helm 3 instalado.
- Cluster k3s/k3d operativo.
- Variable de entorno `GRAFANA_ADMIN_PASSWORD` definida.

## Instalación
Para levantar todo el stack, ejecuta:
```bash
chmod +x install.sh
export GRAFANA_ADMIN_PASSWORD="tu_password_aqui"
./install.sh
```

El acceso a Grafana estará disponible en el puerto **30000** del cluster (NodePort).
