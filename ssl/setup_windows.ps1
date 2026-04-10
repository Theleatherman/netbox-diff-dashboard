using namespace System.Management.Automation
using namespace System.Security.Cryptography
using namespace System.Security.Cryptography.X509Certificates

#Requires -RunAsAdministrator
#Requires -Version 5.1

[CmdletBinding()]
param (
    [Parameter(Mandatory)]
    [string]
    $CACert,

    [Parameter(Mandatory)]
    [string]
    $ClientCert
)

$ErrorActionPreference = 'Stop'

$caCertPath = $ExecutionContext.SessionState.Path.GetUnresolvedProviderPathFromPSPath($CACert)
try {
    $caCertObj = [X509Certificate2]::new($caCertPath)
}
catch {
    $_.ErrorDetails = "Failed to load CACert: $($_.Exception.InnerException.Message)"
    $PSCmdlet.WriteError($_)
    return
}

$clientCertPath = $ExecutionContext.SessionState.Path.GetUnresolvedProviderPathFromPSPath($ClientCert)
try {
    $clientCertObj = [X509Certificate2]::new($clientCertPath)
}
catch {
    $_.ErrorDetails = "Failed to load ClientCert: $($_.Exception.InnerException.Message)"
    $PSCmdlet.WriteError($_)
    return
}

Write-Verbose "Adding CA certificate to Cert:\LocalMachine\Root"
$rootStore = Get-Item -LiteralPath Cert:\LocalMachine\Root
$rootStore.Open([OpenFlags]::ReadWrite)
$rootStore.Add($caCertObj)
$rootStore.Close()

Write-Verbose "Adding client certificate to Cert:\LocalMachine\TrustedPeople"
$trustedPeopleStore = Get-Item -LiteralPath Cert:\LocalMachine\TrustedPeople
$trustedPeopleStore.Open([OpenFlags]::ReadWrite)
$trustedPeopleStore.Add($clientCertObj)
$trustedPeopleStore.Close()

# Get username and generate our password.
# We use RandomNumberGenerator as the Guid type has no guarantees it uses an
# RNG to generate the bytes. This is still not ideal but works for our example
# purposes here.
$userName = "winrm.service"
$userPass = "YvfXbjFLxM77"

$createUserParams = @{
    Name = $userName
    Description = "username for WinRM Certificate Auth"
    Password = ConvertTo-SecureString -AsPlainText -Force -String $userPass
    PasswordNeverExpires = $true
    UserMayNotChangePassword = $true
}
Write-Verbose -Message "Creating local user '$($createUserParams.Name)'"
New-LocalUser @createUserParams | Add-LocalGroupMember -Group DnsAdmins

$certMapping = @{
    Path = 'WSMan:\localhost\ClientCertificate'
    Issuer = $caCertObj.Thumbprint
    Credential = [PSCredential]::new($createUserParams.Name, $createUserParams.Password)
    Force = $true
}
Write-Verbose -Message "Creating WSMan username mapping for '$($certMapping.Subject)'"
$null = New-Item @certMapping

Write-Verbose -Message "Enabling WSMan Certificate auth"
Set-Item -LiteralPath WSMan:\localhost\Service\Auth\Certificate -Value True

Write-Host -Object "Created local user '$($createUserParams.Name)' with password '$userPass'" -ForegroundColor Green
