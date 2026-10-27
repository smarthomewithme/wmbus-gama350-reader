# v4.7 — obserwacja luk GAMA350 wyłącznie z pętli ESPHome

**Status: eksperyment / Draft PR. Nie scalać do `main`. Brak automatycznej instalacji OTA.**

## Dlaczego osobna gałąź od v4.5

- Sprawdzona fizycznie v4.5 (`c95f692e3a8bb357730e91f58b2cd45eba8aa29c`): log 07:38–08:41, 97 kompletnych ramek 326 B, 84 poprawne GAMA, 355 Apator, zero `RX FIFO overflow`, `RXBYTES=65` i niestabilnych RXBYTES.
- Eksperyment v4.6 (09:00–09:12): 7 pełnych GAMA na 24 nominalne okna, 8 overflow, 38 `RXBYTES=65`, 5–10 niestabilnych odczytów RXBYTES podczas długich ramek. W pierwszych 10 min: 9 kandydatów na długą ramkę, 4 niekompletne odczyty; w czterech lukach nadal odbierano krótsze pakiety.
- Natychmiastowy powrót do v4.5 (09:15–09:23): 15 pełnych ramek na 17 okien (ok. 88%), 14 zdekodowanych GAMA, zero overflow i `RXBYTES=65`, wszystkie kompletne ramki `unstable_rxbytes=0`. To mocny sygnał regresji współwystępującej z v4.6, lecz nie dowód mechanizmu.

## Różnica implementacyjna

v4.7 jest **jednym dodatkowym patchem #0008 na oryginalnej gałęzi v4.5**, nie odziedzicza patcha v4.6. Zmienia wyłącznie `Radio::loop()`, dodaje pola odczytywane i aktualizowane **tylko z `loop()`** oraz czysty nagłówek obliczeniowy `loop_gap_observer.h`.

- Kod `Radio::receive_frame()`, `Radio::receiver_task()`, `wakeup_receiver_task_from_isr()`, transceiver CC1101, ISR, radio SPI, FIFO, GPIO, częstotliwość, próg FIFO16, restart RX, AES i dekoder pozostają **bajt w bajt takie same** jak w v4.5.
- W `loop()` co ~1000 ms próbkujemy **istniejące** atomowe `long_radio_frames_` i `payloads_ok_`; nie dodajemy żadnych atomowych liczników do tasku odbiorczego.
- Nowy wpis `RX_DIAG v4.7 loop_only ...` raz na 5 min zawiera `long_seen`, `short_ok_est` (`payloads_ok - long_radio_frames`), `gap_ge45s`, `missing_periods_est`, `gaps_with_short`, `max_gap_ms`.
- Wszystkie liczniki są kumulacyjne od uruchomienia ESP32; wartości odstępów mają dokładność około 1 s (lub gorszą, gdy pętla ESPHome jest opóźniona). `missing_periods_est` zakłada 30-sekundowe okresy nadawania i nie potwierdza nadania utraconych ramek. `short_ok_est` to odjęcie dwóch snapshotów atomowych i może chwilowo różnić się o jedną ramkę.
- Brak nowego klasyfikatora nieudanych długich payloadów: v4.7 nie może policzyć `long_read_fail` oddzielnie bez wejścia w krytyczne miejsce odbioru. Do porównania pozostają istniejące `payload_fail`, `header_fail` i logi CC1101.

## Weryfikacja i bezpieczny OTA

1. Pinned upstream `a732dd0e52c48973fad57e4950a11d8e2f2d6820` + dokładnie łatki #0001–#0007 z v4.5 i nowa #0008. Test natywny granic luk, test kontraktu izolacji kodu RX, test odświeżania cache, ASan/UBSan, offline ESPHome 2026.10.0 i bezpośredniego `github://`.
2. CI nie dotyka fizycznego urządzenia. Po zielonych testach świadomy OTA wykonuje właściciel: `Clean Build Files → Validate → Install → Wirelessly`, z możliwością rollbacku na `experiment/v4.5-isr-woken-init`.
3. Pierwsze 10–15 min pod nadzorem: sprawdzić czy wznowienie odbioru nie prowadzi do `Invalid RX FIFO count: 65`, overflow i `unstable_rxbytes`; następnie godzinny log z pięciominutowymi snapshotami. Jeśli nastąpi regresja, natychmiast wrócić do v4.5.

```yaml
external_components:
  - source: github://smarthomewithme/wmbus-gama350-reader@experiment/v4.7-loop-gap-observer
    refresh: always
    components:
      - wmbus_radio
      - wmbus_common
      - wmbus_meter
      - socket_transmitter
```

**Nie publikować publicznie jako stabilnego wydania i nie scalać do main przed fizycznym odbiorem.**
