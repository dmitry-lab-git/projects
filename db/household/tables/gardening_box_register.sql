--
-- PostgreSQL database dump
--

\restrict HJc5JUJwQZLnAIBLu58gUXjEhCKGw6HHPaWAjmuehIoxcKHL5LqWFJj2BPAu0Fv

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
-- Name: box_register; Type: TABLE; Schema: gardening; Owner: -
--

CREATE TABLE gardening.box_register (
    box_id character varying(50) NOT NULL,
    box_name character varying(255),
    box_type character varying(50)
);


--
-- Name: box_register box_register_pkey; Type: CONSTRAINT; Schema: gardening; Owner: -
--

ALTER TABLE ONLY gardening.box_register
    ADD CONSTRAINT box_register_pkey PRIMARY KEY (box_id);


--
-- Name: TABLE box_register; Type: ACL; Schema: gardening; Owner: -
--

GRANT SELECT ON TABLE gardening.box_register TO reflex_app_user;


--
-- PostgreSQL database dump complete
--

\unrestrict HJc5JUJwQZLnAIBLu58gUXjEhCKGw6HHPaWAjmuehIoxcKHL5LqWFJj2BPAu0Fv

