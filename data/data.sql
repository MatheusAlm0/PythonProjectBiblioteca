-- Cria banco e tabela de usuários com inserts automáticos
-- Para PostgreSQL
CREATE DATABASE IF NOT EXISTS biblioteca;

CREATE TABLE IF NOT EXISTS users (
  id SERIAL PRIMARY KEY,
  username VARCHAR(150) NOT NULL UNIQUE,
  password VARCHAR(255) NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Inserts automáticos (senhas em texto simples para simplicidade)
INSERT INTO users (username, password) VALUES ('teste', 'senha123') ON CONFLICT (username) DO NOTHING;
INSERT INTO users (username, password) VALUES ('meuUsuario', 'senha123') ON CONFLICT (username) DO NOTHING;
