from pydantic_settings import BaseSettings
from pydantic import AnyUrl, AnyHttpUrl, EmailStr

class LoggerSettings(BaseSettings):
    logfile_path: str = "./logs"
    logfile_name: str = "coreid.log"
    logfile_max_size_bytes: int = 10*1024*1024
    logfile_max_count: int = 5

class ConnectionSettings(BaseSettings):
    database_url: AnyUrl

class APIKeys(BaseSettings):
    resend: str

class EmailSettings(BaseSettings):
    sender_name: str
    sender_email: str
    reply_email: str

class ContactInfo(BaseSettings):
    distributor_name: str = "ProcentrIQ"
    distributor_website: AnyHttpUrl = "https://procentriq.ch"
    distributor_contact_email: EmailStr
    tos_url: AnyHttpUrl

class SecuritySettings(BaseSettings):
    authorization_code_length: int = 36
    authorization_code_validity_seconds: int = 60*2
    email_verification_code_validity_seconds: int = 60*15

class Settings(BaseSettings):
    environment: str = "development"
    app_name: str = "CoreID"
    app_host: str = "0.0.0.0"
    app_host_public_url: str
    app_port: int = 8000
    app_version: str
    contact: ContactInfo
    tenant_name: str
    logging: LoggerSettings = LoggerSettings()
    debug: bool = False
    connections: ConnectionSettings
    api_keys: APIKeys
    email: EmailSettings
    security: SecuritySettings = SecuritySettings()

    class Config:
        env_prefix = ""  # To support env variables without a prefix
        case_sensitive = False