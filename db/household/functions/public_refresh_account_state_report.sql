CREATE OR REPLACE FUNCTION public.refresh_account_state_report()
 RETURNS void
 LANGUAGE plpgsql
AS $function$
DECLARE
    v_total_count INTEGER;
    v_verified_count INTEGER;
    v_total_balance_sum NUMERIC(19, 4);
    v_verified_ids UUID[]; -- Массив настоящих UUID
    v_status_id UUID;
    v_verification_hash VARCHAR(64);
BEGIN
    -- 1. Очищаем старый отчет
    TRUNCATE TABLE reports.account_state_report;

    -- 2. Генерируем новый отчет и вставляем данные
    INSERT INTO reports.account_state_report (
        account_id, 
        account_name, 
        entity, 
        balance, 
        account_balance_status, 
        last_updated, 
        account_state, 
        snapshot_tr_id, 
        acc_last_tr_id, 
        acc_balance_snapshot_balance
    )
    WITH latest_ledger AS (
        SELECT 
            account_id,
            MAX(transaction_id) as last_tr_id,
            (ARRAY_AGG(acc_balance ORDER BY transaction_id DESC))[1] as current_balance
        FROM public.ledger 
        GROUP BY account_id
    ),
    latest_snapshot AS (
        SELECT DISTINCT ON (account_id)
            account_id,
            tr_id::integer as snapshot_tr_id,
            balance::numeric as snapshot_balance
        FROM public.acc_balance_snapshot_register
        ORDER BY account_id, code DESC
    ),
    combined AS (
        SELECT 
            acc.account_id::varchar(50),
            acc.account_name,
            ent.entity_name,
            ll.current_balance,
            CASE 
                WHEN ls.snapshot_tr_id IS NULL THEN 'no_snapshot'
                WHEN ls.snapshot_tr_id < ll.last_tr_id THEN 'outdated'
                WHEN ls.snapshot_balance != ll.current_balance THEN 'balance_mismatch'
                ELSE 'verified'
            END as status,
            CURRENT_TIMESTAMP as last_updated,
            CASE 
                WHEN EXISTS (
                    SELECT 1 FROM public.ledger l 
                    WHERE l.account_id = acc.account_id 
                      AND l.operation_date > CURRENT_DATE - INTERVAL '3 months'
                ) OR ll.current_balance != 0 THEN 'active'
                ELSE 'inactive'
            END as state,
            ls.snapshot_tr_id,
            ll.last_tr_id,
            ls.snapshot_balance
        FROM dicts.accounts acc
        JOIN latest_ledger ll ON acc.account_id = ll.account_id
        LEFT JOIN latest_snapshot ls ON acc.account_id = ls.account_id
        LEFT JOIN dicts.entities ent ON acc.entity_id = ent.entity_id
        WHERE (ll.current_balance != 0 OR EXISTS (SELECT 1 FROM public.ledger WHERE account_id = acc.account_id))
    )
    SELECT * FROM combined;

    -- 3. Вызываем отдельную функцию логирования
    PERFORM public.log_system_verification();

END;
$function$

