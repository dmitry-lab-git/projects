--
-- PostgreSQL database dump
--

\restrict qcVTLRdfWvsKzHuZtfGXh1WCqv9zHlPtb5dLDZAPdshYTBsPxQealqo835r8aOH

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
-- Name: v_transactions_last; Type: VIEW; Schema: reports; Owner: -
--

CREATE VIEW reports.v_transactions_last AS
 SELECT code,
    transaction_name,
    amount,
    created_at
   FROM public.transactions;


--
-- Name: TABLE v_transactions_last; Type: ACL; Schema: reports; Owner: -
--

GRANT SELECT ON TABLE reports.v_transactions_last TO reflex_app_user;


--
-- PostgreSQL database dump complete
--

\unrestrict qcVTLRdfWvsKzHuZtfGXh1WCqv9zHlPtb5dLDZAPdshYTBsPxQealqo835r8aOH

