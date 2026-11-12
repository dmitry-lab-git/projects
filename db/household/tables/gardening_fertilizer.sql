--
-- PostgreSQL database dump
--

\restrict YSWuYtl2swwOEqUuUfjlkCwKJgFjKIga28PUahFbXu94TuxXqhyKpIU8KICgMJ8

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
-- Name: fertilizer; Type: TABLE; Schema: gardening; Owner: -
--

CREATE TABLE gardening.fertilizer (
    fertilizer_id character varying(50) NOT NULL,
    fertilizer_name character varying(255),
    description text,
    type character varying(50)
);


--
-- Name: fertilizer fertilizer_pkey; Type: CONSTRAINT; Schema: gardening; Owner: -
--

ALTER TABLE ONLY gardening.fertilizer
    ADD CONSTRAINT fertilizer_pkey PRIMARY KEY (fertilizer_id);


--
-- Name: TABLE fertilizer; Type: ACL; Schema: gardening; Owner: -
--

GRANT SELECT ON TABLE gardening.fertilizer TO reflex_app_user;


--
-- PostgreSQL database dump complete
--

\unrestrict YSWuYtl2swwOEqUuUfjlkCwKJgFjKIga28PUahFbXu94TuxXqhyKpIU8KICgMJ8

