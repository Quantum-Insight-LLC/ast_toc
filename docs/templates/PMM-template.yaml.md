# Шаблон Project Memory Map (PMM)

```yaml
project:
  name: <PROJECT_NAME>
  domain: <domain>
  runtime:
    language: "Python|Go|Java|TS"
    framework: "<framework>"
    database: "<db>"
    messaging: "<kafka|rabbit|nats|none>"
  non_functionals:
    performance: { p99_ms: 300, rps_target: 200 }
    availability: "99.9%"
    security: ["auth", "audit", "secrets", "rbac"]
    compliance: ["логирование аудита", "журнал операций"]
  patterns: ["Hexagonal", "CQRS", "Event Sourcing"]
modules:
  - name: "identity"
    responsibilities: ["auth", "rbac", "audit"]
    dependencies: ["db", "audit"]
    folders:
      - path: "services/identity"
        files:
          - name: "auth_service.py"
            classes:
              - name: "AuthService"
                methods:
                  - name: "issue_token"
                    input: "CredentialsDTO"
                    output: "JwtToken"
                    invariants: ["lockout on N failures"]
          - name: "tests/test_auth_service.py"
            type: "unit"
            given_when_then:
              - given: "valid credentials"
                when: "issue_token called"
                then: "jwt with claims"
interfaces:
  http:
    - path: "/api/v1/login"
      method: "POST"
      request: "CredentialsDTO"
      response: "JwtToken"
      errors: ["401_INVALID_CREDENTIALS", "423_LOCKED"]
data:
  schemas:
    - name: "User"
      fields: { id: "uuid", email: "string", hash: "string", role: "enum" }
observability:
  metrics:
    - name: "auth.login.success_total" ; type: "counter" ; owner: "identity"
    - name: "auth.login.latency_ms"   ; type: "histogram"
tests:
  pyramid:
    unit: ">=70%"
    integration: "~20%"
    e2e: "~10%"
traceability:
  map_csv: "trace_matrix.csv"
```
