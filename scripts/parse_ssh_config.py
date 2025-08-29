import json
import os
import sys
from typing import Dict


def load_config(config_path: str) -> Dict[str, str]:
    """
    Считывает sshd_config и возвращает словарь { "param": "value" }.
    Если параметр отсутствует в файле, его значение будет "no".
    """
    if not os.path.isfile(config_path):
        raise FileNotFoundError(f"sshd_config file not found at {config_path}")

    with open(config_path, "r") as f:
        lines = [line.strip() for line in f if line.strip() and not line.startswith("#")]

    config = {}
    for line in lines:
        parts = line.split(maxsplit=1)
        if len(parts) == 2:
            key, value = parts
            config[key] = value
    return config


def extract_relevant(config: Dict[str, str], standards: Dict[str, str]) -> Dict[str, str]:
    """
    Достаёт только те параметры, которые есть в эталоне.
    Если параметр отсутствует в config, подставляет "no".
    """
    return {param: config.get(param, "no") for param in standards.keys()}


def find_non_compliance(found: Dict[str, str], standards: Dict[str, str]) -> Dict[str, Dict[str, str]]:
    """
    Сравнивает найденные значения с эталонными.
    Возвращает словарь несоответствий.
    """
    violations = {}
    for param, expected in standards.items():
        actual = found[param]
        if actual != expected:
            violations[param] = {"expected": expected, "found": actual}
    return violations


def audit_sshd(config_path: str, standards: Dict[str, str]) -> Dict:
    """
    Основная функция: загружает конфиг, фильтрует нужные параметры,
    проверяет на соответствие.
    """
    config = load_config(config_path)
    found = extract_relevant(config, standards)
    violations = find_non_compliance(found, standards)

    status = "compliant" if not violations else "non-compliant"

    return {
        "message": {"status": status}
    }


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} <path_to_sshd_config> <path_to_standards.json>")
        sys.exit(1)

    sshd_config_path = sys.argv[1]
    standards_path = sys.argv[2]

    with open(standards_path, "r") as f:
        standards = json.load(f)

    audit_result = audit_sshd(sshd_config_path, standards)
    print(json.dumps(audit_result, indent=2))
