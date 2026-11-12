--
-- PostgreSQL database dump
--

\restrict 2XQDQrFq84pTuMwS5M9vvw1BJDousfSQ1VukhstQaaYw55kLdWR6oZqh3anALsF

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
-- Name: notes; Type: TABLE; Schema: gardening; Owner: -
--

CREATE TABLE gardening.notes (
    code integer NOT NULL,
    note_name character varying(255) NOT NULL,
    note_id character varying(50) NOT NULL,
    entity_id character varying(50),
    description text NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: notes_code_seq; Type: SEQUENCE; Schema: gardening; Owner: -
--

ALTER TABLE gardening.notes ALTER COLUMN code ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME gardening.notes_code_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: notes notes_note_id_key; Type: CONSTRAINT; Schema: gardening; Owner: -
--

ALTER TABLE ONLY gardening.notes
    ADD CONSTRAINT notes_note_id_key UNIQUE (note_id);


--
-- Name: notes notes_pkey; Type: CONSTRAINT; Schema: gardening; Owner: -
--

ALTER TABLE ONLY gardening.notes
    ADD CONSTRAINT notes_pkey PRIMARY KEY (code);


--
-- Name: TABLE notes; Type: ACL; Schema: gardening; Owner: -
--

GRANT SELECT ON TABLE gardening.notes TO reflex_app_user;


--
-- PostgreSQL database dump complete
--

\unrestrict 2XQDQrFq84pTuMwS5M9vvw1BJDousfSQ1VukhstQaaYw55kLdWR6oZqh3anALsF

