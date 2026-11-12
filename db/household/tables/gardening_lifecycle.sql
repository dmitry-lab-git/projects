--
-- PostgreSQL database dump
--

\restrict vJABTBLbU29McTWVDVXuTLoNaK6QotQNMRxf8Usx8FFO8u2hgUtKbTZpqLjek20

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
-- Name: lifecycle; Type: TABLE; Schema: gardening; Owner: -
--

CREATE TABLE gardening.lifecycle (
    lifecycle_name character varying(50) NOT NULL,
    lifecycle_name_ru character varying(100)
);


--
-- Name: lifecycle lifecycle_pkey; Type: CONSTRAINT; Schema: gardening; Owner: -
--

ALTER TABLE ONLY gardening.lifecycle
    ADD CONSTRAINT lifecycle_pkey PRIMARY KEY (lifecycle_name);


--
-- Name: TABLE lifecycle; Type: ACL; Schema: gardening; Owner: -
--

GRANT SELECT ON TABLE gardening.lifecycle TO reflex_app_user;


--
-- PostgreSQL database dump complete
--

\unrestrict vJABTBLbU29McTWVDVXuTLoNaK6QotQNMRxf8Usx8FFO8u2hgUtKbTZpqLjek20

