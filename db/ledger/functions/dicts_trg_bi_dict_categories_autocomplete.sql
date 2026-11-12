CREATE OR REPLACE FUNCTION dicts.trg_bi_dict_categories_autocomplete()
 RETURNS trigger
 LANGUAGE plpgsql
AS $function$
DECLARE
    next_code int4;
BEGIN
    -------------------------------------------------------------------------
    -- ЭТАП 1: Расчет последовательного code без разрывов
    -------------------------------------------------------------------------
    SELECT COALESCE(MAX(code), 0) + 1 INTO next_code FROM dicts.dict_categories;
    NEW.code := next_code;

    -------------------------------------------------------------------------
    -- ЭТАП 2: Автозаполнение текстовых и системных полей
    -------------------------------------------------------------------------
    -- Автозаполнение идентификатора по шаблону CAT-X
    IF NEW.category_id IS NULL OR NEW.category_id = '' THEN
        NEW.category_id := 'CAT-' || NEW.code;
    END IF;

    -- Защита от лишних пробелов в наименовании
    NEW.category_name := trim(NEW.category_name);

    RETURN NEW;
END;
$function$

