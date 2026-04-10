import winrm

# Konfiguration (anpassen!)
DNS_SERVER = "10.1.0.2"
CERT_PEM = "/etc/ssl/client_cert.pem"
CERT_KEY = "/etc/ssl/client_key.pem"


def run_cert_auth_winrm_check() -> int:
    """Manual connectivity helper for certificate-authenticated WinRM."""
    try:
        session = winrm.Session(
            f"https://{DNS_SERVER}:5986/wsman",
            auth=("dummy", "dummy"),  # wird bei transport="certificate" ignoriert
            transport="certificate",
            cert_pem=CERT_PEM,
            cert_key_pem=CERT_KEY,
            server_cert_validation="ignore",  # bei echtem CA-Zertifikat: "validate"
        )

        result = session.run_cmd("hostname")
        print("Status Code:", result.status_code)
        print("STDOUT:\n", result.std_out.decode("utf-8"))
        print("STDERR:\n", result.std_err.decode("utf-8"))
        return result.status_code
    except Exception as exc:
        print("WinRM-Verbindung fehlgeschlagen:", str(exc))
        return 1


if __name__ == "__main__":
    raise SystemExit(run_cert_auth_winrm_check())
