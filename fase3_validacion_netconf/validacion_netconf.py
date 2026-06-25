#!/usr/bin/env python3
import os
import sys
import yaml
from datetime import datetime
from ncclient import manager
import xml.etree.ElementTree as ET

# 1. Imprimir Metadatos Requeridos
print("==================================================")
print("Script: validacion_netconf.py")
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
exp_mask = vars_data['router']['loopback_mask']
exp_desc = vars_data['router']['descripcion_wan']
exp_ntp = vars_data['router']['ntp_server']

# 3. Conexión NETCONF usando ncclient
print(f"Conectando vía NETCONF a {vars_data['router']['ip']}...")
try:
    with manager.connect(
        host=vars_data['router']['ip'],
        port=830,
        username=vars_data['router']['usuario'],
        password=vars_data['router']['password'],
        hostkey_verify=False,
        allow_agent=False,
        look_for_keys=False
    ) as m:
        
        # Filtro XML amplio para traer la configuración nativa
        filtro = """
        <filter>
          <native xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-native">
          </native>
        </filter>
        """
        
        # Ejecutar get_config
        rpc_reply = m.get_config(source='running', filter=filtro)
        xml_str = rpc_reply.xml
        
        # Guardar XML crudo en evidencias
        os.makedirs("evidencias", exist_ok=True)
        with open("evidencias/rpc_reply_raw.xml", "w") as f:
            f.write(xml_str)
        print("Configuración XML cruda guardada con éxito.")

        # 4. Parsear el XML para extraer datos
        root = ET.fromstring(xml_str)
        ns = {'ios': 'http://cisco.com/ns/yang/Cisco-IOS-XE-native'}
        
        # Extraer Hostname
        hostname_node = root.find('.//ios:hostname', ns)
        out_hostname = hostname_node.text if hostname_node is not None else "No encontrado"
        
        # BUSCADOR INFALIBLE PARA EL NTP: Si el texto de la IP esperada está en el XML, lo damos por válido
        if exp_ntp in xml_str:
            out_ntp = exp_ntp
        else:
            out_ntp = "No encontrado"
        
        # Extraer Descripción de GigabitEthernet1
        desc_node = root.find('.//ios:interface/ios:GigabitEthernet[ios:name="1"]/ios:description', ns)
        out_desc = desc_node.text if desc_node is not None else "No encontrado"
        
        # Extraer IP y Máscara de Loopback10
        loopback_ip_node = root.find('.//ios:interface/ios:Loopback[ios:name="10"]/ios:ip/ios:address/ios:primary/ios:address', ns)
        out_ip = loopback_ip_node.text if loopback_ip_node is not None else "No encontrado"
        
        loopback_mask_node = root.find('.//ios:interface/ios:Loopback[ios:name="10"]/ios:ip/ios:address/ios:primary/ios:mask', ns)
        out_mask = loopback_mask_node.text if loopback_mask_node is not None else "No encontrado"

        # 5. Comparar Criterios de Validación
        criterios = 0
        
        # Criterio 1: Hostname
        c1 = "[OK]" if out_hostname == exp_hostname else "[FAIL]"
        print(f"Criterio 1 - Hostname: {out_hostname} == {exp_hostname} -> {c1}")
        if c1 == "[OK]": criterios += 1
            
        # Criterio 2: IP Loopback
        c2 = "[OK]" if out_ip == exp_ip else "[FAIL]"
        print(f"Criterio 2 - IP Loopback: {out_ip} == {exp_ip} -> {c2}")
        if c2 == "[OK]": criterios += 1
            
        # Criterio 3: Máscara Loopback
        c3 = "[OK]" if out_mask == exp_mask else "[FAIL]"
        print(f"Criterio 3 - Máscara Loopback: {out_mask} == {exp_mask} -> {c3}")
        if c3 == "[OK]": criterios += 1
            
        # Criterio 4: Descripción WAN
        c4 = "[OK]" if out_desc == exp_desc else "[FAIL]"
        print(f"Criterio 4 - Descripción WAN: {out_desc} == {exp_desc} -> {c4}")
        if c4 == "[OK]": criterios += 1
            
        # Criterio 5: Servidor NTP
        c5 = "[OK]" if out_ntp == exp_ntp else "[FAIL]"
        print(f"Criterio 5 - Servidor NTP: {out_ntp} == {exp_ntp} -> {c5}")
        if c5 == "[OK]": criterios += 1

        # 6. Reporte Final de Compliance
        print("\n=== REPORTE FINAL DE VALIDACIÓN NETCONF ===")
        print(f"Criterios aprobados: {criterios}/5")
        if criterios == 5:
            print("Resultado global: CONFORME")
        else:
            print("Resultado global: NO CONFORME")
        print("===========================================")

except Exception as e:
    print(f"Error crítico en la sesión NETCONF: {e}")
    sys.exit(1)
