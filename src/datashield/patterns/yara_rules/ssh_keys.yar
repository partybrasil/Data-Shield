rule SSH_Private_Key
{
    meta:
        description = "SSH/TLS private key in PEM format"
        severity    = "CRITICAL"
        data_type   = "ssh_private_key"
        risk_score  = 95

    strings:
        $rsa      = "-----BEGIN RSA PRIVATE KEY-----"
        $ec       = "-----BEGIN EC PRIVATE KEY-----"
        $dsa      = "-----BEGIN DSA PRIVATE KEY-----"
        $openssh  = "-----BEGIN OPENSSH PRIVATE KEY-----"
        $pkcs8    = "-----BEGIN PRIVATE KEY-----"
        $enc_pkcs8= "-----BEGIN ENCRYPTED PRIVATE KEY-----"

    condition:
        any of them
}

rule PGP_Private_Key
{
    meta:
        description = "PGP/GPG private key block"
        severity    = "CRITICAL"
        data_type   = "pgp_private_key"
        risk_score  = 92

    strings:
        $pgp_priv = "-----BEGIN PGP PRIVATE KEY BLOCK-----"

    condition:
        $pgp_priv
}

rule X509_Certificate
{
    meta:
        description = "X.509 certificate"
        severity    = "MEDIUM"
        data_type   = "x509_certificate"
        risk_score  = 45

    strings:
        $cert = "-----BEGIN CERTIFICATE-----"

    condition:
        $cert
}
