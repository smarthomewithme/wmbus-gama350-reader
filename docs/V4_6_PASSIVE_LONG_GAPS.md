# v4.6 — pasywna diagnostyka przerw w odbiorze długich ramek CC1101

**Draft eksperymentalny. Nie scalać do main i nie instalować przed zielonym CI oraz świadomą decyzją właściciela.**

## Bazowa obserwacja fizyczna (v4.5, 27.10.2026)

Log 07:38:22–08:41:45 (63 min 23 s): 97 pełnych ramek 326 B, 84 poprawnie zdekodowane telegramy GAMA (~66,7% z ~126 oczekiwanych transmisji co 30 s), 13 błędów 3of6, 355 telegramów Apator, 7 pustych timeoutów nagłówka, **0 RX FIFO overflow, 0 unstable_rxbytes, 0 RXBYTES=65, 0 queue_drops**. W pierwszych 25 min 11 błędów 3of6/40 pełnych ramek przy średnim RSSI -75,1 dBm; w kolejnych ~38 min 2/57 przy lepszym RSSI. Wskazuje to na możliwy wpływ warunków radiowych, nie dowodzi błędu ISR.

## Dokładnie co zmienia v4.6

Jedna kolejna łatka `patches/0008-v4_6-passive-long-gap-diagnostics.patch` na dokładnie bazowej v4.5 `c95f692e3a8bb357730e91f58b2cd45eba8aa29c`:

- `long_candidates`: po poprawnym nagłówku znana oczekiwana długość payloadu >=250 B; **to nie potwierdza identyfikatora GAMA**.
- `long_read_fail`: kandydat >=250 B, którego payloadu radio nie przeczytało w całości.
- `short_radio_frames`: poprawnie odczytane ramki krótsze niż 250 B, niekoniecznie zdekodowane jako Apator.
- `gap_ge45s`: liczba przerw >=45 s między **kompletnymi** długimi ramkami RF.
- `missing_periods_est`: przybliżenie liczby brakujących okresów 30 s z tych przerw (zaokrąglenie odstępu, minus odebrana ramka). Nie dowodzi, że licznik naprawdę nadał.
- `gaps_with_short`: w ilu takich przerwach co najmniej jedna krótka ramka nadal została poprawnie odebrana — rozróżnia ciszę całego toru RF od braku długich ramek.
- `max_gap_ms`: największa zaobserwowana przerwa w ms.

Nowa linia `RX_DIAG v4.6 ...` pojawia się co 5 minut w zwykłym `Radio::loop()`, obok istniejącego `RX_DIAG cumulative`. Wszystkie liczniki są **narastające od bootu**; analizować przyrosty między kolejnymi pięciominutowymi odczytami.

Nie dodano logowania w ISR, odczytów statusu CC1101, transakcji SPI ani aktywnego próbkowania radia. Nie zmieniono GPIO, 868,950 MHz, filtrów, 325 kHz BW, FIFO16, czasów odbioru, AES, kolejki, dekodera, algorytmu restartu RX ani wysyłki Home Assistant/UDP. Mała ilość dodatkowej pracy CPU w zadaniu odbiorczym (atomowe liczniki, `millis()` raz na pełną długą ramkę) **może jednak zmienić timing**; dlatego wymaga fizycznej weryfikacji.

## Jak odczytywać wyniki

- `long_candidates > long_radio_frames` i `long_read_fail > 0`: część wykrytych długich ramek ginie **podczas** odczytu payloadu.
- `long_candidates ≈ long_radio_frames`, a `missing_periods_est` rośnie: braki następują **przed uzyskaniem pełnego rozpoznanego nagłówka** albo sygnału w ogóle nie odebrano; sam licznik nie rozstrzyga zakłóceń, kolizji czy braku transmisji.
- `gaps_with_short > 0`: odbiornik nadal pracował i zbierał krótkie RF w czasie części luk. To **nie** dowodzi, że konkretną ramkę GAMA dało się odebrać.
- Błędy 3of6 oznaczają *kompletną* ramkę radiową, ale niepoprawną treść; rozliczać je niezależnie od `long_read_fail`.
- Pierwsza dłuższa przerwa liczona jest dopiero po odebraniu pierwszej pełnej długiej ramki; nie wykrywa nieobecności od startu. Suma estymowanych braków zależy od założenia okresu 30 sekund.

## Bramki CI i odbiór fizyczny

1. Pinned upstream `a732dd0e52c48973fad57e4950a11d8e2f2d6820`; `git apply --check` wszystkich ośmiu łatek; nienaruszone bootstrap shims.
2. Test natywny granic matematyki luk (`tests/v46_gap_math.cpp`), testy ASan/UBSan, test bootstrapa po `refresh: always`.
3. Build ESPHome **2026.10.0** z odizolowanego źródła i bezpośredniego `github://`, bez fizycznego urządzenia w CI.
4. Dopiero po PASS: właściciel może przetestować OTA w ESPHome GUI, najpierw 10–15 min pod nadzorem, później ~1 h pełnych logów.
5. Porównać procent `GAMA decoded / oczekiwane`, pełne 326B, 3of6, Apator, FIFO overflow, timeouty, nowy `RX_DIAG v4.6`; nie scalać do main bez decyzji właściciela.

### Źródło do ESPHome — **dopiero po zatwierdzeniu testu OTA**

```yaml
external_components:
  - source: github://smarthomewithme/wmbus-gama350-reader@experiment/v4.6-passive-long-gaps
    refresh: always
    components:
      - wmbus_radio
      - wmbus_common
      - wmbus_meter
      - socket_transmitter
```

`Clean Build Files → Validate → Install → Wirelessly`. Nie zastępować pozostałego YAML.

**Rollback**: `@experiment/v4.5-isr-woken-init` (obecna testowana wersja), ewentualnie `@experiment/v4.4-stale-irq-clear` lub stabilna `@experiment/v4.1-fifo16`. Żadna operacja CI nie wysyła firmware do urządzenia.
