--
-- PostgreSQL database dump
--

\restrict 0sdojSZUymtDNleETuEPGcVhlcelAAW7OeMAsnHiW7brdd2I6rDbAkHqMRf6vMJ

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

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: version_updates; Type: TABLE; Schema: development; Owner: -
--

CREATE TABLE development.version_updates (
    code integer DEFAULT nextval('development.version_updates_code_seq'::regclass) NOT NULL,
    update_version_name character varying(50),
    update_version_id character varying(50),
    version_id character varying(50),
    registration_date date NOT NULL,
    description text,
    affected_objects text,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT version_updates_code_positive CHECK ((code > 0))
);


--
-- Name: COLUMN version_updates.update_version_id; Type: COMMENT; Schema: development; Owner: -
--

COMMENT ON COLUMN development.version_updates.update_version_id IS 'Идентификатор конкретного обновления (напр. UVR-002)';


--
-- Name: COLUMN version_updates.version_id; Type: COMMENT; Schema: development; Owner: -
--

COMMENT ON COLUMN development.version_updates.version_id IS 'Ссылка на основную версию системы (напр. VER-003)';


--
-- Name: version_updates version_updates_code_pkey; Type: CONSTRAINT; Schema: development; Owner: -
--

ALTER TABLE ONLY development.version_updates
    ADD CONSTRAINT version_updates_code_pkey PRIMARY KEY (code);


--
-- Name: version_updates version_updates_code_unique; Type: CONSTRAINT; Schema: development; Owner: -
--

ALTER TABLE ONLY development.version_updates
    ADD CONSTRAINT version_updates_code_unique UNIQUE (code);


--
-- Name: version_updates trg_version_updates_insert; Type: TRIGGER; Schema: development; Owner: -
--

CREATE TRIGGER trg_version_updates_insert BEFORE INSERT ON development.version_updates FOR EACH ROW EXECUTE FUNCTION development.fn_auto_generate_uvr();


--
-- Name: TABLE version_updates; Type: ACL; Schema: development; Owner: -
--

GRANT SELECT ON TABLE development.version_updates TO pwa_workers_inspector;


--
-- PostgreSQL database dump complete
--

\unrestrict 0sdojSZUymtDNleETuEPGcVhlcelAAW7OeMAsnHiW7brdd2I6rDbAkHqMRf6vMJ

