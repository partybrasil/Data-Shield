rule High_Entropy_Blob
{
    meta:
        description = "Generic high-entropy region, likely encrypted or encoded secret"
        severity    = "MEDIUM"
        risk_score  = 50

    strings:
        // Base64-like: at least 40 contiguous base64 chars (possible encoded key)
        $b64_long = /[A-Za-z0-9+\/]{40,}={0,2}/

    condition:
        $b64_long
}

rule High_Entropy_Hex
{
    meta:
        description = "Long hexadecimal string, possible hash or key"
        severity    = "MEDIUM"
        risk_score  = 48

    strings:
        $hex_long = /[0-9a-fA-F]{64,}/

    condition:
        $hex_long
}
