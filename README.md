# INFORME TÉCNICO DE IMPLEMENTACIÓN Y AUTOMATIZACIÓN DE RED

## 1. Objetivo del proyecto
Este proyecto automatiza e incorpora de forma controlada el nuevo router perimetral corporativo para la empresa cliente Clinica Las Americas SA. El objetivo principal es desplegar la configuración base de seguridad y gestión garantizando cero errores humanos mediante auditorías de compliance independientes de extremo a extremo.

## 2. Alcance
El alcance incluye el aprovisionamiento automatizado del Hostname, Banner de Acceso, Servidor NTP corporativo, Descripción de la Interfaz WAN (GigabitEthernet1) y la creación de la interfaz lógica de Loopback10 para administración remota. No incluye configuraciones de protocolos de enrutamiento dinámico ni listas de control de acceso (ACLs).

## 3. Infraestructura utilizada
- **Estación de Trabajo (VM):** DEVASC VM con Ubuntu Linux y Ansible Core.
- **Dispositivo Objetivo (Router):** Cisco CSR1kv ejecutando Cisco IOS-XE Virtual dentro de VirtualBox.
- **Conectividad:** Interfaz de red Host-Only a través de la subred 192.168.56.0/24.

## 4. Tecnologías empleadas y justificación
- **pyATS / Genie:** Empleado en la Fase 1 y Fase 5 para capturas instantáneas de estado de red multiplataforma no disruptivas y generación de archivos diff estruturados.
- **Ansible:** Utilizado por su naturaleza de motor de automatización sin agentes para desplegar la configuración en bloque garantizando idempotencia en entornos de TI.
- **NETCONF:** Protocolo basado en XML y YANG de lectura para verificar de forma segura y directa los cambios directamente en el plano de control operativo.
- **RESTCONF:** API programable basada en HTTPS/JSON que permite interrogar recursos atómicos individuales de la configuración sin descargar árboles masivos de datos.

## 5. Configuración aplicada
- **Código de alumno:** 005D-03
- **Hostname Corporativo:** RTR-CLINAMER
- **Loopback de gestión:** 10.5.3.1 255.255.255.0
- **Descripción Interfaz WAN:** Enlace-WAN-Concepcion
- **Banner de acceso:** ACCESO RESTRINGIDO - CLINAMER
- **Servidor NTP:** 9.9.9.9

## 6. Resultados de validación
- **Validación NETCONF:** CONFORME (5 de 5 criterios validados con éxito)
- **Validación RESTCONF:** CONFORME (4 de 4 criterios validados con éxito)

## 7. Conclusiones
El aprovisionamiento del enrutador se cerró exitosamente de manera automatizada. Se verificó la total idempotencia del Playbook de Ansible y la consistencia de datos a través de llamadas independientes de API, por lo que el equipo se encuentra validado y en estado óptimo para pasar a operaciones.
