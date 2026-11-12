CREATE OR REPLACE FUNCTION reports.refresh_ledger_by_accounts()
 RETURNS void
 LANGUAGE plpgsql
AS $function$
BEGIN
    TRUNCATE TABLE reports.ledger_by_accounts;

    INSERT INTO reports.ledger_by_accounts (
        transaction_id, 
        account_id, 
        account_balance, 
        system_balance, 
        transaction_name,
        account_is_verified,
        system_is_verified
    )
    WITH all_transactions AS (
        SELECT DISTINCT 
            tr.code as transaction_id, 
            tr.transaction_name
        FROM public.transactions tr
    ),
    all_accounts AS (
        SELECT DISTINCT 
            acc.account_id
        FROM dicts.accounts acc
    ),
    -- Матрица: каждая транзакция со всеми уникальными счетами системы
    grid AS (
        SELECT 
            t.transaction_id, 
            t.transaction_name, 
            a.account_id
        FROM all_transactions t
        CROSS JOIN all_accounts a
    ),
    -- Снэпшоты из регистра (для транзакций >= 1363)
    snapshot_mapping AS (
        SELECT DISTINCT 
            s.tr_id::integer as snapshot_tr_id,
            s.account_id
        FROM public.acc_balance_snapshot_register s
        WHERE s.account_id IS NOT NULL 
          AND s.tr_id ~ '^\d+$'
    ),
    -- Реальные движения и ревизии, строго привязанные к transactions.account_id
    tx_events AS (
        SELECT 
            tr.code as transaction_id,
            acc.account_id as account_id,
            tr.amount * COALESCE(t.account_effect, 1) as delta,
            -- Является ли транзакция ревизией ИМЕННО для этого счета по названию (< 1363)
            CASE 
                WHEN tr.code < 1363 AND tr.transaction_name ILIKE '%Ревизия%' THEN TRUE 
                ELSE FALSE 
            END as is_rev_name
        FROM public.transactions tr
        LEFT JOIN dicts.dict_types t ON tr.type_id = t.id
        LEFT JOIN dicts.accounts acc ON tr.account_id = acc.id
        WHERE tr.account_id IS NOT NULL
    ),
    -- Соединяем матрицу со счетами и транзакциями
    combined AS (
        SELECT 
            g.transaction_id,
            g.transaction_name,
            g.account_id,
            COALESCE(te.delta, 0) as delta,
            COALESCE(te.is_rev_name, FALSE) as is_rev_name,
            CASE WHEN sm.snapshot_tr_id IS NOT NULL THEN TRUE ELSE FALSE END as has_snapshot
        FROM grid g
        LEFT JOIN tx_events te 
            ON g.transaction_id = te.transaction_id 
           AND g.account_id = te.account_id
        LEFT JOIN snapshot_mapping sm
            ON g.transaction_id = sm.snapshot_tr_id
           AND g.account_id = sm.account_id
    ),
    -- События верификации и движений применительно к конкретному счету в сетке
    events AS (
        SELECT 
            transaction_id,
            transaction_name,
            account_id,
            delta,
            -- Событие верификации для данного счета
            CASE 
                WHEN (transaction_id < 1363 AND is_rev_name) OR (transaction_id >= 1363 AND has_snapshot) THEN TRUE 
                ELSE FALSE 
            END as is_verification_event,
            -- Обычное движение баланса (дельта не 0 и не событие верификации)
            CASE 
                WHEN delta <> 0 AND NOT ((transaction_id < 1363 AND is_rev_name) OR (transaction_id >= 1363 AND has_snapshot)) THEN TRUE 
                ELSE FALSE 
            END as is_movement_event
        FROM combined
    ),
    -- Накопительные итоги и маркеры
    running_accounts AS (
        SELECT 
            transaction_id,
            transaction_name,
            account_id,
            delta,
            SUM(delta) OVER (
                PARTITION BY account_id 
                ORDER BY transaction_id 
                ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
            ) as account_balance,
            -- Последняя точка верификации для счета (по умолчанию 0, т.к. с 1 транзакции все верифицированы)
            COALESCE(
                MAX(CASE WHEN is_verification_event THEN transaction_id END) OVER (
                    PARTITION BY account_id 
                    ORDER BY transaction_id 
                    ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
                ), 0
            ) as max_verif_tr,
            -- Последнее движение баланса для счета
            COALESCE(
                MAX(CASE WHEN is_movement_event THEN transaction_id END) OVER (
                    PARTITION BY account_id 
                    ORDER BY transaction_id 
                    ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
                ), -1
            ) as max_mov_tr
        FROM events
    ),
    -- Статус верификации конкретного счета
    verified_status AS (
        SELECT 
            transaction_id,
            transaction_name,
            account_id,
            account_balance,
            CASE 
                WHEN transaction_id < 1363 THEN (max_verif_tr >= max_mov_tr)
                ELSE (max_verif_tr > 0)
            END as account_is_verified
        FROM running_accounts
    ),
    -- Системный статус верификации (TRUE, если все счета верифицированы)
    system_verification AS (
        SELECT 
            transaction_id,
            transaction_name,
            account_id,
            account_balance,
            account_is_verified,
            BOOL_AND(account_is_verified) OVER (PARTITION BY transaction_id) as system_is_verified
        FROM verified_status
    ),
    -- Накопительный системный баланс
    running_system AS (
        SELECT 
            transaction_id,
            SUM(delta) OVER (
                ORDER BY transaction_id 
                ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
            ) as system_balance
        FROM (
            SELECT transaction_id, SUM(delta) as delta
            FROM combined
            GROUP BY transaction_id
        ) t_totals
    )
    SELECT 
        sv.transaction_id,
        sv.account_id,
        sv.account_balance,
        rs.system_balance,
        sv.transaction_name,
        sv.account_is_verified,
        sv.system_is_verified
    FROM system_verification sv
    JOIN running_system rs ON sv.transaction_id = rs.transaction_id
    ORDER BY sv.transaction_id ASC, sv.account_id ASC;

EXCEPTION
    WHEN OTHERS THEN
        RAISE;
END;
$function$

