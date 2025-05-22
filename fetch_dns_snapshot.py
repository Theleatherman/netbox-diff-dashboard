from dns_cache import store_dns_cache
from config import NETBOX_API_URL, NETBOX_API_TOKEN, DNS_SERVER, DNS_HOSTNAME, CERT_PEM, CERT_KEY_PEM
import winrm

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
    } | Select-Object @{Name="IPAddress";Expression={$_.RecordData.IPv4Address.IPAddressToString}}, HostName, ZoneName
}
$records | ConvertTo-Json -Depth 3
"""

result = session.run_ps(ps_script)

if result.status_code != 0:
    raise RuntimeError(result.std_err.decode())

entries = []
import json
out = result.std_out.decode().strip()
err = result.std_err.decode("utf-8", errors="replace").strip()

if not out:
    print("❌ Keine Ausgabe erhalten.")
    print("STDERR:\n", err)
    exit(1)

records = json.loads(out)

print("STDOUT (erste 500 Zeichen):")
print(out[:500])

print("STDERR (PowerShell-Fehler):")
print(result.std_err.decode("utf-8", errors="replace"))


for r in records:
    if r.get("IPAddress") and r.get("HostName"):
        entries.append({
            "ip": r["IPAddress"],
            "hostname": r["HostName"],
            "zone": r.get("ZoneName", "")
})

store_dns_cache(entries)
print(f"✅ {len(entries)} DNS-Records gespeichert.")