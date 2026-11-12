--
-- PostgreSQL database dump
--

\restrict suSMu9OtLg1lT9WIlDMqHQhPNUkkBfSU4lDk4eTEf6QApg5DoaL3G1CO1uD7MU2

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
-- Name: seed_pack; Type: TABLE; Schema: gardening; Owner: -
--

CREATE TABLE gardening.seed_pack (
    seed_pack_id character varying(50) NOT NULL,
    seed_pack_name character varying(255),
    flower_latin_name character varying(255),
    seed_quantity character varying(50),
    produced_by character varying(255),
    best_before_date character varying(50),
    pack_date character varying(50),
    price_kzt numeric
);


--
-- Name: seed_pack seed_pack_pkey; Type: CONSTRAINT; Schema: gardening; Owner: -
--

ALTER TABLE ONLY gardening.seed_pack
    ADD CONSTRAINT seed_pack_pkey PRIMARY KEY (seed_pack_id);


--
-- Name: TABLE seed_pack; Type: ACL; Schema: gardening; Owner: -
--

GRANT SELECT ON TABLE gardening.seed_pack TO reflex_app_user;


--
-- PostgreSQL database dump complete
--

\unrestrict suSMu9OtLg1lT9WIlDMqHQhPNUkkBfSU4lDk4eTEf6QApg5DoaL3G1CO1uD7MU2

