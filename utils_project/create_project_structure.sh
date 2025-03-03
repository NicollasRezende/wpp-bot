#!/bin/bash

echo "Criando estrutura de diretórios..."

# Criar diretórios principais
mkdir -p whatsapp_api/config
mkdir -p whatsapp_api/app/api/endpoints
mkdir -p whatsapp_api/app/core
mkdir -p whatsapp_api/app/db/crud
mkdir -p whatsapp_api/app/models
mkdir -p whatsapp_api/app/schemas
mkdir -p whatsapp_api/app/services
mkdir -p whatsapp_api/app/utils
mkdir -p whatsapp_api/tests/test_api
mkdir -p whatsapp_api/tests/test_services
mkdir -p whatsapp_api/alembic/versions
mkdir -p whatsapp_api/media
mkdir -p whatsapp_api/logs

echo "Criando arquivos __init__.py..."

# Criar arquivos __init__.py em todos os diretórios Python
touch whatsapp_api/__init__.py
touch whatsapp_api/config/__init__.py
touch whatsapp_api/app/__init__.py
touch whatsapp_api/app/api/__init__.py
touch whatsapp_api/app/api/endpoints/__init__.py
touch whatsapp_api/app/core/__init__.py
touch whatsapp_api/app/db/__init__.py
touch whatsapp_api/app/db/crud/__init__.py
touch whatsapp_api/app/models/__init__.py
touch whatsapp_api/app/schemas/__init__.py
touch whatsapp_api/app/services/__init__.py
touch whatsapp_api/app/utils/__init__.py
touch whatsapp_api/tests/__init__.py
touch whatsapp_api/tests/test_api/__init__.py
touch whatsapp_api/tests/test_services/__init__.py

echo "Criando arquivos principais..."

# Criar arquivos na raiz
touch whatsapp_api/.env
touch whatsapp_api/requirements.txt
touch whatsapp_api/README.md
touch whatsapp_api/main.py
touch whatsapp_api/.gitignore
touch whatsapp_api/alembic.ini

# Criar arquivos de configuração
touch whatsapp_api/config/settings.py
touch whatsapp_api/config/database.py

# Criar módulos principais
touch whatsapp_api/app/api/dependencies.py
touch whatsapp_api/app/api/exceptions.py
touch whatsapp_api/app/api/router.py
touch whatsapp_api/app/api/endpoints/webhook.py
touch whatsapp_api/app/api/endpoints/admin.py

# Criar módulos de core
touch whatsapp_api/app/core/security.py
touch whatsapp_api/app/core/exceptions.py
touch whatsapp_api/app/core/session.py

# Criar módulos de banco de dados
touch whatsapp_api/app/db/base.py
touch whatsapp_api/app/db/session.py
touch whatsapp_api/app/db/crud/base.py
touch whatsapp_api/app/db/crud/user.py
touch whatsapp_api/app/db/crud/menu.py

# Criar modelos
touch whatsapp_api/app/models/user.py
touch whatsapp_api/app/models/menu.py

# Criar schemas
touch whatsapp_api/app/schemas/user.py
touch whatsapp_api/app/schemas/menu.py

# Criar serviços
touch whatsapp_api/app/services/whatsapp.py
touch whatsapp_api/app/services/menu.py
touch whatsapp_api/app/services/logger.py

# Criar utilitários
touch whatsapp_api/app/utils/constants.py
touch whatsapp_api/app/utils/templates.py
touch whatsapp_api/app/utils/helpers.py
touch whatsapp_api/app/utils/menu_templates.json

# Criar arquivos para testes
touch whatsapp_api/tests/conftest.py

# Criar arquivos para alembic
touch whatsapp_api/alembic/README.md
touch whatsapp_api/alembic/env.py

echo "✅ Estrutura de diretórios e arquivos criada com sucesso em ./whatsapp_api/"
echo "📁 Total de diretórios criados: 15"
echo "📄 Total de arquivos criados: 39"
