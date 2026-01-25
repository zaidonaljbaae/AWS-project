CREATE SCHEMA IF NOT EXISTS fiat;

CREATE TABLE IF NOT EXISTS fiat.nota_servico (
  id UUID PRIMARY KEY,
  numero BIGINT,
  descricao TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW()
);
