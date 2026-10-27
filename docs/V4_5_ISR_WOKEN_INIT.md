# v4.5 — eksperyment: inicjalizacja flagi przełączenia zadania w ISR

**Stan: kod kandydujący do testów, brak fizycznego odbioru v4.5, bez scalenia do `main`.**

## Punkt wyjścia

Gałąź `experiment/v4.5-isr-woken-init` powstała dokładnie z fizycznie testowanej v4.4 (`16ed1c1e3d7da2ce4d463e8351224183b25612ee`). Zachowuje FIFO16 i kasowanie starych powiadomień po pełnym odczycie, przed `restart_rx()`.

W 22m29s teście v4.4: 33 prawidłowe telegramy GAMA, 35 pełnych ramek 326 B, 115 Apator, 0 pustych timeoutów, **1 RX FIFO overflow**, 3 ostrzeżenia `RXBYTES=65`, 2 błędy 3-of-6, zero `queue_drops`. Nie jest to potwierdzona konfiguracja produkcyjna.

## Jedyna zmiana w produkcyjnym C++

W `Radio::wakeup_receiver_task_from_isr()`:

```diff
-  BaseType_t xHigherPriorityTaskWoken;
+  BaseType_t xHigherPriorityTaskWoken = pdFALSE;
```

FreeRTOS wymaga zainicjalizowania wskaźnika `pxHigherPriorityTaskWoken` wartością `pdFALSE` przed `vTaskNotifyGiveFromISR()`. Bez tego `portYIELD_FROM_ISR()` może otrzymać niezdefiniowaną wartość, gdy nie było powodu do przełączenia zadania. To korekta API, **nie dowód rozwiązania błędów RF**.

Oficjalna dokumentacja: https://www.freertos.org/media/2018/FreeRTOS_Reference_Manual_V10.0.0.pdf

Wszystkie inne aspekty pozostają identyczne z v4.4: GDO ISR/notification, `ulTaskNotifyTake(pdTRUE, 0)`, SPI, próg FIFO16, rejestry CC1101, 868.950 MHz, 325 kHz, radio diagnostics, dekodery 3of6, GAMA/Apator, AES, Home Assistant i UDP. Patch 0007 plus testy i mechanizm bootstrapa nie dodają odczytów SPI ani nowych logów wewnątrz odbioru ramki.

## Odbiór i bramki

- Pinned upstream i **7** łatek, `git apply --check` / `git diff --check`; sprawdzenie dokładnie jednej inicjalizacji i zachowania poprawek v4.1/v4.4.
- Testy natywne, regresja odświeżania cache GitHub oraz kompilacja ESPHome 2026.10.0 z przygotowanego źródła i bezpośrednio z `github://`.
- GitHub Actions **nigdy nie flashuje ESP32** ani nie łączy się z Home Assistant.
- Do czasu uzyskania wyników dłuższego testu v4.4: **nie instalować v4.5, nie scalać PR.**
- Test fizyczny v4.5 wyłącznie po zielonym CI i decyzji właściciela; pierwsze 10–15 minut pod nadzorem, a potem dłuższe porównanie GAMA/Apator, 326 B, 3of6, `RX FIFO overflow`, `RXBYTES=65`, `unstable_rxbytes`, pustych timeoutów i `RX_DIAG cumulative`.

## Instalacja przez ESPHome GUI — dopiero po zgodzie właściciela

Zachowaj cały dotychczasowy YAML, podmień tylko źródło:

```yaml
external_components:
  - source: github://smarthomewithme/wmbus-gama350-reader@experiment/v4.5-isr-woken-init
    refresh: always
    components: [wmbus_radio, wmbus_common, wmbus_meter, socket_transmitter]
```

ESPHome: **Clean Build Files → Validate → Install → Wirelessly**. Znacznik `CC1101 v4.5 ISR woken initialization experiment ready` jest komunikatem *budowania komponentów na hoście ESPHome*, a nie logiem uruchomionego urządzenia. Log z urządzenia nadal zawiera marker v4.1 FIFO16.

**Rollback**: przy serii przepełnień albo zanikających wskazaniach wróć w YAML do `@experiment/v4.4-stale-irq-clear` lub `@experiment/v4.1-fifo16`, potem Clean Build Files → Validate → Install → Wirelessly.
