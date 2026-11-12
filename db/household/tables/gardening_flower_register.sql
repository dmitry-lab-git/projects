--
-- PostgreSQL database dump
--

\restrict 4q2mFgiBgGvKbFwLGEtxSS53WpcALp94Ov8DR5RkVIKizifVvqyfacsdwHq7mGN

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
-- Name: flower_register; Type: TABLE; Schema: gardening; Owner: -
--

CREATE TABLE gardening.flower_register (
    code integer NOT NULL,
    flower_id character varying(50) NOT NULL,
    flower_name_ru character varying(255) NOT NULL,
    flower_name_en character varying(255)
);


--
-- Name: flower_register flower_register_flower_id_key; Type: CONSTRAINT; Schema: gardening; Owner: -
--

ALTER TABLE ONLY gardening.flower_register
    ADD CONSTRAINT flower_register_flower_id_key UNIQUE (flower_id);


--
-- Name: flower_register flower_register_pkey; Type: CONSTRAINT; Schema: gardening; Owner: -
--

ALTER TABLE ONLY gardening.flower_register
    ADD CONSTRAINT flower_register_pkey PRIMARY KEY (code);


--
-- Name: TABLE flower_register; Type: ACL; Schema: gardening; Owner: -
--

GRANT SELECT ON TABLE gardening.flower_register TO reflex_app_user;


--
-- PostgreSQL database dump complete
--

\unrestrict 4q2mFgiBgGvKbFwLGEtxSS53WpcALp94Ov8DR5RkVIKizifVvqyfacsdwHq7mGN

