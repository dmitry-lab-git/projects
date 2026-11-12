--
-- PostgreSQL database dump
--

\restrict al3euYj58aKabPutIEpti03fedW5EkBmkvUD7XhQbi5kfDWQ1QKDSTMOy4ornQs

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
-- Name: v_category_usage; Type: VIEW; Schema: reports; Owner: -
--

CREATE VIEW reports.v_category_usage AS
 SELECT c.id,
    c.code,
    c.category_name,
    c.category_id,
    c.parent_category_id,
    c.created_at,
    count(t.id) AS usage_count
   FROM (dicts.dict_categories c
     LEFT JOIN public.transactions t ON ((t.category_id = c.id)))
  GROUP BY c.id, c.code, c.category_name, c.category_id, c.parent_category_id, c.created_at;


--
-- Name: TABLE v_category_usage; Type: ACL; Schema: reports; Owner: -
--

GRANT SELECT ON TABLE reports.v_category_usage TO reflex_app_user;


--
-- PostgreSQL database dump complete
--

\unrestrict al3euYj58aKabPutIEpti03fedW5EkBmkvUD7XhQbi5kfDWQ1QKDSTMOy4ornQs

