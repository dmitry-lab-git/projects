--
-- PostgreSQL database dump
--

\restrict whrw8jEGRbELPvbdkGyC4c5k6Nhgf6gyKyyXNaqkamGeeg1DIU1MP4NTxG7SB3a

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
-- Name: fabric_treatment_protocols; Type: TABLE; Schema: texere; Owner: -
--

CREATE TABLE texere.fabric_treatment_protocols (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    fabric_type character varying(150) NOT NULL,
    density_gsm integer,
    pre_soaking_required boolean DEFAULT true,
    soaking_details text,
    washing_temperature_c integer DEFAULT 30,
    washing_duration_minutes integer,
    spin_rpm integer DEFAULT 0,
    detergents_meta jsonb DEFAULT '{}'::jsonb,
    drying_method text,
    ironing_modes text,
    critical_issues text,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    CONSTRAINT chk_spin_rpm CHECK ((spin_rpm >= 0)),
    CONSTRAINT chk_washing_temp CHECK (((washing_temperature_c >= 0) AND (washing_temperature_c <= 95)))
);


--
-- Name: TABLE fabric_treatment_protocols; Type: COMMENT; Schema: texere; Owner: -
--

COMMENT ON TABLE texere.fabric_treatment_protocols IS 'База знаний и протоколы технологических процессов ВТО, замачивания и стирки отрезов для предотвращения дефектов (заломов, потери цвета).';


--
-- Name: fabric_treatment_protocols pk_fabric_treatment_protocols; Type: CONSTRAINT; Schema: texere; Owner: -
--

ALTER TABLE ONLY texere.fabric_treatment_protocols
    ADD CONSTRAINT pk_fabric_treatment_protocols PRIMARY KEY (id);


--
-- Name: idx_treatment_protocols_fabric_type; Type: INDEX; Schema: texere; Owner: -
--

CREATE INDEX idx_treatment_protocols_fabric_type ON texere.fabric_treatment_protocols USING btree (fabric_type);


--
-- Name: TABLE fabric_treatment_protocols; Type: ACL; Schema: texere; Owner: -
--

GRANT SELECT ON TABLE texere.fabric_treatment_protocols TO reflex_app_user;


--
-- PostgreSQL database dump complete
--

\unrestrict whrw8jEGRbELPvbdkGyC4c5k6Nhgf6gyKyyXNaqkamGeeg1DIU1MP4NTxG7SB3a

