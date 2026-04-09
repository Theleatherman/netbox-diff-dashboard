import winrm
session = winrm.Session(
    "https://10.1.0.2:5986/wsman",
    auth=("dummy", "dummy"),
    transport="certificate",
    cert_pem="/etc/ssl/client_cert.pem",
    cert_key_pem="/etc/ssl/client_key.pem",
    server_cert_validation="ignore"
)
r = session.run_cmd("hostname")
print(r.status_code)
print(r.std_out.decode())
