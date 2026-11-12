CREATE OR REPLACE FUNCTION dicts.trg_bi_entities_autocomplete()
 RETURNS trigger
 LANGUAGE plpgsql
AS $function$
DECLARE
    next_code int4;
BEGIN
    -------------------------------------------------------------------------
    -- ЭТАП 1: Расчет последовательного code без разрывов
    -------------------------------------------------------------------------
    SELECT COALESCE(MAX(code), 0) + 1 INTO next_code FROM dicts.entities;
    NEW.code := next_code;

    -------------------------------------------------------------------------
    -- ЭТАП 2: Автозаполнение текстовых и системных полей
    -------------------------------------------------------------------------
    -- Автозаполнение идентификатора по шаблону ENT-X
    IF NEW.entity_id IS NULL OR NEW.entity_id = '' THEN
        NEW.entity_id := 'ENT-' || NEW.code;
    END IF;

    -- Защита от лишних пробелов в наименовании
    NEW.entity_name := trim(NEW.entity_name);

    RETURN NEW;
END;
$function$

