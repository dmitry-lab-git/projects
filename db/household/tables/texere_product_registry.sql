--
-- PostgreSQL database dump
--

\restrict etHOOkHuKVXoIiIrubeiZ9Dwqqvkkiu740u6Y78n2c0jVVPyoZjvAT11uBpDSrh

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
-- Name: product_registry; Type: TABLE; Schema: texere; Owner: -
--

CREATE TABLE texere.product_registry (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    title character varying(255) NOT NULL,
    item_count integer DEFAULT 1 CONSTRAINT product_registry_quantity_not_null NOT NULL,
    materials jsonb DEFAULT '{}'::jsonb NOT NULL,
    meta jsonb DEFAULT '{}'::jsonb NOT NULL,
    completion_date date,
    quality_rating integer,
    comments text,
    project_cost_kzt numeric(12,2),
    macro_category character varying(100),
    category_l2 character varying(100),
    subcategory_l3 character varying(100),
    item_size character varying(50) DEFAULT 'Custom Size'::character varying NOT NULL,
    gender character varying(20),
    size_standard character varying(50),
    batches_count integer NOT NULL,
    production_type character varying(50) NOT NULL,
    using_status character varying(50),
    fabric_consumption numeric(10,2),
    total_fabric_consumption numeric(10,3) DEFAULT 0.000 NOT NULL,
    CONSTRAINT chk_quality_range CHECK (((quality_rating >= 1) AND (quality_rating <= 10)))
);


--
-- Name: COLUMN product_registry.fabric_consumption; Type: COMMENT; Schema: texere; Owner: -
--

COMMENT ON COLUMN texere.product_registry.fabric_consumption IS 'Расход ткани (например, в метрах или килограммах)';


--
-- Name: COLUMN product_registry.total_fabric_consumption; Type: COMMENT; Schema: texere; Owner: -
--

COMMENT ON COLUMN texere.product_registry.total_fabric_consumption IS 'Автоматически рассчитанный суммарный расход ткани (в метрах) на основе поля materials';


--
-- Name: product_registry product_registry_pkey; Type: CONSTRAINT; Schema: texere; Owner: -
--

ALTER TABLE ONLY texere.product_registry
    ADD CONSTRAINT product_registry_pkey PRIMARY KEY (id);


--
-- Name: idx_product_registry_cat_l2; Type: INDEX; Schema: texere; Owner: -
--

CREATE INDEX idx_product_registry_cat_l2 ON texere.product_registry USING btree (category_l2);


--
-- Name: idx_product_registry_completion_date; Type: INDEX; Schema: texere; Owner: -
--

CREATE INDEX idx_product_registry_completion_date ON texere.product_registry USING btree (completion_date);


--
-- Name: idx_product_registry_gender; Type: INDEX; Schema: texere; Owner: -
--

CREATE INDEX idx_product_registry_gender ON texere.product_registry USING btree (gender);


--
-- Name: idx_product_registry_item_size; Type: INDEX; Schema: texere; Owner: -
--

CREATE INDEX idx_product_registry_item_size ON texere.product_registry USING btree (item_size);


--
-- Name: idx_product_registry_item_size_standard; Type: INDEX; Schema: texere; Owner: -
--

CREATE INDEX idx_product_registry_item_size_standard ON texere.product_registry USING btree (size_standard);


--
-- Name: idx_product_registry_macro_cat; Type: INDEX; Schema: texere; Owner: -
--

CREATE INDEX idx_product_registry_macro_cat ON texere.product_registry USING btree (macro_category);


--
-- Name: idx_product_registry_materials; Type: INDEX; Schema: texere; Owner: -
--

CREATE INDEX idx_product_registry_materials ON texere.product_registry USING gin (materials);


--
-- Name: idx_product_registry_meta; Type: INDEX; Schema: texere; Owner: -
--

CREATE INDEX idx_product_registry_meta ON texere.product_registry USING gin (meta);


--
-- Name: idx_product_registry_production_type; Type: INDEX; Schema: texere; Owner: -
--

CREATE INDEX idx_product_registry_production_type ON texere.product_registry USING btree (production_type);


--
-- Name: idx_product_registry_project_cost; Type: INDEX; Schema: texere; Owner: -
--

CREATE INDEX idx_product_registry_project_cost ON texere.product_registry USING btree (project_cost_kzt);


--
-- Name: idx_product_registry_total_fabric_consumption; Type: INDEX; Schema: texere; Owner: -
--

CREATE INDEX idx_product_registry_total_fabric_consumption ON texere.product_registry USING btree (total_fabric_consumption);


--
-- Name: product_registry trg_calculate_total_fabric; Type: TRIGGER; Schema: texere; Owner: -
--

CREATE TRIGGER trg_calculate_total_fabric BEFORE INSERT OR UPDATE ON texere.product_registry FOR EACH ROW EXECUTE FUNCTION texere.fn_calculate_total_fabric();


--
-- Name: TABLE product_registry; Type: ACL; Schema: texere; Owner: -
--

GRANT SELECT ON TABLE texere.product_registry TO reflex_app_user;


--
-- PostgreSQL database dump complete
--

\unrestrict etHOOkHuKVXoIiIrubeiZ9Dwqqvkkiu740u6Y78n2c0jVVPyoZjvAT11uBpDSrh

