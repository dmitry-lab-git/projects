--
-- PostgreSQL database dump
--

\restrict d7EbfH6dygvKWptOpbxsEKwYZWwMmGbGLuKZZ9DZxVsZeS1M7l9n5wFo79lzRr0

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
-- Name: role_metadata; Type: TABLE; Schema: development; Owner: -
--

CREATE TABLE development.role_metadata (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    role_oid oid NOT NULL,
    role_name character varying(100) NOT NULL,
    purpose text,
    env_location text,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL
);


--
-- Name: role_metadata role_metadata_pkey; Type: CONSTRAINT; Schema: development; Owner: -
--

ALTER TABLE ONLY development.role_metadata
    ADD CONSTRAINT role_metadata_pkey PRIMARY KEY (id);


--
-- Name: role_metadata role_metadata_role_name_key; Type: CONSTRAINT; Schema: development; Owner: -
--

ALTER TABLE ONLY development.role_metadata
    ADD CONSTRAINT role_metadata_role_name_key UNIQUE (role_name);


--
-- Name: role_metadata role_metadata_role_oid_key; Type: CONSTRAINT; Schema: development; Owner: -
--

ALTER TABLE ONLY development.role_metadata
    ADD CONSTRAINT role_metadata_role_oid_key UNIQUE (role_oid);


--
-- Name: TABLE role_metadata; Type: ACL; Schema: development; Owner: -
--

GRANT SELECT ON TABLE development.role_metadata TO pwa_workers_inspector;


--
-- PostgreSQL database dump complete
--

\unrestrict d7EbfH6dygvKWptOpbxsEKwYZWwMmGbGLuKZZ9DZxVsZeS1M7l9n5wFo79lzRr0

