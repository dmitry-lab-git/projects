--
-- PostgreSQL database dump
--

\restrict zlRoPKFtA26rngXifwLkcgKSpnInk8y4Ya7qlsV8kczoeXAYqwvfXcAkx2e7gig

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
-- Name: repair_registry; Type: TABLE; Schema: texere; Owner: -
--

CREATE TABLE texere.repair_registry (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    title character varying(255) NOT NULL,
    item_count integer DEFAULT 1 NOT NULL,
    defect_description text NOT NULL,
    work_performed text,
    materials jsonb DEFAULT '{}'::jsonb NOT NULL,
    meta jsonb DEFAULT '{}'::jsonb NOT NULL,
    receipt_date date DEFAULT CURRENT_DATE NOT NULL,
    completion_date date,
    quality_rating integer,
    comments text,
    repair_cost_kzt numeric(12,2),
    macro_category character varying(100),
    category_l2 character varying(100),
    subcategory_l3 character varying(100),
    item_size character varying(50) DEFAULT 'Custom Size'::character varying NOT NULL,
    gender character varying(20),
    size_standard character varying(50),
    origin_country character varying(100),
    repair_status character varying(50) DEFAULT 'Pending'::character varying NOT NULL,
    CONSTRAINT chk_repair_quality_range CHECK (((quality_rating >= 1) AND (quality_rating <= 10)))
);


--
-- Name: repair_registry repair_registry_pkey; Type: CONSTRAINT; Schema: texere; Owner: -
--

ALTER TABLE ONLY texere.repair_registry
    ADD CONSTRAINT repair_registry_pkey PRIMARY KEY (id);


--
-- Name: idx_repair_registry_cat_l2; Type: INDEX; Schema: texere; Owner: -
--

CREATE INDEX idx_repair_registry_cat_l2 ON texere.repair_registry USING btree (category_l2);


--
-- Name: idx_repair_registry_completion_date; Type: INDEX; Schema: texere; Owner: -
--

CREATE INDEX idx_repair_registry_completion_date ON texere.repair_registry USING btree (completion_date);


--
-- Name: idx_repair_registry_gender; Type: INDEX; Schema: texere; Owner: -
--

CREATE INDEX idx_repair_registry_gender ON texere.repair_registry USING btree (gender);


--
-- Name: idx_repair_registry_materials; Type: INDEX; Schema: texere; Owner: -
--

CREATE INDEX idx_repair_registry_materials ON texere.repair_registry USING gin (materials);


--
-- Name: idx_repair_registry_meta; Type: INDEX; Schema: texere; Owner: -
--

CREATE INDEX idx_repair_registry_meta ON texere.repair_registry USING gin (meta);


--
-- Name: idx_repair_registry_receipt_date; Type: INDEX; Schema: texere; Owner: -
--

CREATE INDEX idx_repair_registry_receipt_date ON texere.repair_registry USING btree (receipt_date);


--
-- Name: idx_repair_registry_status; Type: INDEX; Schema: texere; Owner: -
--

CREATE INDEX idx_repair_registry_status ON texere.repair_registry USING btree (repair_status);


--
-- Name: TABLE repair_registry; Type: ACL; Schema: texere; Owner: -
--

GRANT SELECT ON TABLE texere.repair_registry TO reflex_app_user;


--
-- PostgreSQL database dump complete
--

\unrestrict zlRoPKFtA26rngXifwLkcgKSpnInk8y4Ya7qlsV8kczoeXAYqwvfXcAkx2e7gig

