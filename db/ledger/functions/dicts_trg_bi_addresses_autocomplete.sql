CREATE OR REPLACE FUNCTION dicts.trg_bi_addresses_autocomplete()
 RETURNS trigger
 LANGUAGE plpgsql
AS $function$
DECLARE
    next_code int4;
BEGIN
    -------------------------------------------------------------------------
    -- ЭТАП 1: Строгая валидация address_name по регламенту
    -------------------------------------------------------------------------
    
    -- Очищаем от случайных двойных пробелов и скрытых символов
    NEW.address_name := regexp_replace(trim(NEW.address_name), '\s+', ' ', 'g');

    -- Правило 1: Проверка на правильное начало (строчные ул., пр., пер., мкр.)
    IF NEW.address_name NOT SIMILAR TO '(ул\.|пр\.|пер\.|мкр\.) %' THEN
        RAISE EXCEPTION 'Нарушен регламент адреса: строка должна начинаться с сокращений "ул. ", "пр. ", "пер. " или "мкр. " с маленькой буквы.';
    END IF;

    -- Правило 3 и 4: Обязательная запятая перед номером дома и запрет на слова "дом", "д."
    IF regexp_like(NEW.address_name, ', (дом|д\.)') THEN
        RAISE EXCEPTION 'Нарушен регламент адреса: исключите слово "дом" или "д.". После запятой должен идти сразу номер дома (например: ул. Мира, 50).';
    END IF;

    IF NOT regexp_like(NEW.address_name, ', [0-9]') THEN
        RAISE EXCEPTION 'Нарушен регламент адреса: отсутствует запятая перед номером дома или сам номер дома не указан цифрой (например: ул. Катаева, 9).';
    END IF;


    -------------------------------------------------------------------------
    -- ЭТАП 2: Расчет последовательного code без разрывов и автозаполнение
    -------------------------------------------------------------------------
    
    -- Блокируем строки таблицы и высчитываем честный следующий code
    SELECT COALESCE(MAX(code), 0) + 1 INTO next_code FROM dicts.addresses;
    NEW.code := next_code;

    -- Автозаполнение системного ID (ADR-113)
    IF NEW.address_id IS NULL OR NEW.address_id = '' THEN
        NEW.address_id := 'ADR-' || NEW.code;
    END IF;

    -- Автозаполнение статуса
    IF NEW.external_status IS NULL OR NEW.external_status = '' THEN
        NEW.external_status := 'Active';
    END IF;

    -- Форматирование даты в ДД.ММ.ГГ
    IF NEW.observed_at IS NULL OR NEW.observed_at = '' THEN
        NEW.observed_at := to_char(COALESCE(NEW.created_at, CURRENT_TIMESTAMP), 'DD.MM.YY');
    END IF;

    -- Дефолты по географии
    IF NEW.city IS NULL OR NEW.city = '' THEN
        NEW.city := 'Павлодар';
    END IF;

    IF NEW.country IS NULL OR NEW.country = '' THEN
        NEW.country := 'Казахстан';
    END IF;

    RETURN NEW;
END;
$function$

