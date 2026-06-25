#!/usr/bin/env python3
import os
import sys
import yaml
import json
import requests
from datetime import datetime

# Deshabilitar advertencias de certificados SSL autofirmados
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# 1. Imprimir Metadatos Requeridos
print("==================================================")
print("Script: validacion_restconf.py")
print(f"Fecha/Hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print(f"Host VM: {os.uname()[1]}")
print("==================================================")

# 2. Cargar variables del archivo centralizado
vars_path = "../vars/vars_005D_03.yaml"
try:
    with open(vars_path, 'r') as f:
        vars_data = yaml.safe_load(f)
except Exception as e:
    print(f"Error al cargar variables: {e}")
    sys.exit(1)

# Variables esperadas
exp_hostname = vars_data['cliente']['hostname']
exp_ip = vars_data['router']['loopback_ip']
exp_desc = vars_data['router']['descripcion_wan']
exp_ntp = vars_data['router']['ntp_server']

# Configuración de la API RESTCONF
router_ip = vars_data['router']['ip']
auth = (vars_data['router']['usuario'], vars_data['router']['password'])
headers = {
    "Accept": "application/yang-data+json",
    "Content-Type": "application/yang-data+json"
}

base_url = f"https://{router_ip}/restconf/data"

# Endpoints a consultar mapeados con su archivo de salida correspondiente
endpoints = {
    "hostname": (f"{base_url}/Cisco-IOS-XE-native:native/hostname", "get_hostname.json"),
    "loopback": (f"{base_url}/ietf-interfaces:interfaces/interface=Loopback10", "get_loopback.json"),
    "interface": (f"{base_url}/ietf-interfaces:interfaces/interface=GigabitEthernet1", "get_interfaces.json"),
    "ntp": (f"{base_url}/Cisco-IOS-XE-native:native/ntp", "get_ntp.json")
}

responses_data = {}

print("Consultando endpoints RESTCONF...")
for key, (url, filename) in endpoints.items():
    try:
        response = requests.get(url, auth=auth, headers=headers, verify=False, timeout=10)
        if response.status_code == 200:
            data = response.json()
            responses_data[key] = data
            
            # Guardar el JSON crudo de la respuesta en la ruta exacta solicitada
            filepath = f"evidencias/responses/{filename}"
            with open(filepath, "w") as f:
                json.dump(data, f, indent=4)
        else:
            print(f"Advertencia: Endpoint {key} retornó código {response.status_code}")
            responses_data[key] = None
    except Exception as e:
        print(f"Error al consultar {key}: {e}")
        responses_data[key] = None

# 3. Procesar y Comparar Criterios de Validación
criterios = 0
print("\nIniciando análisis de criterios...")

# Criterio 1: Hostname Corporativo
out_hostname = "No encontrado"
if responses_data.get("hostname"):
    try: out_hostname = responses_data["hostname"]["Cisco-IOS-XE-native:hostname"]
    except: pass
c1 = "[OK]" if out_hostname == exp_hostname else "[FAIL]"
print(f"Criterio 1 - Hostname: {out_hostname} == {exp_hostname} -> {c1}")
if c1 == "[OK]": criterios += 1

# Criterio 2: IP del Loopback
out_ip = "No encontrado"
if responses_data.get("loopback"):
    try: out_ip = responses_data["loopback"]["ietf-interfaces:interface"]["ietf-ip:ipv4"]["address"][0]["ip"]
    except: pass
c2 = "[OK]" if out_ip == exp_ip else "[FAIL]"
print(f"Criterio 2 - IP Loopback: {out_ip} == {exp_ip} -> {c2}")
if c2 == "[OK]": criterios += 1

# Criterio 3: Descripción WAN
out_desc = "No encontrado"
if responses_data.get("interface"):
    try: out_desc = responses_data["interface"]["ietf-interfaces:interface"]["description"]
    except: pass
c3 = "[OK]" if out_desc == exp_desc else "[FAIL]"
print(f"Criterio 3 - Descripción WAN: {out_desc} == {exp_desc} -> {c3}")
if c3 == "[OK]": criterios += 1

# Criterio 4: Servidor NTP (Búsqueda textual infalible en JSON)
out_ntp = "No encontrado"
if responses_data.get("ntp"):
    ntp_str = json.dumps(responses_data["ntp"])
    if exp_ntp in ntp_str:
        out_ntp = exp_ntp
c4 = "[OK]" if out_ntp == exp_ntp else "[FAIL]"
print(f"Criterio 4 - Servidor NTP: {out_ntp} == {exp_ntp} -> {c4}")
if c4 == "[OK]": criterios += 1

# 4. Reporte Final de Compliance RESTCONF
print("\n=== REPORTE FINAL DE VALIDACIÓN RESTCONF ===")
print(f"Criterios aprobados: {criterios}/4")
if criterios == 4:
    print("Resultado global: CONFORME")
else:
    print("Resultado global: NO CONFORME")
print("===========================================")
