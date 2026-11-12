--
-- PostgreSQL database dump
--

\restrict N1dPA0fsOYvvv9zBFXKleYZ49nMMybOZwwU8gHsxsbG6BhpeK3hmb6RjCDEj9Ph

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
-- Name: state; Type: TABLE; Schema: gardening; Owner: -
--

CREATE TABLE gardening.state (
    state character varying(50) NOT NULL
);


--
-- Name: state state_pkey; Type: CONSTRAINT; Schema: gardening; Owner: -
--

ALTER TABLE ONLY gardening.state
    ADD CONSTRAINT state_pkey PRIMARY KEY (state);


--
-- Name: TABLE state; Type: ACL; Schema: gardening; Owner: -
--

GRANT SELECT ON TABLE gardening.state TO reflex_app_user;


--
-- PostgreSQL database dump complete
--

\unrestrict N1dPA0fsOYvvv9zBFXKleYZ49nMMybOZwwU8gHsxsbG6BhpeK3hmb6RjCDEj9Ph

