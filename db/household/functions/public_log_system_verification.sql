CREATE OR REPLACE FUNCTION public.log_system_verification()
 RETURNS text
 LANGUAGE plpgsql
AS $function$
DECLARE
    v_total_count INTEGER;
    v_verified_count INTEGER;
    v_total_balance_sum NUMERIC(19, 4);
    v_verified_ids UUID[]; 
    v_last_transaction_id UUID;
    v_status_id UUID;
    v_verification_hash VARCHAR(64);
    v_rows_affected INTEGER;
BEGIN
    -- 1. Находим ID последней актуальной транзакции на текущий момент
    SELECT id INTO v_last_transaction_id
    FROM public.transactions
    ORDER BY created_at DESC
    LIMIT 1;

    -- 2. Собираем показатели из уже сформированного отчета
    SELECT 
        COUNT(*),
        COUNT(*) FILTER (WHERE r.account_balance_status = 'verified'),
        COALESCE(SUM(r.balance) FILTER (WHERE r.account_balance_status = 'verified'), 0),
        ARRAY_AGG(a.id ORDER BY a.id) FILTER (WHERE r.account_balance_status = 'verified'),
        md5(ARRAY_TO_STRING(ARRAY_AGG(a.id::text || ':' || r.balance::text ORDER BY a.id) FILTER (WHERE r.account_balance_status = 'verified'), ','))
    INTO 
        v_total_count, 
        v_verified_count,
        v_total_balance_sum,
        v_verified_ids,
        v_verification_hash
    FROM reports.account_state_report r
    LEFT JOIN dicts.accounts a ON r.account_id = a.account_id;

    -- 3. Проверка жесткого условия
    IF v_total_count > 0 AND v_total_count = v_verified_count THEN
        
        SELECT id INTO v_status_id 
        FROM dicts.dict_statuses 
        WHERE entity_type = 'SYSTEM_VERIFICATION' AND code = 'SUCCESS';

        IF v_status_id IS NULL THEN
            INSERT INTO dicts.dict_statuses (entity_type, code, name)
            VALUES ('SYSTEM_VERIFICATION', 'SUCCESS', 'All accounts verified')
            RETURNING id INTO v_status_id;
        END IF;

        -- Пытаемся записать лог
        INSERT INTO reports.system_verification_log (
            status_id,
            total_accounts_processed, 
            verified_count, 
            total_balance_sum,
            verified_account_ids,
            last_transaction_id,
            verification_hash
        )
        VALUES (
            v_status_id,
            v_total_count, 
            v_verified_count, 
            v_total_balance_sum,
            COALESCE(v_verified_ids, '{}'::UUID[]),
            v_last_transaction_id,
            v_verification_hash
        )
        ON CONFLICT (verification_hash) DO NOTHING;

        -- Проверяем, вставилась ли реальная новая строка
        GET DIAGNOSTICS v_rows_affected = ROW_COUNT;

        IF v_rows_affected > 0 THEN
            RETURN 'All accounts verified, log registered';
        ELSE
            RETURN 'All accounts verified, but no changes detected (duplicate skipped)';
        END IF;
        
    ELSE
        RETURN 'Not all accounts are verified';
    END IF;

END;
$function$

