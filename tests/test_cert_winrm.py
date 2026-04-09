import winrm

# Konfiguration (anpassen!)
DNS_SERVER = "10.1.0.2"
CERT_PEM = "/etc/ssl/client_cert.pem"
CERT_KEY = "/etc/ssl/client_key.pem"

# Verbindungsaufbau
try:
    session = winrm.Session(
        f"https://{DNS_SERVER}:5986/wsman",
        auth=("dummy", "dummy"),  # wird bei transport="certificate" ignoriert
        transport="certificate",
        cert_pem=CERT_PEM,
        cert_key_pem=CERT_KEY,
        server_cert_validation="ignore"  # bei echtem CA-Zertifikat: "validate"
    )

    r = session.run_cmd("hostname")
    print("Status Code:", r.status_code)
    print("STDOUT:\n", r.std_out.decode("utf-8"))
    print("STDERR:\n", r.std_err.decode("utf-8"))

except Exception as e:
    print("❌ Verbindung fehlgeschlagen:", str(e))
