# Mapping контрактов к тестам

- CLI-START → e2e: tests/e2e/test_cli.py::test_start
- CLI-STOP → e2e: tests/e2e/test_cli.py::test_stop
- CLI-STATUS → e2e: tests/e2e/test_cli.py::test_status
- FILE-CREATE-TOC → integration: tests/integration/test_watcher.py::test_create_or_modify_adds_toc
- FILE-IGNORE-BIG → integration: tests/integration/test_watcher.py::test_large_file_ignored

Гейт CI: если для любого элемента из `contracts.yaml` нет привязанного теста — сборка падает.
