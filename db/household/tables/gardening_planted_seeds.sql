--
-- PostgreSQL database dump
--

\restrict jdb84EgaheT2LfcSpXcVvRGvCb1quwJkJpW2vfabg9vF9cSwek0XUJgDNJIyDqC

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
-- Name: planted_seeds; Type: TABLE; Schema: gardening; Owner: -
--

CREATE TABLE gardening.planted_seeds (
    code integer NOT NULL,
    seed_name character varying(255),
    seed_planting_id character varying(50) NOT NULL,
    state character varying(50),
    planted_at date,
    seed_quantity integer,
    seed_pack character varying(50),
    box_id character varying(50)
);


--
-- Name: planted_seeds planted_seeds_pkey; Type: CONSTRAINT; Schema: gardening; Owner: -
--

ALTER TABLE ONLY gardening.planted_seeds
    ADD CONSTRAINT planted_seeds_pkey PRIMARY KEY (code);


--
-- Name: planted_seeds planted_seeds_seed_planting_id_key; Type: CONSTRAINT; Schema: gardening; Owner: -
--

ALTER TABLE ONLY gardening.planted_seeds
    ADD CONSTRAINT planted_seeds_seed_planting_id_key UNIQUE (seed_planting_id);


--
-- Name: planted_seeds planted_seeds_box_id_fkey; Type: FK CONSTRAINT; Schema: gardening; Owner: -
--

ALTER TABLE ONLY gardening.planted_seeds
    ADD CONSTRAINT planted_seeds_box_id_fkey FOREIGN KEY (box_id) REFERENCES gardening.box_register(box_id);


--
-- Name: planted_seeds planted_seeds_seed_pack_fkey; Type: FK CONSTRAINT; Schema: gardening; Owner: -
--

ALTER TABLE ONLY gardening.planted_seeds
    ADD CONSTRAINT planted_seeds_seed_pack_fkey FOREIGN KEY (seed_pack) REFERENCES gardening.seed_pack(seed_pack_id);


--
-- Name: planted_seeds planted_seeds_state_fkey; Type: FK CONSTRAINT; Schema: gardening; Owner: -
--

ALTER TABLE ONLY gardening.planted_seeds
    ADD CONSTRAINT planted_seeds_state_fkey FOREIGN KEY (state) REFERENCES gardening.state(state);


--
-- Name: TABLE planted_seeds; Type: ACL; Schema: gardening; Owner: -
--

GRANT SELECT ON TABLE gardening.planted_seeds TO reflex_app_user;


--
-- PostgreSQL database dump complete
--

\unrestrict jdb84EgaheT2LfcSpXcVvRGvCb1quwJkJpW2vfabg9vF9cSwek0XUJgDNJIyDqC

