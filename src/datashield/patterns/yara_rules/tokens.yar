rule OAuth_Bearer_Token
{
    meta:
        description = "OAuth Bearer or access token pattern"
        severity    = "HIGH"
        risk_score  = 75

    strings:
        $bearer  = /Bearer\s+[A-Za-z0-9\-_\.]{20,}/i
        $oauth   = /access_token[\"']?\s*:\s*[\"']?[A-Za-z0-9\-_\.]{20,}/i
        $refresh = /refresh_token[\"']?\s*:\s*[\"']?[A-Za-z0-9\-_\.]{20,}/i

    condition:
        any of them
}

rule Slack_Token
{
    meta:
        description = "Slack bot or user token"
        severity    = "HIGH"
        risk_score  = 80

    strings:
        $bot  = /xoxb-[0-9]{11}-[0-9]{11}-[0-9a-zA-Z]{24}/
        $user = /xoxp-[0-9]{11}-[0-9]{11}-[0-9]{11}-[0-9a-f]{32}/

    condition:
        any of them
}

rule NPM_Token
{
    meta:
        description = "NPM authentication token"
        severity    = "HIGH"
        risk_score  = 78

    strings:
        $npm = /npm_[0-9A-Za-z]{36}/
        $npmrc_auth = /_authToken\s*=\s*[A-Za-z0-9\-_]{20,}/

    condition:
        any of them
}

rule Terraform_Cloud_Token
{
    meta:
        description = "HashiCorp Terraform Cloud token"
        severity    = "HIGH"
        risk_score  = 82

    strings:
        $tf = /[0-9A-Za-z]{14}\.atlasv1\.[0-9A-Za-z]{67}/
        $hcv = /hvs\.[A-Za-z0-9]{24,}/

    condition:
        any of them
}

rule Docker_Auth
{
    meta:
        description = "Docker registry auth (base64 encoded)"
        severity    = "HIGH"
        risk_score  = 78

    strings:
        $auth_field = /"auth"\s*:\s*"[A-Za-z0-9+\/=]{20,}"/

    condition:
        $auth_field
}
