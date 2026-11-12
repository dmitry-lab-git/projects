CREATE OR REPLACE FUNCTION audit.get_unposted_transactions()
 RETURNS TABLE(id uuid, code integer, transaction_name character varying, operation_date date, operation_time time without time zone, amount numeric, current_status_code character varying, current_status_name character varying, category_name character varying, type_name character varying, contragent_from_name character varying, contragent_to_name character varying, account_name character varying, account_details character varying)
 LANGUAGE plpgsql
AS $function$
BEGIN
    RETURN QUERY
    SELECT 
        st.id,
        st.code,
        st.transaction_name,
        st.operation_date,
        st.operation_time,
        st.amount,
        ds.code::varchar,
        ds.name::varchar,
        cat.category_name::varchar,
        dt.type_name::varchar,
        cf.contragent_name::varchar,
        ct.contragent_name::varchar,
        acc.account_name::varchar,
        (COALESCE(e.entity_name, '') || ' (' || COALESCE(e.entity_id, '') || ' (' || COALESCE(acc.account_id, '') || '))')::varchar AS account_details
    FROM audit.staging_transactions st
    LEFT JOIN dicts.dict_statuses ds ON st.status_id = ds.id
    LEFT JOIN dicts.dict_categories cat ON st.category_id = cat.id
    LEFT JOIN dicts.dict_types dt ON st.type_id = dt.id
    LEFT JOIN dicts.contragents cf ON st.contragent_from_id = cf.id
    LEFT JOIN dicts.contragents ct ON st.contragent_to_id = ct.id
    LEFT JOIN dicts.accounts acc ON st.account_id = acc.id
    LEFT JOIN dicts.entities e ON acc.entity_id::text = e.id::text OR acc.entity_id = e.entity_id
    WHERE st.status_id IS NULL 
       OR NOT (ds.entity_type = 'TRANSACTION' AND ds.code = 'POSTED')
    ORDER BY 
        st.code ASC NULLS LAST, 
        st.operation_date DESC NULLS LAST, 
        st.operation_time DESC NULLS LAST;
END;
$function$

