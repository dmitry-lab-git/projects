--
-- PostgreSQL database dump
--

\restrict vCELRg3wdSBLWd3OlhtiFJb5NIOvYe1kBKzgRFKtjLpovUPCUem19eIGg5VlioM

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
-- Name: v_project_summary_post; Type: VIEW; Schema: texere; Owner: -
--

CREATE VIEW texere.v_project_summary_post AS
 SELECT id AS project_id,
    title AS project_title,
    COALESCE((meta ->> 'title_en'::text), (title)::text) AS project_title_en,
    macro_category,
    category_l2,
    subcategory_l3,
    item_size,
    size_standard,
    item_count AS quantity,
    batches_count,
    production_type,
    using_status,
    quality_rating,
    project_cost_kzt,
    COALESCE(completion_date, (((meta -> 'workflow_timestamps'::text) ->> 'completion_approx_date'::text))::date) AS completion_date,
        CASE
            WHEN (quality_rating <= 5) THEN 'Требует доработки / Опыт'::text
            WHEN (((meta ->> 'gift_recipient'::text) IS NOT NULL) OR ((meta ->> 'recipient'::text) IS NOT NULL)) THEN 'Подарочный проект'::text
            ELSE 'Основная линейка'::text
        END AS project_category_status
   FROM texere.product_registry
  WHERE (((meta ->> 'data_checked'::text))::boolean = true);


--
-- Name: TABLE v_project_summary_post; Type: ACL; Schema: texere; Owner: -
--

GRANT SELECT ON TABLE texere.v_project_summary_post TO reflex_app_user;


--
-- PostgreSQL database dump complete
--

\unrestrict vCELRg3wdSBLWd3OlhtiFJb5NIOvYe1kBKzgRFKtjLpovUPCUem19eIGg5VlioM

