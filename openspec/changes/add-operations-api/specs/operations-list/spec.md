## ADDED Requirements

### Requirement: Получение операций с пагинацией
Система SHALL предоставлять ручку `GET /operations` с параметрами `limit` (по умолчанию 20, от 1 до 100) и `offset` (по умолчанию 0, не меньше 0), возвращающую объект `{items, total, limit, offset}`, отсортированный по дате создания от новых к старым.

#### Scenario: Первая страница
- **WHEN** в системе 45 операций и клиент вызывает `GET /operations?limit=20&offset=0`
- **THEN** система отвечает `200`, `items` содержит 20 самых новых операций, `total=45`

#### Scenario: Последняя неполная страница
- **WHEN** в системе 45 операций и клиент вызывает `GET /operations?limit=20&offset=40`
- **THEN** `items` содержит 5 операций

#### Scenario: Некорректные параметры
- **WHEN** клиент вызывает `GET /operations?limit=1000`
- **THEN** система отвечает `422`

#### Scenario: Пустой список
- **WHEN** операций нет
- **THEN** система отвечает `200` с пустым `items` и `total=0`

### Requirement: Группа операции
Каждая операция в ответе SHALL содержать поле `category` со значением из набора `transfer`, `salary`, `other`, `uncategorized`; для новых загруженных операций значение равно `uncategorized`.

#### Scenario: Операция с проставленной группой
- **WHEN** у операции в БД `category=salary`
- **THEN** в ответе `GET /operations` эта операция имеет `category: "salary"`
