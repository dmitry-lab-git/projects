--
-- PostgreSQL database dump
--

\restrict c8lnUAtVgOkkjLeyL3bF8mK9hXuI4qHswKszFK3gLdbrmh5z5UE4q52gkmYe2Xh

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
-- Name: event_type; Type: TABLE; Schema: gardening; Owner: -
--

CREATE TABLE gardening.event_type (
    event_type character varying(50) NOT NULL,
    event_type_ru character varying(100)
);


--
-- Name: event_type event_type_pkey; Type: CONSTRAINT; Schema: gardening; Owner: -
--

ALTER TABLE ONLY gardening.event_type
    ADD CONSTRAINT event_type_pkey PRIMARY KEY (event_type);


--
-- Name: TABLE event_type; Type: ACL; Schema: gardening; Owner: -
--

GRANT SELECT ON TABLE gardening.event_type TO reflex_app_user;


--
-- PostgreSQL database dump complete
--

\unrestrict c8lnUAtVgOkkjLeyL3bF8mK9hXuI4qHswKszFK3gLdbrmh5z5UE4q52gkmYe2Xh

