CREATE OR REPLACE FUNCTION development.fn_auto_generate_uvr()
 RETURNS trigger
 LANGUAGE plpgsql
AS $function$
DECLARE
  v_max int;
BEGIN
  SELECT COALESCE(MAX(code), 0) INTO v_max FROM development.version_updates;
  NEW.code := v_max + 1;
  NEW.update_version_id := 'UVR-' || LPAD(NEW.code::text, 3, '0');
  NEW.created_at := COALESCE(NEW.created_at, CURRENT_TIMESTAMP);
  PERFORM setval('development.version_updates_code_seq', NEW.code + 1, false);
  RETURN NEW;
END;
$function$

