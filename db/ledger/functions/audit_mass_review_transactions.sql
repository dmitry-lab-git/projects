CREATE OR REPLACE FUNCTION audit.mass_review_transactions()
 RETURNS text
 LANGUAGE plpgsql
AS $function$
DECLARE
    target_status_id UUID;
    posted_status_id UUID;
    updated_rows INT;
BEGIN
    -- 1. Находим UUID для статуса REVIEWED по правильной колонке code
    SELECT id INTO target_status_id 
    FROM dicts.dict_statuses 
    WHERE entity_type = 'TRANSACTION' AND code = 'REVIEWED';

    -- 2. Находим UUID для статуса POSTED, чтобы случайно не затереть его
    SELECT id INTO posted_status_id 
    FROM dicts.dict_statuses 
    WHERE entity_type = 'TRANSACTION' AND code = 'POSTED';

    -- Защитная проверка
    IF target_status_id IS NULL THEN
        RAISE EXCEPTION 'Критическая ошибка: Статус TRANSACTION/REVIEWED не найден в справочнике статусов!';
    END IF;

    -- 3. Обновляем транзакции в staging: исключаем POSTED и те, что уже REVIEWED
    UPDATE audit.staging_transactions
    SET status_id = target_status_id
    WHERE (status_id IS DISTINCT FROM posted_status_id)
      AND (status_id IS DISTINCT FROM target_status_id);

    GET DIAGNOSTICS updated_rows = ROW_COUNT;

    RETURN 'Успех. Переведено в статус REVIEWED (Утверждено оператором) транзакций: ' || updated_rows::TEXT;
END;
$function$

