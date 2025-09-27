Feature: Обновление TOC при изменениях файлов

  Background:
    Given каталог "./src" существует
    And в конфиге max_file_mb = 1

  Scenario: Добавление TOC в новый файл
    Given создан файл "./src/a.py" без TOC
    When демон фиксирует событие изменения
    Then в "./src/a.py" появляется блок между маркерами FILE_TOC BEGIN/END

  Scenario: Обновление TOC после правки
    Given файл "./src/b.py" с TOC и классом "B"
    When я добавляю метод "foo(self)"
    And демон фиксирует событие изменения
    Then TOC в "./src/b.py" обновляется и включает "foo(self)"

  Scenario: Игнорирование большого файла
    Given файл "./src/big.py" размером больше 1 МБ
    When big.py изменён
    Then демон ничего не меняет и пишет предупреждение в лог
