canonical_brief:
  project: "<Название проекта>"
  customer: "Quantum Insight"
  date: "<Дата>"

  goals:
    - "Основная цель 1"
    - "Основная цель 2"

  scope_in:
    - "Что входит в рамки проекта"
  scope_out:
    - "Что не входит (явно исключено)"

  functional_reqs:
    - REQ-01: "Пользователь может войти в систему"
    - REQ-02: "Администратор видит журнал логинов"

  non_functional_reqs:
    performance: "p99 ≤ 300ms при 10k rps"
    availability: "99.9%"
    security: ["RBAC", "журнал аудита", "шифрование"]
    compliance: ["ГОСТ Р 56939", "ФЗ-152 о персональных данных"]

  acceptance_criteria:
    - "Все REQ имеют автотесты и проходят в CI"
    - "Все NFR подтверждены нагрузочным тестом"
    - "ПМИ и Отчёт об испытаниях сформированы автоматически"

  constraints:
    language: "Python 3.12"
    framework: "FastAPI"
    db: "Postgres 15"
    infra: "Docker + Kubernetes"

  risks:
    - id: RISK-01
      desc: "Размытое ТЗ"
      mitigation: "Нормализация требований в Canonical Brief"

  notes:
    - "Все требования фиксируются в матрице трассируемости (trace_matrix.csv)"
    - "Этот файл — источник истины для PMM"
