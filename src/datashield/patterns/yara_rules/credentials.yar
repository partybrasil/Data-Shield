rule AWS_Credentials
{
    meta:
        description = "AWS access key or secret key in plaintext"
        severity    = "CRITICAL"
        risk_score  = 90

    strings:
        $access_key    = /AKIA[0-9A-Z]{16}/
        $secret_label  = /aws_secret_access_key/i
        $session_token = /FwoGZXIvYXdz/

    condition:
        $access_key or $secret_label or $session_token
}

rule GitHub_Token
{
    meta:
        description = "GitHub Personal Access Token"
        severity    = "HIGH"
        risk_score  = 80

    strings:
        $ghp  = /ghp_[0-9a-zA-Z]{36}/
        $gho  = /gho_[0-9a-zA-Z]{36}/
        $ghs  = /ghs_[0-9a-zA-Z]{36}/
        $ghu  = /ghu_[0-9a-zA-Z]{36}/
        $fine = /github_pat_[0-9a-zA-Z_]{82}/

    condition:
        any of them
}

rule Generic_Password_Field
{
    meta:
        description = "Password field assignment in config/source files"
        severity    = "MEDIUM"
        risk_score  = 65

    strings:
        $pwd1 = /password\s*=\s*[^\s]{8,}/i
        $pwd2 = /passwd\s*=\s*[^\s]{8,}/i
        $pwd3 = /\"password\"\s*:\s*\"[^\"]{8,}\"/i

    condition:
        any of them
}

rule Stripe_Key
{
    meta:
        description = "Stripe live secret or restricted key"
        severity    = "CRITICAL"
        risk_score  = 95

    strings:
        $sk = /sk_live_[0-9a-zA-Z]{24,}/
        $rk = /rk_live_[0-9a-zA-Z]{24,}/

    condition:
        any of them
}

rule JWT_Token
{
    meta:
        description = "JSON Web Token (JWT)"
        severity    = "HIGH"
        risk_score  = 75

    strings:
        $jwt = /eyJ[A-Za-z0-9\-_]{10,}\.eyJ[A-Za-z0-9\-_]{10,}\.[A-Za-z0-9\-_]{10,}/

    condition:
        $jwt
}

rule Database_Connection_String
{
    meta:
        description = "Database connection string with embedded credentials"
        severity    = "HIGH"
        risk_score  = 88

    strings:
        $pg     = /postgres:\/\/[^:]+:[^@]+@/
        $mysql  = /mysql:\/\/[^:]+:[^@]+@/
        $mongo  = /mongodb\+srv:\/\/[^:]+:[^@]+@/
        $redis  = /redis:\/\/:[^@]+@/

    condition:
        any of them
}

rule OpenAI_API_Key
{
    meta:
        description = "OpenAI API key"
        severity    = "HIGH"
        risk_score  = 82

    strings:
        $v1   = /sk-[A-Za-z0-9]{20}T3BlbkFJ[A-Za-z0-9]{20}/
        $v2   = /sk-proj-[0-9A-Za-z\-_]{50,}/
        $ant  = /sk-ant-[0-9a-zA-Z\-_]{90,}/

    condition:
        any of them
}
