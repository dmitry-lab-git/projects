--
-- PostgreSQL database dump
--

\restrict zpkh5wOxNRnXM9KDO8Pq4ohOBcm0DOHuxs6L6QgPGkHpGxhkuVAskrHUo1mA5i7

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
-- Name: accounts; Type: TABLE; Schema: dicts; Owner: -
--

CREATE TABLE dicts.accounts (
    code integer,
    account_name character varying(50),
    account_id character varying(50),
    entity_id character varying(50),
    id uuid DEFAULT gen_random_uuid() CONSTRAINT account_register_id_not_null NOT NULL,
    opening_date date,
    keywords text,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    status_id uuid NOT NULL,
    currency uuid NOT NULL
);


--
-- Name: accounts accounts_code_unique; Type: CONSTRAINT; Schema: dicts; Owner: -
--

ALTER TABLE ONLY dicts.accounts
    ADD CONSTRAINT accounts_code_unique UNIQUE (code);


--
-- Name: accounts accounts_pkey; Type: CONSTRAINT; Schema: dicts; Owner: -
--

ALTER TABLE ONLY dicts.accounts
    ADD CONSTRAINT accounts_pkey PRIMARY KEY (id);


--
-- Name: idx_accounts_status_id; Type: INDEX; Schema: dicts; Owner: -
--

CREATE INDEX idx_accounts_status_id ON dicts.accounts USING btree (status_id);


--
-- Name: accounts fk_accounts_currency; Type: FK CONSTRAINT; Schema: dicts; Owner: -
--

ALTER TABLE ONLY dicts.accounts
    ADD CONSTRAINT fk_accounts_currency FOREIGN KEY (currency) REFERENCES dicts.dicts_currencies(id);


--
-- Name: accounts fk_accounts_status; Type: FK CONSTRAINT; Schema: dicts; Owner: -
--

ALTER TABLE ONLY dicts.accounts
    ADD CONSTRAINT fk_accounts_status FOREIGN KEY (status_id) REFERENCES dicts.dict_statuses(id);


--
-- Name: TABLE accounts; Type: ACL; Schema: dicts; Owner: -
--

GRANT SELECT ON TABLE dicts.accounts TO receipt_processor_svc;
GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE dicts.accounts TO reflex_app_user;
GRANT SELECT ON TABLE dicts.accounts TO data_ingress_worker;
GRANT SELECT ON TABLE dicts.accounts TO pwa_workers_inspector;


--
-- PostgreSQL database dump complete
--

\unrestrict zpkh5wOxNRnXM9KDO8Pq4ohOBcm0DOHuxs6L6QgPGkHpGxhkuVAskrHUo1mA5i7

