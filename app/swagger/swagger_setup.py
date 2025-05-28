# C:\Users\ianes\Desktop\BigData-2025.1\app\swagger\swagger_setup.py

from flask_restx import Api
from app.swagger.swagger_config import (
    SWAGGER_TITLE,
    SWAGGER_DESC,
    SWAGGER_VERSION,
    SWAGGER_DOC
)

def configure_swagger(app):
    """
    Configura a documentação da API usando Flask-RESTX.
    Retorna uma instância da classe Api, que usaremos para registrar namespaces.
    """
    api = Api(
        app,
        version=SWAGGER_VERSION,
        title=SWAGGER_TITLE,
        description=SWAGGER_DESC,
        doc=SWAGGER_DOC  # Exemplo: /docs
    )
    return api
