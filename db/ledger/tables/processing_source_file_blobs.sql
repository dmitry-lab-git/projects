--
-- PostgreSQL database dump
--

\restrict 2ogb3Exb64iz2GofhQUOuBxlpuI9gceiqgkVJw0uQtBf44wyKvIp3DrBjO3BGnC

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
-- Name: source_file_blobs; Type: TABLE; Schema: processing; Owner: -
--

CREATE TABLE processing.source_file_blobs (
    source_file_id uuid NOT NULL,
    compressed_data bytea NOT NULL,
    mime_type character varying(50) DEFAULT 'image/jpeg'::character varying NOT NULL,
    original_size bigint NOT NULL,
    compressed_size bigint NOT NULL,
    compression_ratio numeric(5,2),
    is_protected boolean DEFAULT false NOT NULL,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL
);


--
-- Name: source_file_blobs source_file_blobs_pkey; Type: CONSTRAINT; Schema: processing; Owner: -
--

ALTER TABLE ONLY processing.source_file_blobs
    ADD CONSTRAINT source_file_blobs_pkey PRIMARY KEY (source_file_id);


--
-- Name: source_file_blobs fk_blobs_source_file; Type: FK CONSTRAINT; Schema: processing; Owner: -
--

ALTER TABLE ONLY processing.source_file_blobs
    ADD CONSTRAINT fk_blobs_source_file FOREIGN KEY (source_file_id) REFERENCES processing.source_files(id) ON DELETE RESTRICT;


--
-- Name: TABLE source_file_blobs; Type: ACL; Schema: processing; Owner: -
--

GRANT ALL ON TABLE processing.source_file_blobs TO reflex_app_user;
GRANT ALL ON TABLE processing.source_file_blobs TO receipt_processor_svc;
GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE processing.source_file_blobs TO data_ingress_worker;
GRANT SELECT ON TABLE processing.source_file_blobs TO pwa_workers_inspector;


--
-- PostgreSQL database dump complete
--

\unrestrict 2ogb3Exb64iz2GofhQUOuBxlpuI9gceiqgkVJw0uQtBf44wyKvIp3DrBjO3BGnC

