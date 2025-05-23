import json
import urllib3
import requests
import winrm
from ipaddress import ip_address

from config import NETBOX_API_URL, NETBOX_API_TOKEN, DNS_SERVER, CERT_PEM, CERT_KEY_PEM
from dns_cache import load_dns_cache, get_dns_cache_age
from netbox import get_mgmt_ips  # ← wichtig: deine Funktion, die list[tuple] zurückgibt

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

NETBOX_API_HEADERS = {
    "Authorization": f"Token {NETBOX_API_TOKEN}"
} if NETBOX_API_TOKEN else {}

def get_netbox_ips():
    """
    Wandelt Ergebnis von get_mgmt_ips() in IP→Hostname-map um
    """
    return {
        ip: dns
        for (ip, desc, dns, tags) in get_mgmt_ips()
        if ip and dns and isinstance(dns, str)
    }

def get_dns_records_via_winrm():
    session = winrm.Session(
        f"https://{DNS_SERVER}:5986/wsman",
        auth=("dummy", "dummy"),
        transport="certificate",
        cert_pem=CERT_PEM,
        cert_key_pem=CERT_KEY_PEM,
        server_cert_validation="ignore"
    )

    ps_script = """
    $records = @()
    Get-DnsServerZone | ForEach-Object {
        $zone = $_.ZoneName
        $records += Get-DnsServerResourceRecord -ZoneName $zone | Where-Object {
            $_.RecordType -eq 'A' -or $_.RecordType -eq 'PTR'
        } | Select-Object @{Name="IPAddress";Expression={$_.RecordData.IPv4Address.IPAddressToString}}, HostName, RecordType, ZoneName
    }
    $records | ConvertTo-Json -Depth 3
    """

    result = session.run_ps(ps_script)

    if result.status_code != 0:
        raise RuntimeError(f"DNS Query via WinRM failed: {result.std_err.decode()}")

    records = json.loads(result.std_out.decode())
    ip_hostname_map = {}

    for rec in records:
        ip = rec.get("IPAddress")
        hostname = rec.get("HostName")
        if ip:
            ip_hostname_map[ip] = hostname.lower() if hostname else ""

    return ip_hostname_map

def get_ip_hostname_diff():
    netbox_map = {
        ip.split("/")[0]: dns
        for (ip, desc, dns, tags) in get_mgmt_ips()
        if ip and dns and isinstance(dns, str)
    }
    dns_map = load_dns_cache()

    only_in_netbox = {
        ip: netbox_map[ip]
        for ip in netbox_map
        if ip not in dns_map
    }

    only_in_dns = {
        ip: dns_map[ip]
        for ip in dns_map
        if ip not in netbox_map
    }

    in_both = []
    hostname_mismatches = []

    for ip in netbox_map:
        if ip in dns_map:
            netbox_host = netbox_map[ip]
            dns_host = dns_map[ip]
            in_both.append((ip, netbox_host, dns_host))
            if (
                isinstance(netbox_host, str)
                and isinstance(dns_host, str)
                and netbox_host and dns_host
                and netbox_host.lower() != dns_host.lower()
            ):
                hostname_mismatches.append((ip, netbox_host, dns_host))

    return {
        "only_in_netbox": only_in_netbox,
        "only_in_dns": only_in_dns,
        "both": in_both,
        "hostname_mismatches": hostname_mismatches
    }
