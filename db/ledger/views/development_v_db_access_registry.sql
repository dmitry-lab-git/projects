--
-- PostgreSQL database dump
--

\restrict e5fO1INDLbjsoD0IBQcGg5GXrmdQaeJfTJ0w9GMhbgyneizYAPdA1XPawMRhBMw

-- Dumped from database version 18.6 (Ubuntu 18.6-0ubuntu0.26.04.1)
-- Dumped by pg_dump version 18.6 (Ubuntu 18.6-0ubuntu0.26.04.1)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: v_db_access_registry; Type: VIEW; Schema: development; Owner: -
--

CREATE VIEW development.v_db_access_registry AS
 SELECT m.id AS role_uuid,
    r.oid AS role_oid,
    r.rolname AS role_name,
    m.purpose,
    m.env_location,
    r.rolcanlogin AS can_login,
    r.rolsuper AS is_superuser,
    COALESCE(( SELECT array_agg(DISTINCT (g.table_schema)::text ORDER BY ((g.table_schema)::text)) AS array_agg
           FROM information_schema.role_table_grants g
          WHERE ((g.grantee)::name = r.rolname)), '{}'::text[]) AS granted_schemas,
    COALESCE(( SELECT jsonb_object_agg(sub.tbl, sub.privs) AS jsonb_object_agg
           FROM ( SELECT (((g.table_schema)::text || '.'::text) || (g.table_name)::text) AS tbl,
                    array_agg((g.privilege_type)::text ORDER BY (g.privilege_type)::text) AS privs
                   FROM information_schema.role_table_grants g
                  WHERE ((g.grantee)::name = r.rolname)
                  GROUP BY g.table_schema, g.table_name) sub), '{}'::jsonb) AS granted_tables,
    r.rolvaliduntil AS valid_until
   FROM (pg_roles r
     LEFT JOIN development.role_metadata m ON ((m.role_oid = r.oid)))
  WHERE (r.rolname !~~ 'pg_%'::text)
  ORDER BY r.rolname;


--
-- Name: TABLE v_db_access_registry; Type: ACL; Schema: development; Owner: -
--

GRANT SELECT ON TABLE development.v_db_access_registry TO pwa_workers_inspector;


--
-- PostgreSQL database dump complete
--

\unrestrict e5fO1INDLbjsoD0IBQcGg5GXrmdQaeJfTJ0w9GMhbgyneizYAPdA1XPawMRhBMw

