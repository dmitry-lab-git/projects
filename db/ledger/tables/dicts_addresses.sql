--
-- PostgreSQL database dump
--

\restrict ddglxHrItIb4fuFvPKeJ2N3ZcNlrqad4AYbTldWSwUgO9UmNshyuZIt2lxdgZ1g

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
-- Name: addresses; Type: TABLE; Schema: dicts; Owner: -
--

CREATE TABLE dicts.addresses (
    code integer NOT NULL,
    address_name character varying(64),
    address_id character varying(50),
    external_status character varying(50),
    observed_at character varying(50),
    city character varying(50),
    country character varying(50),
    id uuid DEFAULT gen_random_uuid() CONSTRAINT adress_register_id_not_null NOT NULL,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    status_id uuid DEFAULT '1e604e11-8e44-4da3-beb2-369a0113ffdf'::uuid NOT NULL
);


--
-- Name: addresses addresses_code_unique; Type: CONSTRAINT; Schema: dicts; Owner: -
--

ALTER TABLE ONLY dicts.addresses
    ADD CONSTRAINT addresses_code_unique UNIQUE (code);


--
-- Name: addresses addresses_pkey; Type: CONSTRAINT; Schema: dicts; Owner: -
--

ALTER TABLE ONLY dicts.addresses
    ADD CONSTRAINT addresses_pkey PRIMARY KEY (id);


--
-- Name: addresses trg_addresses_autocomplete; Type: TRIGGER; Schema: dicts; Owner: -
--

CREATE TRIGGER trg_addresses_autocomplete BEFORE INSERT ON dicts.addresses FOR EACH ROW EXECUTE FUNCTION dicts.trg_bi_addresses_autocomplete();


--
-- Name: addresses fk_addresses_status; Type: FK CONSTRAINT; Schema: dicts; Owner: -
--

ALTER TABLE ONLY dicts.addresses
    ADD CONSTRAINT fk_addresses_status FOREIGN KEY (status_id) REFERENCES dicts.dict_statuses(id);


--
-- Name: TABLE addresses; Type: ACL; Schema: dicts; Owner: -
--

GRANT SELECT ON TABLE dicts.addresses TO receipt_processor_svc;
GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE dicts.addresses TO reflex_app_user;
GRANT SELECT ON TABLE dicts.addresses TO data_ingress_worker;
GRANT SELECT ON TABLE dicts.addresses TO pwa_workers_inspector;


--
-- PostgreSQL database dump complete
--

\unrestrict ddglxHrItIb4fuFvPKeJ2N3ZcNlrqad4AYbTldWSwUgO9UmNshyuZIt2lxdgZ1g

