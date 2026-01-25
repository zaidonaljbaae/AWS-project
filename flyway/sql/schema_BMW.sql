CREATE SCHEMA IF NOT EXISTS bmw;

CREATE TABLE IF NOT EXISTS bmw.nota_servico (
  id UUID PRIMARY KEY,
  numero BIGINT,
  descricao TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW()
);
