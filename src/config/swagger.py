template = {
    "swagger": "2.0",
    "info": {
        "title": "E-Services API",
        "description": "API for E-Services",
        "contact": {
            "responsibleOrganization": "",
            "responsibleDeveloper": "",
            "email": "ugbogu@yahoo.com",
            "url": "http://www.gjengineer.com",
        },
        "termsOfService": "http://www.gjengineer.com/terms",
        "version": "1.0"
    },
    "basePath": "/api/v1",  # base bash for blueprint registration
    "schemes": [
        "http",
        "https"
    ],
    "securityDefinitions": {
        "APIKeyHeader": {
            "type": "apiKey",
            "name": "Authorization",
            "in": "header",
            "description": "JWT Authorization header using the Bearer scheme. Example: \"Authorization: Bearer {token}\""
        }
    },
}

swagger_config = {
    "headers": [
    ],
    "specs": [
        {
            "endpoint": 'apispec',
            "route": '/apispec.json',
            "rule_filter": lambda rule: True,  # all in
            "model_filter": lambda tag: True,  # all in
        }
    ],
    "static_url_path": "/flasgger_static",
    "swagger_ui": True,
    "specs_route": "/"
}
