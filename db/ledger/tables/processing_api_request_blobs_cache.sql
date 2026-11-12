--
-- PostgreSQL database dump
--

\restrict ix3lXB3V2bRN5aEi5tfXG0pHs7nJzFj4kp1IkyQXywHnaf5ktu0cy8FdeOLcvdK

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
-- Name: api_request_blobs_cache; Type: TABLE; Schema: processing; Owner: -
--

CREATE TABLE processing.api_request_blobs_cache (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    request_id uuid NOT NULL,
    file_data bytea NOT NULL,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL
);


--
-- Name: api_request_blobs_cache api_request_blobs_cache_pkey; Type: CONSTRAINT; Schema: processing; Owner: -
--

ALTER TABLE ONLY processing.api_request_blobs_cache
    ADD CONSTRAINT api_request_blobs_cache_pkey PRIMARY KEY (id);


--
-- Name: idx_blobs_cache_created_at; Type: INDEX; Schema: processing; Owner: -
--

CREATE INDEX idx_blobs_cache_created_at ON processing.api_request_blobs_cache USING btree (created_at);


--
-- Name: idx_blobs_cache_request_id; Type: INDEX; Schema: processing; Owner: -
--

CREATE INDEX idx_blobs_cache_request_id ON processing.api_request_blobs_cache USING btree (request_id);


--
-- Name: TABLE api_request_blobs_cache; Type: ACL; Schema: processing; Owner: -
--

GRANT ALL ON TABLE processing.api_request_blobs_cache TO receipt_processor_svc;
GRANT ALL ON TABLE processing.api_request_blobs_cache TO reflex_app_user;
GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE processing.api_request_blobs_cache TO data_ingress_worker;
GRANT SELECT ON TABLE processing.api_request_blobs_cache TO pwa_workers_inspector;


--
-- PostgreSQL database dump complete
--

\unrestrict ix3lXB3V2bRN5aEi5tfXG0pHs7nJzFj4kp1IkyQXywHnaf5ktu0cy8FdeOLcvdK

