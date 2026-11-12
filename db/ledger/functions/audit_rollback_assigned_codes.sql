CREATE OR REPLACE FUNCTION audit.rollback_assigned_codes()
 RETURNS text
 LANGUAGE plpgsql
AS $function$
DECLARE
    posted_status_id UUID;
    cleared_rows INT;
BEGIN
    -- Находим ID статуса POSTED, чтобы ни в коем случае не стереть коды у архивных/проведенных строк
    SELECT id INTO posted_status_id 
    FROM dicts.dict_statuses 
    WHERE entity_type = 'TRANSACTION' AND code = 'POSTED';

    -- Сбрасываем коды обратно в NULL для всех непроведенных строк
    UPDATE audit.staging_transactions
    SET code = NULL
    WHERE status_id IS DISTINCT FROM posted_status_id;

    GET DIAGNOSTICS cleared_rows = ROW_COUNT;

    RETURN 'Откат завершен. Сброшены коды у ' || cleared_rows::TEXT || ' транзакций.';
END;
$function$

