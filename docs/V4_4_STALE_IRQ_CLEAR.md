# v4.4 — eksperyment z czyszczeniem zaległych IRQ (ESPHome OTA)

## Dane wyjściowe
W fizycznym teście v4.1 FIFO16 (03:18:30–06:45:57, 27.10.2026) uzyskano 267 poprawnych GAMA, 292 pełne ramki 326 B, 25 błędów 3-of-6, 661 odczytów Apator, 0 przepełnień FIFO, 0 niestabilnych RXBYTES w pełnych ramkach, 4 błędy kolejki oraz **900 pustych timeoutów nagłówka**, z których 872 logowano w odległości maksymalnie 100 ms od poprawnego odczytu GAMA/Apator. Skuteczność szacowana dla emisji co 30 s: ok. 64,3%.

## Hipoteza, nie potwierdzona przyczyna
CC1101 GDO0 (FIFOTHR 16 B) może wyzwalać wiele IRQ podczas odczytu tej samej ramki. Zaległe powiadomienia FreeRTOS mogą powodować dodatkowe próby nagłówka i długie puste timeouty. Zbieżność czasowa nie dowodzi źródła wszystkich strat GAMA.

## Jedyna zmiana w ścieżce produkcyjnej
Bezpośrednio **po udanym odczycie pełnego payloadu i zapisaniu RSSI**, a **przed `restart_rx()`**, zadanie odbiornika wywołuje `(void) ulTaskNotifyTake(pdTRUE, 0);` w celu skasowania oczekujących sygnałów starej ramki. Zostaje oryginalny ISR, FIFO16, 868.950 MHz, 325 kHz, pinout, SPI, 3-of-6, CRC, AES, oba liczniki, format diagnostyki i 500 ms timeout. Oprócz tego zmieniono tylko kontrolę bootstrapa i CI. Nie dodano żadnych odczytów SPI ani logów w czasie odbioru.

## Bramka przed instalacją
- Przejść natywne testy, kontrolę przygotowanych źródeł oraz kompilację ESPHome 2026.10.0 przez GitHub Actions (zwłaszcza bezpośrednio z `github://`).
- Dodatkowo sprawdzić, że czyszczenie następuje przed ponownym uzbrojeniem odbiornika.
- CI nie może potwierdzić bezpieczeństwa RF. Po dwóch wcześniejszych regresjach v4.2 i v4.3 nie zostawiać nowej wersji bez nadzoru.

## Instalacja przez ESPHome GUI (wyłącznie użytkownik)
W zachowanym YAML podmień **tylko** źródło:

```yaml
external_components:
  - source: github://smarthomewithme/wmbus-gama350-reader@experiment/v4.4-stale-irq-clear
    refresh: always
    components: [wmbus_radio, wmbus_common, wmbus_meter, socket_transmitter]
```

Po zielonym CI: **Clean Build Files → Validate → Install → Wirelessly**. W logu starowym szukaj `CC1101 v4.4 stale IRQ clear experiment ready` oraz `SHWM v4.1 FIFO16 experiment`; nowy znacznik v4.4 w C++ jest komentarzem, nie nowym logiem urządzenia.

## Test fizyczny i stop
- Pierwsze 10–15 minut pod nadzorem, z tą samą anteną, bramą i loggerem co v4.1.
- Zestawić `RX timeout after 0 bytes (need 3)` w przeliczeniu na minutę (v4.1: ~4,34/min), GAMA sukces (v4.1: ~64,3% szacowane), pełne 326 B, 3-of-6, Apator, queue drops, FIFO overflows i stabilność HA.
- **Natychmiast wrócić do v4.1** przy serii overflow, zerwaniu Apatora, braku GAMA lub powtarzających się anomaliach.
- Bez sukcesu 15-min testu — bez 6h testu i bez merge do `main`.

## Rollback
W tym samym YAML zmień jedynie `@experiment/v4.4-stale-irq-clear` na `@experiment/v4.1-fifo16`, następnie **Clean Build Files → Validate → Install → Wirelessly**.
