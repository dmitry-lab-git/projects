CREATE OR REPLACE FUNCTION audit.assign_transaction_codes()
 RETURNS text
 LANGUAGE plpgsql
AS $function$
DECLARE
    r RECORD;
    start_code INT := 0;
    current_code INT;
    last_valid_id UUID;
    error_count INT;
BEGIN
    -- 1. Динамически определяем стартовый код
    SELECT MAX(code) INTO start_code FROM audit.staging_transactions;
    
    IF start_code IS NULL OR start_code = 0 THEN
        SELECT COALESCE(MAX(code), 0) INTO start_code FROM public.transactions;
    END IF;

    current_code := start_code;

    -- 2. Проверяем наличие невалидных (NULL) значений даты/времени
    SELECT COUNT(*) INTO error_count 
    FROM audit.staging_transactions 
    WHERE code IS NULL AND (operation_date IS NULL OR operation_time IS NULL);

    IF error_count > 0 THEN
        RAISE NOTICE 'ОШИБКА: Найдено транзакций без заполненной даты или времени: %', error_count;
        
        FOR r IN (
            SELECT id, transaction_name, operation_date, operation_time 
            FROM audit.staging_transactions 
            WHERE code IS NULL AND (operation_date IS NULL OR operation_time IS NULL)
            LIMIT 10
        ) LOOP
            RAISE NOTICE 'Требует проверки -> ID: %, Название: %, Дата: %, Время: %', 
                r.id, COALESCE(r.transaction_name, '[Без названия]'), r.operation_date, r.operation_time;
        END LOOP;
        
        RAISE EXCEPTION 'Вычисление прервано. Невозможно определить хронологический порядок для неразмеченных строк.';
    END IF;

    -- 3. Присвоение последовательных кодов для новых строк (code IS NULL)
    FOR r IN 
        SELECT id 
        FROM audit.staging_transactions
        WHERE code IS NULL
        ORDER BY operation_date ASC, operation_time ASC, created_at ASC, id ASC
    LOOP
        current_code := current_code + 1;
        
        UPDATE audit.staging_transactions
        SET code = current_code
        WHERE id = r.id;
        
        last_valid_id := r.id;
    END LOOP;

    -- 4. Результат
    IF current_code = start_code THEN
        RETURN 'Все транзакции уже имеют коды. Новых записей для нумерации не обнаружено.';
    ELSE
        RETURN 'Успех. Новые транзакции пронумерованы. Стартовый код был: ' || start_code::TEXT || ', последний актуальный код: ' || current_code::TEXT;
    END IF;

EXCEPTION
    WHEN OTHERS THEN
        RAISE NOTICE 'Произошел runtime-сбой при обновлении строк.';
        RAISE NOTICE 'Последний успешно обработанный ID транзакции: %', COALESCE(last_valid_id::text, 'нет');
        RAISE NOTICE 'Последний рабочий код: %', current_code;
        RAISE; -- Откатываем (ROLLBACK) изменения текущей сессии
END;
$function$

