--
-- PostgreSQL database dump
--

\restrict MrXLR2Rt7sl460VJ3GlcvmQGrshHdAZt66Htst9m1d42iUrbw0b4bAI7yTcSprd

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
-- Name: time_tracker; Type: TABLE; Schema: infrastructure; Owner: -
--

CREATE TABLE infrastructure.time_tracker (
    id uuid NOT NULL,
    task_name character varying(255) NOT NULL,
    start_time timestamp with time zone NOT NULL,
    end_time timestamp with time zone,
    comment text,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    is_deleted boolean DEFAULT false NOT NULL
);


--
-- Name: time_tracker time_tracker_pkey; Type: CONSTRAINT; Schema: infrastructure; Owner: -
--

ALTER TABLE ONLY infrastructure.time_tracker
    ADD CONSTRAINT time_tracker_pkey PRIMARY KEY (id);


--
-- Name: idx_time_tracker_updated_at; Type: INDEX; Schema: infrastructure; Owner: -
--

CREATE INDEX idx_time_tracker_updated_at ON infrastructure.time_tracker USING btree (updated_at);


--
-- Name: TABLE time_tracker; Type: ACL; Schema: infrastructure; Owner: -
--

GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE infrastructure.time_tracker TO reflex_app_user;


--
-- PostgreSQL database dump complete
--

\unrestrict MrXLR2Rt7sl460VJ3GlcvmQGrshHdAZt66Htst9m1d42iUrbw0b4bAI7yTcSprd

