rule X509_DER_Certificate
{
    meta:
        description = "DER-encoded X.509 certificate (binary)"
        severity    = "LOW"
        risk_score  = 40

    strings:
        // DER SEQUENCE header for X.509: 30 82 ?? ?? 30 82
        $der_cert = { 30 82 ?? ?? 30 82 }

    condition:
        $der_cert at 0
}

rule PKCS12_Keystore
{
    meta:
        description = "PKCS#12 / PFX keystore (binary) — contains private key"
        severity    = "CRITICAL"
        risk_score  = 88

    strings:
        // PFX DER header: SEQUENCE { INTEGER 3, ... }
        $pfx_header = { 30 82 ?? ?? 02 01 03 }

    condition:
        $pfx_header at 0
}

rule Java_KeyStore
{
    meta:
        description = "Java KeyStore (JKS) binary file"
        severity    = "HIGH"
        risk_score  = 85

    strings:
        $jks_magic = { FE ED FE ED }

    condition:
        $jks_magic at 0
}
