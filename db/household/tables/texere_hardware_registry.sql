--
-- PostgreSQL database dump
--

\restrict 5GI3q57zudtt2Gm91IfXbqUd9K679GhGsWQJgzkeSpaEFLmpd6JsDDhbiv0gmP8

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
-- Name: hardware_registry; Type: TABLE; Schema: texere; Owner: -
--

CREATE TABLE texere.hardware_registry (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    parent_id uuid,
    product_id uuid NOT NULL,
    hardware_list jsonb DEFAULT '[]'::jsonb NOT NULL,
    has_custom_work boolean DEFAULT false NOT NULL,
    comments text,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL
);


--
-- Name: hardware_registry hardware_registry_pkey; Type: CONSTRAINT; Schema: texere; Owner: -
--

ALTER TABLE ONLY texere.hardware_registry
    ADD CONSTRAINT hardware_registry_pkey PRIMARY KEY (id);


--
-- Name: idx_hardware_registry_list; Type: INDEX; Schema: texere; Owner: -
--

CREATE INDEX idx_hardware_registry_list ON texere.hardware_registry USING gin (hardware_list);


--
-- Name: idx_hardware_registry_parent_id; Type: INDEX; Schema: texere; Owner: -
--

CREATE INDEX idx_hardware_registry_parent_id ON texere.hardware_registry USING btree (parent_id);


--
-- Name: idx_hardware_registry_product_id; Type: INDEX; Schema: texere; Owner: -
--

CREATE INDEX idx_hardware_registry_product_id ON texere.hardware_registry USING btree (product_id);


--
-- Name: TABLE hardware_registry; Type: ACL; Schema: texere; Owner: -
--

GRANT SELECT ON TABLE texere.hardware_registry TO reflex_app_user;


--
-- PostgreSQL database dump complete
--

\unrestrict 5GI3q57zudtt2Gm91IfXbqUd9K679GhGsWQJgzkeSpaEFLmpd6JsDDhbiv0gmP8

