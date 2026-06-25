#!/usr/bin/env python3
import os
import sys
from datetime import datetime

# 1. Inicializar Metadatos
print("==================================================")
print("Script: generar_certificado.py")
print(f"Fecha/Hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print(f"Host VM: {os.uname()[1]}")
print("==================================================")

# Rutas de evidencias previas
netconf_log = "../fase3_validacion_netconf/evidencias/output_validacion_netconf.txt"
restconf_log = "../fase4_validacion_restconf/evidencias/output_validacion_restconf.txt"

# Leer estados de validación anteriores
netconf_ok = False
restconf_ok = False

if os.path.exists(netconf_log):
    with open(netconf_log, "r") as f:
        if "Resultado global: CONFORME" in f.read():
            netconf_ok = True

if os.path.exists(restconf_log):
    with open(restconf_log, "r") as f:
        if "Resultado global: CONFORME" in f.read():
            restconf_ok = True

# 2. Construir el Certificado de Compliance Exigido
os.makedirs("evidencias", exist_ok=True)
cert_path = "evidencias/certificado_compliance_005D_03.txt"

status_netconf = "CONFORME" if netconf_ok else "NO CONFORME"
status_restconf = "CONFORME" if restconf_ok else "NO CONFORME"
status_global = "CONFORME" if (netconf_ok and restconf_ok) else "NO CONFORME"

certificado_contenido = f"""==================================================
CERTIFICADO DE COMPLIANCE DE AUDITORÍA DE RED
==================================================
Código Alumno   : 005D-03
Nombre Alumno   : Victor Exequiel Arriagada Troncoso
Empresa Cliente : Clinica Las Americas SA
Fecha Emisión   : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
--------------------------------------------------
RESULTADOS DE VERIFICACIÓN INDEPENDIENTE:
--------------------------------------------------
- Auditoría vía PROTOCOLO NETCONF : {status_netconf}
- Auditoría vía PROTOCOLO RESTCONF: {status_restconf}
--------------------------------------------------
DICTAMEN FINAL:
EQUIPO ESTADO GLOBAL: {status_global}
=================================================="""

# Guardar el archivo físico
with open(cert_path, "w") as cert_file:
    cert_file.write(certificado_contenido)

# Imprimir por pantalla para control
print(certificado_contenido)
