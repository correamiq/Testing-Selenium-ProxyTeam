# TP 0 — Prerrequisitos: k3s + Kubernetes básico
**Seminario de Integración Profesional · UNLu DCB · 2026**  
**Docente:** Dr. David Petrocelli

## Camino A — Instalación de k3s en Debian

### Paso 1: Instalar k3s

**Comando ejecutado:**
```bash
curl -sfL https://get.k3s.io | sh -
```

**Output / evidencia:**
```
valentin@Debian:~/Proyectos/testing/Testing-Selenium-ProxyTeam$ curl -sfL https://get.k3s.io | sh -
[sudo] contraseña para valentin: 
[INFO]  Finding release for channel stable
[INFO]  Using v1.35.4+k3s1 as release
[INFO]  Downloading hash https://github.com/k3s-io/k3s/releases/download/v1.35.4%2Bk3s1/sha256sum-amd64.txt
[INFO]  Skipping binary downloaded, installed k3s matches hash
[INFO]  Skipping installation of SELinux RPM
[INFO]  Skipping /usr/local/bin/kubectl symlink to k3s, already exists
[INFO]  Skipping /usr/local/bin/crictl symlink to k3s, already exists
[INFO]  Skipping /usr/local/bin/ctr symlink to k3s, command exists in PATH at /usr/bin/ctr
[INFO]  Creating killall script /usr/local/bin/k3s-killall.sh
[INFO]  Creating uninstall script /usr/local/bin/k3s-uninstall.sh
[INFO]  env: Creating environment file /etc/systemd/system/k3s.service.env
[INFO]  systemd: Creating service file /etc/systemd/system/k3s.service
[INFO]  systemd: Enabling k3s unit
Created symlink '/etc/systemd/system/multi-user.target.wants/k3s.service' → '/etc/systemd/system/k3s.service'.
[INFO]  No change detected so skipping service start
```

**Notas** : El software ya había sido instalado con anterioridad 

### Paso 2: Verificar que el cluster está vivo


**Comandos ejecutados:**
```bash
sudo k3s kubectl get nodes
```

**Output:**
```
valentin@Debian:~/Proyectos/testing/Testing-Selenium-ProxyTeam$ sudo k3s kubectl get nodes
NAME     STATUS   ROLES           AGE     VERSION
debian   Ready    control-plane   2d22h   v1.35.4+k3s1
```


### Paso 3: Configurar kubectl sin sudo


**Comandos ejecutados:**
```bash
mkdir -p ~/.kube
sudo cp /etc/rancher/k3s/k3s.yaml ~/.kube/config
sudo chown $USER:$USER ~/.kube/config
echo 'export KUBECONFIG=~/.kube/config' >> ~/.bashrc
source ~/.bashrc
kubectl get nodes
```

**Output:**
```
valentin@Debian:~/Proyectos/testing/Testing-Selenium-ProxyTeam$ k3s kubectl get nodes
NAME     STATUS   ROLES           AGE     VERSION
debian   Ready    control-plane   2d22h   v1.35.4+k3s1
```

### Paso 4: Cargar una imagen Docker en k3s


**Comandos ejecutados:**
```bash
# docker save <imagen>:latest -o mi-imagen.tar
# sudo k3s ctr images import mi-imagen.tar
# rm mi-imagen.tar
# sudo k3s ctr images list | grep mi-imagen
```

**Output:**
```
# 
```


### Paso 5: Tirar abajo k3s al terminar el TP


**Comando:**
```bash
sudo /usr/local/bin/k3s-uninstall.sh
```

**Notas:**
> Recordar ejecutarlo cuando termines el TP para liberar ~400-500 MB de RAM.

---

## Hello World — nginx de validación

**Creación del pod**
```bash
valentin@Debian:~/Proyectos/testing/Testing-Selenium-ProxyTeam/tp0$ kubectl apply -f nginx-test.yml
pod/nginx-test created
```

**Verificar que el pod esta corriendo**
```bash
valentin@Debian:~/Proyectos/testing/Testing-Selenium-ProxyTeam/tp0$ kubectl get pod nginx-test --watch
NAME         READY   STATUS    RESTARTS   AGE
nginx-test   1/1     Running   0          2m18s
```

**Haciendo port-forward para probar el pod**
```bash
valentin@Debian:~/Proyectos/testing/Testing-Selenium-ProxyTeam/tp0$ kubectl port-forward pod/nginx-test 8080:80
Forwarding from 127.0.0.1:8080 -> 80
Forwarding from [::1]:8080 -> 80
Handling connection for 8080
```

**Accediendo al nginx con `curl localhost:8080`**
```bash
valentin@Debian:~/Proyectos/testing/Testing-Selenium-ProxyTeam$ curl http://localhost:8080
<!DOCTYPE html>
<html>
<head>
<title>Welcome to nginx!</title>
<style>
html { color-scheme: light dark; }
body { width: 35em; margin: 0 auto;
font-family: Tahoma, Verdana, Arial, sans-serif; }
</style>
</head>
<body>
<h1>Welcome to nginx!</h1>
<p>If you see this page, nginx is successfully installed and working.
Further configuration is required for the web server, reverse proxy, 
API gateway, load balancer, content cache, or other features.</p>

<p>For online documentation and support please refer to
<a href="https://nginx.org/">nginx.org</a>.<br/>
To engage with the community please visit
<a href="https://community.nginx.org/">community.nginx.org</a>.<br/>
For enterprise grade support, professional services, additional 
security features and capabilities please refer to
<a href="https://f5.com/nginx">f5.com/nginx</a>.</p>

<p><em>Thank you for using nginx.</em></p>
</body>
</html>
```

**Limpieza**
```bash
valentin@Debian:~/Proyectos/testing/Testing-Selenium-ProxyTeam/tp0$ kubectl delete -f nginx-test.yml
pod "nginx-test" deleted from default namespace
```
