--
-- PostgreSQL database dump
--

\restrict 4yz5bvAHQ9gOajwlODf36mSr8jNGxAs3FKtGdxYQ1TSSQbORXeDDroc9PrHupe6

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
-- Name: v_international_media_catalog; Type: VIEW; Schema: texere; Owner: -
--

CREATE VIEW texere.v_international_media_catalog AS
 WITH expanded_fabrics AS (
         SELECT product_registry.id,
            COALESCE(NULLIF(product_registry.total_fabric_consumption, 0.000), ( SELECT sum(((fabric.value ->> 'consumption_m'::text))::numeric) AS sum
                   FROM jsonb_array_elements(
                        CASE
                            WHEN (jsonb_typeof((product_registry.materials -> 'fabrics'::text)) = 'array'::text) THEN (product_registry.materials -> 'fabrics'::text)
                            ELSE '[]'::jsonb
                        END) fabric(value)), ((product_registry.meta ->> 'fabric_cutting_length_m'::text))::numeric, NULLIF(("substring"(((product_registry.meta -> 'normalization_stamp'::text) ->> 'consumption_note'::text), 'Расход ([0-9.]+)'::text))::numeric, 0.000), NULLIF(("substring"(product_registry.comments, 'расход ([0-9.]+)'::text))::numeric, 0.000), NULLIF(("substring"(product_registry.comments, 'велюр Visavi 30 \(([0-9.]+)\)'::text))::numeric, 0.000), (0)::numeric) AS total_project_consumption_raw
           FROM texere.product_registry
        ), item_counts AS (
         SELECT pr_counts.id,
            pr_counts.item_count AS actual_item_count
           FROM texere.product_registry pr_counts
        )
 SELECT
        CASE
            WHEN ((pr.id = '9b594a7e-9e9a-4f00-b1cf-09feadba13c7'::uuid) AND ((pr.macro_category)::text = 'Upcycling & Accessories'::text)) THEN '9b594a7e-9e9a-4f00-b1cf-09feadba13c8'::uuid
            ELSE pr.id
        END AS product_id,
    COALESCE((pr.meta ->> 'title_en'::text), (pr.title)::text) AS title_en,
        CASE
            WHEN ((pr.macro_category)::text = ANY (ARRAY[('Home Textiles'::character varying)::text, ('Interior'::character varying)::text, ('Home Textiles & Interior'::character varying)::text])) THEN ('Home Textiles & Interior'::text)::character varying
            WHEN ((pr.macro_category)::text = ANY (ARRAY[('Apparel'::character varying)::text, ('Tops'::character varying)::text, ('Bottoms'::character varying)::text])) THEN ('Apparel (Tops & Bottoms)'::text)::character varying
            WHEN (((pr.macro_category)::text = ANY (ARRAY[('Accessories'::character varying)::text, ('Upcycling'::character varying)::text])) OR (((pr.meta ->> 'is_upcycling'::text))::boolean = true)) THEN ('Upcycling & Accessories'::text)::character varying
            ELSE pr.macro_category
        END AS macro_category,
    pr.category_l2,
    pr.subcategory_l3,
    COALESCE((pr.meta ->> 'suit_set_code'::text), 'Single Item'::text) AS suit_set_code,
        CASE
            WHEN (pr.quality_rating <= 5) THEN 'Defect'::text
            WHEN (((pr.using_status)::text ~~ '%в архиве%'::text) OR ((pr.using_status)::text ~~ '%в хранении%'::text)) THEN 'In Storage'::text
            WHEN (((pr.using_status)::text ~~ '%утеряно%'::text) OR ((pr.using_status)::text ~~ '%изношено%'::text)) THEN 'Worn Out / Lost (From Gifted)'::text
            WHEN (((pr.using_status)::text ~~ '%подарено%'::text) AND ((pr.using_status)::text ~~ '%активно используется%'::text)) THEN 'Gifted & Actively Used'::text
            WHEN (((pr.using_status)::text ~~ '%подарено%'::text) OR ((pr.meta ->> 'gift_recipient'::text) IS NOT NULL) OR ((pr.meta ->> 'recipient'::text) IS NOT NULL)) THEN 'Gifted (In Wardrobe / Used)'::text
            ELSE 'Actively Used'::text
        END AS item_status,
    pr.using_status AS usage,
        CASE
            WHEN (((pr.gender)::text = 'male'::text) OR ((pr.gender)::text = 'Мужская'::text)) THEN 'Men'::text
            WHEN (((pr.gender)::text = 'female'::text) OR ((pr.gender)::text = 'Женская'::text)) THEN 'Women'::text
            ELSE 'Unisex'::text
        END AS target_audience,
    pr.item_size,
    pr.size_standard,
    ic.actual_item_count AS items,
    pr.batches_count,
        CASE
            WHEN (((pr.meta ->> 'is_upcycling'::text))::boolean = true) THEN 'Upcycling'::text
            ELSE 'New Materials'::text
        END AS production_type,
    COALESCE(pr.completion_date, (((pr.meta -> 'workflow_timestamps'::text) ->> 'completion_approx_date'::text))::date) AS completed_at,
    (ef.total_project_consumption_raw)::numeric(10,3) AS total_project_consumption_m
   FROM ((texere.product_registry pr
     JOIN expanded_fabrics ef ON ((pr.id = ef.id)))
     JOIN item_counts ic ON ((pr.id = ic.id)))
  WHERE (((pr.meta ->> 'data_checked'::text))::boolean = true);


--
-- Name: TABLE v_international_media_catalog; Type: ACL; Schema: texere; Owner: -
--

GRANT SELECT ON TABLE texere.v_international_media_catalog TO reflex_app_user;


--
-- PostgreSQL database dump complete
--

\unrestrict 4yz5bvAHQ9gOajwlODf36mSr8jNGxAs3FKtGdxYQ1TSSQbORXeDDroc9PrHupe6

