# WhatsApp API Template

Uma API robusta e escalável para gerenciar interações com a API de negócios do WhatsApp, projetada para empresas que desejam automatizar o atendimento ao cliente através do WhatsApp.

## Funcionalidades

- ✅ Webhook para receber mensagens do WhatsApp
- ✅ Sistema de menus interativos (botões, listas)
- ✅ Controle de estado de conversação
- ✅ Suporte a mídias (imagens, documentos, áudio, vídeo)
- ✅ Envio de localização e contatos
- ✅ Templates de mensagens
- ✅ Log de conversas
- ✅ Autenticação e verificação de webhook
- ✅ Controle de horário comercial
- ✅ Banco de dados PostgreSQL
- ✅ Arquitetura modular e escalável

## Pré-requisitos

- Python 3.8+
- PostgreSQL 12+
- Conta Business no WhatsApp
- Acesso à API do WhatsApp Business

## Instalação

1. Clone este repositório:
   ```bash
   git clone https://github.com/seu-usuario/whatsapp-api-template.git
   cd whatsapp-api-template
   ```

2. Crie um ambiente virtual e instale as dependências:
   ```bash
   python -m venv venv
   source venv/bin/activate  # No Windows: venv\\Scripts\\activate
   pip install -r requirements.txt
   ```

3. Configure o arquivo `.env` com suas credenciais:
   ```
   # Copie o arquivo de exemplo
   cp .env.example .env
   # Edite com suas informações
   nano .env
   ```

4. Configure o banco de dados:
   ```bash
   # Crie um banco de dados PostgreSQL
   createdb whatsapp_db
   
   # Execute migrações iniciais
   alembic upgrade head
   ```

5. Inicie a aplicação:
   ```bash
   python main.py
   ```

6. Configure seu webhook no painel do WhatsApp Business:
   - URL: `https://seu-dominio.com/api/v1/webhook/webhook`
   - Token de verificação: o mesmo definido em `.env`

## Estrutura do Projeto

```
whatsapp_api/
├── .env                      # Variáveis de ambiente
├── requirements.txt          # Dependências do projeto
├── README.md                 # Documentação
├── main.py                   # Ponto de entrada da aplicação
├── alembic/                  # Migrações de banco de dados
├── config/                   # Configurações da aplicação
│   ├── settings.py           # Configurações gerais
│   └── database.py           # Configuração do banco de dados
├── app/                      # Código principal da aplicação
│   ├── api/                  # API e rotas
│   │   └── endpoints/        # Endpoints específicos
│   ├── db/                   # Camada de banco de dados
│   │   └── crud/             # Operações CRUD
│   ├── models/               # Modelos de dados
│   ├── schemas/              # Esquemas Pydantic
│   ├── services/             # Serviços da aplicação
│   └── utils/                # Utilitários
└── tests/                    # Testes
```

## Configuração dos Menus

Os menus são definidos no banco de dados. Para adicionar ou modificar menus, você pode:

1. Editar o arquivo `app/utils/menu_templates.json` com suas definições
2. Executar o script de atualização de menus:
   ```bash
   python -m app.scripts.update_menus
   ```

### Estrutura de Menus

Cada menu pode ter diferentes tipos:
- **Text**: Mensagem de texto simples
- **Button**: Mensagem com botões interativos
- **List**: Menu em formato de lista com opções
- **Link**: Mensagem com link clicável

Exemplo de definição de menu:

```json
{
  "name": "initial",
  "description": "Menu inicial",
  "content": "Olá! Como posso ajudar?",
  "options": {
    "menu_type": "button",
    "buttons": {
      "info": {
        "id": "info",
        "title": "Informações",
        "next_menu": "info_menu"
      },
      "support": {
        "id": "support",
        "title": "Suporte",
        "next_menu": "support_menu"
      }
    }
  }
}
```

## Envio de Mensagens

O serviço de WhatsApp (`app/services/whatsapp.py`) fornece métodos para enviar diferentes tipos de mensagens:

```python
# Exemplo de uso
from app.services.whatsapp import whatsapp_service

# Mensagem de texto
await whatsapp_service.send_message(
    phone_number="551234567890",
    message="Olá! Como posso ajudar?"
)

# Mensagem com botões
await whatsapp_service.send_button_message(
    phone_number="551234567890",
    body_text="Escolha uma opção:",
    buttons=[
        {"id": "option1", "title": "Opção 1"},
        {"id": "option2", "title": "Opção 2"}
    ]
)
```

## Personalização

Para adaptar este template para sua empresa:

1. **Menus**: Edite o arquivo `app/utils/menu_templates.json` com seu conteúdo
2. **Templates**: Modifique os templates no WhatsApp Business
3. **Lógica de Negócio**: Implemente sua lógica específica em `app/services/`

## Escalabilidade

Este template foi projetado para ser escalável:

- **Banco de Dados**: Utiliza PostgreSQL com conexões eficientes
- **Processamento Assíncrono**: Utiliza FastAPI e async/await
- **Processamento em Background**: Tarefas longas são processadas em background
- **Cache**: Pode ser facilmente integrado com Redis para cache
