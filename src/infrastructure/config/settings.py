import os
import config.environment

class BaseSettings:
    """共通設定"""
    APP_NAME = "StockPulse"
    DEBUG = os.getenv("DEBUG", "False").lower() == "true"

    AWS_REGION = os.getenv("AWS_REGION", "ap-northeast-1")
    S3_BUCKET = os.getenv("S3_BUCKET")

    LINE_ACCESS_TOKEN = os.getenv("LINE_ACCESS_TOKEN")
    LINE_USER_IDS = os.getenv("LINE_USER_IDS", "").split(',')


class DevelopmentSettings(BaseSettings):
    """開発環境設定"""
    APP_ENV = "development"
    DEBUG = True

class ProductionSettings(BaseSettings):
    """本番環境設定"""
    APP_ENV = "production"
    DEBUG = False

APP_ENV = os.getenv("APP_ENV", "development")

if APP_ENV == "production":
    settings = ProductionSettings()
else:
    settings = DevelopmentSettings()
