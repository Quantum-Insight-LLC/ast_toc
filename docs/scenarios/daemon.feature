Feature: Управление демоном AST-TOC

  Scenario: Запуск демона
    Given демон не запущен
    When я выполняю "ast_toc start"
    Then статус демона равен "running"
    And код возврата равен 0

  Scenario: Остановка демона
    Given демон запущен
    When я выполняю "ast_toc stop"
    Then статус демона равен "stopped"
    And код возврата равен 0

  Scenario: Статус демона
    Given демон запущен
    When я выполняю "ast_toc status"
    Then вывод содержит "running (pid="
