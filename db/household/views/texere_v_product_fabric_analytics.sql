--
-- PostgreSQL database dump
--

\restrict hYlALqn7gURngxftJEmt6xmzHrbWNJXl8C6TVXbWFWzFnxbgc3yK3gN5W5Aa2zS

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
-- Name: v_product_fabric_analytics; Type: VIEW; Schema: texere; Owner: -
--

CREATE VIEW texere.v_product_fabric_analytics AS
 SELECT id AS product_id,
    title AS product_title,
    (meta ->> 'title_en'::text) AS product_title_en,
    completion_date,
    item_count,
    macro_category,
    category_l2,
    subcategory_l3,
    item_size,
    production_type,
    using_status,
        CASE
            WHEN ((materials -> 'items'::text) IS NOT NULL) THEN ( SELECT COALESCE(sum((COALESCE(((t.val ->> 'total_consumption_m'::text))::numeric, (0)::numeric) + COALESCE(((t.val ->> 'consumption_m'::text))::numeric, (0)::numeric))), 0.000) AS "coalesce"
               FROM jsonb_each((product_registry.materials -> 'items'::text)) t(key, val))
            WHEN (((materials -> 'fabrics'::text) IS NOT NULL) AND (jsonb_typeof((materials -> 'fabrics'::text)) = 'array'::text)) THEN ( SELECT COALESCE(sum(COALESCE(((elem.value ->> 'consumption_m'::text))::numeric, (0)::numeric)), 0.000) AS "coalesce"
               FROM jsonb_array_elements((product_registry.materials -> 'fabrics'::text)) elem(value))
            ELSE 0.000
        END AS total_fabric_consumption
   FROM texere.product_registry;


--
-- Name: VIEW v_product_fabric_analytics; Type: COMMENT; Schema: texere; Owner: -
--

COMMENT ON VIEW texere.v_product_fabric_analytics IS 'Постоянное аналитическое представление для контроля расхода тканей, статусов использования изделий и категорийного анализа (с поддержкой title_en)';


--
-- Name: TABLE v_product_fabric_analytics; Type: ACL; Schema: texere; Owner: -
--

GRANT SELECT ON TABLE texere.v_product_fabric_analytics TO reflex_app_user;


--
-- PostgreSQL database dump complete
--

\unrestrict hYlALqn7gURngxftJEmt6xmzHrbWNJXl8C6TVXbWFWzFnxbgc3yK3gN5W5Aa2zS

