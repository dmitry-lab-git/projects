--
-- PostgreSQL database dump
--

\restrict POZ4zoVlv14mfSJwqjEl1OjJnSVZit8ICwdpnczKQzCDsJFpy19Y3lGjVEaOkoX

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
-- Name: v_material_disposition_summary; Type: VIEW; Schema: infrastructure; Owner: -
--

CREATE VIEW infrastructure.v_material_disposition_summary AS
 SELECT 'by_resource'::text AS report_type,
    TRIM(BOTH FROM to_char((md.utilized_at)::timestamp with time zone, 'fmMonth YYYY'::text)) AS report_month,
    rc.material_name AS grouping_key,
    sum(md.quantity) AS total_mass,
    count(md.id) AS total_count
   FROM (infrastructure.material_disposition md
     JOIN infrastructure.resource_catalog rc ON ((md.resource_id = rc.id)))
  GROUP BY (TRIM(BOTH FROM to_char((md.utilized_at)::timestamp with time zone, 'fmMonth YYYY'::text))), rc.material_name
UNION ALL
 SELECT 'by_disposal_point'::text AS report_type,
    TRIM(BOTH FROM to_char((md.utilized_at)::timestamp with time zone, 'fmMonth YYYY'::text)) AS report_month,
    COALESCE(dp.name, 'Не указан'::character varying) AS grouping_key,
    sum(md.quantity) AS total_mass,
    count(md.id) AS total_count
   FROM (infrastructure.material_disposition md
     LEFT JOIN infrastructure.disposal_points dp ON ((md.disposal_point = dp.id)))
  GROUP BY (TRIM(BOTH FROM to_char((md.utilized_at)::timestamp with time zone, 'fmMonth YYYY'::text))), dp.name;


--
-- Name: TABLE v_material_disposition_summary; Type: ACL; Schema: infrastructure; Owner: -
--

GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE infrastructure.v_material_disposition_summary TO reflex_app_user;


--
-- PostgreSQL database dump complete
--

\unrestrict POZ4zoVlv14mfSJwqjEl1OjJnSVZit8ICwdpnczKQzCDsJFpy19Y3lGjVEaOkoX

