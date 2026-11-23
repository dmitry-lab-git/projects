"""Смоук-проверка инициализации и оркестратора рабочего пространства."""

import sys

from workspace_module.orchestrator import Orchestrator


def main() -> int:
    print("--- ЗАПУСК ПРОВЕРКИ WORKSPACE_MODULE ---")
    orc = Orchestrator()
    res = orc.run_night_mode("SmokeCheck")
    if res.get("ok"):
        print("--- ПРОВЕРКА ПРОЙДЕНА ---")
        return 0
    print("--- ПРОВЕРКА НЕ ПРОЙДЕНА ---")
    return 1


if __name__ == "__main__":
    sys.exit(main())