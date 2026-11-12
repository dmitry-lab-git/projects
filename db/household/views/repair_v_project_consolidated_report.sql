--
-- PostgreSQL database dump
--

\restrict fB53Lji8eZC7nf5mukteGONeeAcurcF7Iq5iYXPnABsdsBTozW4UCtxRzdJWB15

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
-- Name: v_project_consolidated_report; Type: VIEW; Schema: repair; Owner: -
--

CREATE VIEW repair.v_project_consolidated_report AS
 SELECT count(*) AS total_projects,
    count(*) FILTER (WHERE ((status)::text = 'completed'::text)) AS completed_projects,
    count(*) FILTER (WHERE ((status)::text = 'planning'::text)) AS planning_projects,
    count(*) FILTER (WHERE (((meta ->> 'outsource'::text))::boolean = true)) AS outsourced_count,
    round((((count(*) FILTER (WHERE (((meta ->> 'outsource'::text))::boolean = true)))::numeric / (count(*))::numeric) * (100)::numeric), 1) AS outsource_share_percent,
    count(*) FILTER (WHERE ((((meta ->> 'disposed'::text))::boolean = true) OR ((meta ->> 'disposal_status'::text) = 'disposed'::text))) AS disposed_count
   FROM repair.projects;


--
-- Name: TABLE v_project_consolidated_report; Type: ACL; Schema: repair; Owner: -
--

GRANT SELECT ON TABLE repair.v_project_consolidated_report TO reflex_app_user;


--
-- PostgreSQL database dump complete
--

\unrestrict fB53Lji8eZC7nf5mukteGONeeAcurcF7Iq5iYXPnABsdsBTozW4UCtxRzdJWB15

