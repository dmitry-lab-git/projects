--
-- PostgreSQL database dump
--

\restrict PN48MKKfzPG1nQFqgyxvt8PPnv74gnXbYayPZbckWwd4c5sgMsz6XJlpBp3meDr

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
-- Name: events_register; Type: TABLE; Schema: gardening; Owner: -
--

CREATE TABLE gardening.events_register (
    code integer NOT NULL,
    event_id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    object_id character varying(50) NOT NULL,
    event_with_object character varying(50) NOT NULL,
    event_type character varying(50) NOT NULL,
    event_time date NOT NULL,
    created_at timestamp with time zone DEFAULT now() CONSTRAINT events_register_recorded_at_not_null NOT NULL,
    meta jsonb
);


--
-- Name: events_register_code_seq; Type: SEQUENCE; Schema: gardening; Owner: -
--

ALTER TABLE gardening.events_register ALTER COLUMN code ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME gardening.events_register_code_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: events_register events_register_event_id_key; Type: CONSTRAINT; Schema: gardening; Owner: -
--

ALTER TABLE ONLY gardening.events_register
    ADD CONSTRAINT events_register_event_id_key UNIQUE (event_id);


--
-- Name: events_register events_register_pkey; Type: CONSTRAINT; Schema: gardening; Owner: -
--

ALTER TABLE ONLY gardening.events_register
    ADD CONSTRAINT events_register_pkey PRIMARY KEY (code);


--
-- Name: events_register events_register_event_type_fkey; Type: FK CONSTRAINT; Schema: gardening; Owner: -
--

ALTER TABLE ONLY gardening.events_register
    ADD CONSTRAINT events_register_event_type_fkey FOREIGN KEY (event_type) REFERENCES gardening.event_type(event_type);


--
-- Name: TABLE events_register; Type: ACL; Schema: gardening; Owner: -
--

GRANT SELECT ON TABLE gardening.events_register TO reflex_app_user;


--
-- PostgreSQL database dump complete
--

\unrestrict PN48MKKfzPG1nQFqgyxvt8PPnv74gnXbYayPZbckWwd4c5sgMsz6XJlpBp3meDr

