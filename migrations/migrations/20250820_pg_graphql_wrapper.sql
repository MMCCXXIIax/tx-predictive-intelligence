-- Ensure pg_graphql is installed
create extension if not exists pg_graphql;

-- Create/update the GraphQL JSONB wrapper
create or replace function public.graphql(
  operation jsonb
) returns jsonb
language sql
as $$
  select graphql.resolve(
    coalesce(operation->>'query', ''),
    coalesce(operation->'variables', '{}'::jsonb),
    null,
    '{}'::jsonb
  )
$$;
