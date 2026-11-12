--
-- PostgreSQL database dump
--

\restrict zmUc06vaX1oe9mfGSjlawwPwfV6sgUJHSbNZvfz3XVkUAdENYnvxwpBsCB0VDlN

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

--
-- Name: version_registry_report; Type: VIEW; Schema: reports; Owner: -
--

CREATE VIEW reports.version_registry_report AS
 SELECT version_id AS current_ver,
    update_version_id AS current_uvr,
    registration_date,
    description,
    affected_objects,
    code,
    created_at
   FROM development.version_updates
  ORDER BY registration_date DESC, code DESC
 LIMIT 1;


--
-- Name: TABLE version_registry_report; Type: ACL; Schema: reports; Owner: -
--

GRANT SELECT ON TABLE reports.version_registry_report TO reflex_app_user;


--
-- PostgreSQL database dump complete
--

\unrestrict zmUc06vaX1oe9mfGSjlawwPwfV6sgUJHSbNZvfz3XVkUAdENYnvxwpBsCB0VDlN

