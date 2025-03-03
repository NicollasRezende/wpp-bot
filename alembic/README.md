# Migrações de Banco de Dados com Alembic

Este diretório contém scripts de migração para o banco de dados usando [Alembic](https://alembic.sqlalchemy.org/).

## Comandos Básicos

### Inicialização

Se você estiver configurando o projeto pela primeira vez, Alembic já estará inicializado. Caso contrário, você pode inicializá-lo com:

```bash
alembic init alembic
```

### Criação de Migração

Para criar uma nova migração:

```bash
alembic revision --autogenerate -m "descrição da alteração"
```

Este comando irá:
1. Comparar o estado atual do banco de dados com os modelos SQLAlchemy
2. Gerar um script de migração com as diferenças
3. Salvar o script no diretório `alembic/versions/`

### Aplicar Migrações

Para aplicar todas as migrações pendentes:

```bash
alembic upgrade head
```

Para aplicar até uma migração específica:

```bash
alembic upgrade <revision_id>
```

### Reverter Migrações

Para reverter a última migração:

```bash
alembic downgrade -1
```

Para reverter até uma migração específica:

```bash
alembic downgrade <revision_id>
```

Para reverter todas as migrações:

```bash
alembic downgrade base
```

### Verificar Status

Para ver o status atual das migrações:

```bash
alembic current
```

Para ver o histórico de migrações:

```bash
alembic history
```

## Configuração

A configuração do Alembic está no arquivo `alembic.ini` e o script de ambiente está em `alembic/env.py`.

## Boas Práticas

1. **Sempre teste migrações em ambiente de desenvolvimento** antes de aplicá-las em produção
2. **Nunca edite manualmente um arquivo de migração** depois de aplicado em qualquer ambiente
3. **Sempre faça backup do banco de dados** antes de aplicar migrações em produção
4. **Mantenha uma migração por alteração lógica** em vez de acumular muitas alterações em uma única migração
5. **Inclua código para migração de dados** quando necessário, não apenas alterações de esquema

## Solução de Problemas

Se encontrar problemas com migrações:

1. Verifique se o banco de dados está acessível
2. Garanta que as permissões do usuário do banco de dados são adequadas
3. Compare o esquema atual do banco com o esperado
4. Verifique a tabela `alembic_version` no banco de dados

## Recursos Adicionais

- [Documentação oficial do Alembic](https://alembic.sqlalchemy.org/en/latest/)
- [Tutorial sobre Alembic e FastAPI](https://fastapi.tiangolo.com/advanced/async-sql-databases/#migrations-with-alembic)