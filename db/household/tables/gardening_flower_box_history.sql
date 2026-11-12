--
-- PostgreSQL database dump
--

\restrict JYhvVYdLPdIiTndZG245hV1AJIPbcbeLPsjwbm5bw0DTmKPkqZIxNNMxanI3rBI

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
-- Name: flower_box_history; Type: TABLE; Schema: gardening; Owner: -
--

CREATE TABLE gardening.flower_box_history (
    code integer NOT NULL,
    flower_id character varying(50) NOT NULL,
    box_id character varying(50) NOT NULL,
    created_at date
);


--
-- Name: flower_box_history flower_box_history_pkey; Type: CONSTRAINT; Schema: gardening; Owner: -
--

ALTER TABLE ONLY gardening.flower_box_history
    ADD CONSTRAINT flower_box_history_pkey PRIMARY KEY (code);


--
-- Name: flower_box_history flower_box_history_box_id_fkey; Type: FK CONSTRAINT; Schema: gardening; Owner: -
--

ALTER TABLE ONLY gardening.flower_box_history
    ADD CONSTRAINT flower_box_history_box_id_fkey FOREIGN KEY (box_id) REFERENCES gardening.box_register(box_id);


--
-- Name: TABLE flower_box_history; Type: ACL; Schema: gardening; Owner: -
--

GRANT SELECT ON TABLE gardening.flower_box_history TO reflex_app_user;


--
-- PostgreSQL database dump complete
--

\unrestrict JYhvVYdLPdIiTndZG245hV1AJIPbcbeLPsjwbm5bw0DTmKPkqZIxNNMxanI3rBI

