-- Criar banco de dados
CREATE DATABASE whatsapp_db;

-- Conectar ao banco de dados
\c whatsapp_db;

-- Extensão para utilizar UUID, se necessário
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Extensão para melhorar performance de pesquisa em texto
CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- Tabela de usuários
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255),
    phone_number VARCHAR(50) UNIQUE NOT NULL,
    contract_number VARCHAR(50),
    terms_accepted BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE
);

CREATE INDEX idx_users_phone_number ON users(phone_number);

-- Tabela de logs de conversa
CREATE TABLE conversation_logs (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    message TEXT NOT NULL,
    direction VARCHAR(10) NOT NULL, -- 'incoming' ou 'outgoing'
    menu_option VARCHAR(50),
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_conversation_logs_user_id ON conversation_logs(user_id);
CREATE INDEX idx_conversation_logs_timestamp ON conversation_logs(timestamp);

-- Tabela de menus
CREATE TABLE menus (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    description VARCHAR(255),
    parent_id INTEGER REFERENCES menus(id) ON DELETE SET NULL,
    content TEXT NOT NULL,
    options JSONB,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE
);

CREATE INDEX idx_menus_name ON menus(name);
CREATE INDEX idx_menus_parent_id ON menus(parent_id);

-- Tabela de estados de menu para usuários
CREATE TABLE menu_states (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE UNIQUE,
    current_menu VARCHAR(100),
    awaiting_response BOOLEAN DEFAULT FALSE,
    form_filled BOOLEAN DEFAULT FALSE,
    context_data JSONB,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_menu_states_user_id ON menu_states(user_id);

-- Tabela para configurações da aplicação
CREATE TABLE settings (
    id SERIAL PRIMARY KEY,
    key VARCHAR(100) NOT NULL UNIQUE,
    value TEXT,
    description VARCHAR(255),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Inserir configurações iniciais
INSERT INTO settings (key, value, description) VALUES
    ('business_hours_start', '8', 'Hora de início do horário comercial (0-23)'),
    ('business_hours_end', '18', 'Hora de término do horário comercial (0-23)'),
    ('outside_hours_message', 'Nosso horário de atendimento é de 8h às 18h, de segunda a sexta-feira. Sua mensagem foi registrada e responderemos assim que possível.', 'Mensagem para fora do horário comercial'),
    ('terms_message', 'Antes de começarmos, precisamos que você aceite nossos termos e condições de uso.', 'Mensagem de termos e condições');

-- Inserir menus iniciais
INSERT INTO menus (name, description, content, options) VALUES
    ('initial', 'Menu inicial após aceitação dos termos', 'Olá! Bem-vindo ao nosso atendimento pelo WhatsApp. Como posso ajudar você hoje?', 
     '{"menu_type": "button", "buttons": {"info": {"id": "info", "title": "Informações Gerais", "next_menu": "info"}, "support": {"id": "support", "title": "Suporte", "next_menu": "support"}, "commercial": {"id": "commercial", "title": "Comercial", "next_menu": "commercial"}}}'),
    
    ('info', 'Menu de informações', 'Informações Gerais\n\nSelecione uma opção para saber mais:', 
     '{"menu_type": "list", "header": "Informações", "footer": "Selecione uma opção", "button_text": "Ver opções", "sections": {"about": {"title": "Sobre Nós", "rows": {"about_company": {"id": "about_company", "title": "Nossa Empresa", "description": "Conheça nossa história e valores"}, "services": {"id": "services", "title": "Nossos Serviços", "description": "Conheça os serviços que oferecemos"}, "location": {"id": "location", "title": "Localização", "description": "Onde nos encontrar"}}}}}');

-- Atualizar parent_id do menu info para referenciar o menu initial
UPDATE menus SET parent_id = (SELECT id FROM menus WHERE name = 'initial') WHERE name = 'info';

-- Criar função para atualizar automaticamente o campo updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Criar triggers para atualização automática do campo updated_at
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_menus_updated_at BEFORE UPDATE ON menus FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_settings_updated_at BEFORE UPDATE ON settings FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_menu_states_updated_at BEFORE UPDATE ON menu_states FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Criar usuário para a aplicação (substitua 'password' por uma senha forte)
CREATE USER whatsapp_user WITH PASSWORD 'password';
GRANT ALL PRIVILEGES ON DATABASE whatsapp_db TO whatsapp_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO whatsapp_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO whatsapp_user;

-- Configurar permissões para o usuário da aplicação
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO whatsapp_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO whatsapp_user;
