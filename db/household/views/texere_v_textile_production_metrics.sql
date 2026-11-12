--
-- PostgreSQL database dump
--

\restrict YcWgHGUUbp0UoSrGhy2Pim4PVZ1Qrhh5H6mzibx9icKwo1ZXeEwzXUZMzvqLB3F

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
-- Name: v_textile_production_metrics; Type: VIEW; Schema: texere; Owner: -
--

CREATE VIEW texere.v_textile_production_metrics AS
 SELECT macro_category,
    count(DISTINCT product_id) AS total_projects,
    sum(items) AS total_items_produced,
    round(sum(total_project_consumption_m), 2) AS total_fabric_consumed_m,
    round(avg(total_project_consumption_m), 2) AS avg_consumption_per_project
   FROM texere.v_international_media_catalog
  GROUP BY macro_category;


--
-- Name: TABLE v_textile_production_metrics; Type: ACL; Schema: texere; Owner: -
--

GRANT SELECT ON TABLE texere.v_textile_production_metrics TO reflex_app_user;


--
-- PostgreSQL database dump complete
--

\unrestrict YcWgHGUUbp0UoSrGhy2Pim4PVZ1Qrhh5H6mzibx9icKwo1ZXeEwzXUZMzvqLB3F

