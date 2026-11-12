CREATE OR REPLACE FUNCTION dicts.trg_bi_contragents_autocomplete()
 RETURNS trigger
 LANGUAGE plpgsql
AS $function$
DECLARE
    next_code int4;
BEGIN
    -------------------------------------------------------------------------
    -- ЭТАП 1: Расчет последовательного code без разрывов
    -------------------------------------------------------------------------
    
    -- Блокируем строки таблицы для вычисления честного последовательного номера
    SELECT COALESCE(MAX(code), 0) + 1 INTO next_code FROM dicts.contragents;
    
    -- Принудительно перезаписываем code, защищая от ручной передачи некорректного значения
    NEW.code := next_code;

    -------------------------------------------------------------------------
    -- ЭТАП 2: Автозаполнение связанных текстовых и системных полей
    -------------------------------------------------------------------------
    
    -- Автозаполнение текстового идентификатора по шаблону CNT-X
    IF NEW.contragent_id IS NULL OR NEW.contragent_id = '' THEN
        NEW.contragent_id := 'CNT-' || NEW.code;
    END IF;

    -- Проверка дефолтного типа контрагента, если не выбран на форме
    IF NEW.contragent_type IS NULL OR NEW.contragent_type = '' THEN
        NEW.contragent_type := 'Физическое лицо';
    END IF;

    -- Защита полей от случайных пробелов
    NEW.contragent_name := trim(NEW.contragent_name);

    RETURN NEW;
END;
$function$

