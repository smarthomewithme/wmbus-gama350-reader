# CC1101 v4.3 — pasywna diagnostyka nagłówków (test OTA przez GitHub)

## Dlaczego istnieje ta wersja
Wersja v4.1 FIFO16 przez 202 min przy zamkniętej bramie nie zgłosiła ani jednego przepełnienia FIFO i dekodowała 269 telegramów GAMA (szacunkowo 66,4% z 405 emisji).
Wersja v4.2 po instalacji zgłosiła 12 przepełnień w ok. 2 minuty. Po powrocie do v4.1 odbiór wrócił do normy. Dokładny mechanizm regresji **nie jest udowodniony**.

## Izolacja zmiany
v4.3 jest zbudowane z tej samej przypiętej wersji upstream i poprawek 0001–0005 co sprawdzone v4.1.
Względem v4.1 wprowadza wyłącznie:
- Lekkie przypisanie przyczyny w istniejących ścieżkach błędu `read_in_task`, bez dodatkowego odczytu SPI.
- Liczniki przyczyn nieudanego 3-bajtowego nagłówka: pusty timeout, częściowy timeout, niestabilne RXBYTES, overflow, nieprawidłowy FIFO count, przedwczesny koniec, inne.
- Oddzielny licznik odrzuconej długości payloadu.
- Jeden raport `RX_HEADER_DIAG cumulative ...` co 5 minut w istniejącym miejscu raportowania `RX_DIAG cumulative`.

**Nie ma pomiaru czasu w ISR, `esp_timer_get_time`, atomowych operacji w ISR ani zmiany funkcji budzenia zadania.**
Bez zmian pozostają: próg `FIFOTHR=0x03` (16 B), 868.950 MHz, filtr 325 kHz, GPIO/SPI, AES, GAMA/Apator, dekodowanie 3-of-6, buforowanie, normalny odczyt i opróżnianie FIFO.
Mimo małego zakresu zmiany jest to eksperyment — test CI nie dowodzi poprawnego zachowania sprzętu.

## ESPHome: bez terminala
Zmień **tylko istniejący wpis source** w `external_components` na:

```yaml
external_components:
  - source: github://smarthomewithme/wmbus-gama350-reader@experiment/v4.3-passive-header
    refresh: always
    components: [wmbus_radio, wmbus_common, wmbus_meter, socket_transmitter]
```

Po zielonych testach GitHub Actions wybierz w ESPHome: **Clean Build Files → Validate → Install → Wirelessly**.
Nie zmieniaj identyfikatorów liczników, sekretów, loggera ani pinów.
Oczekiwane logi:

```
SHWM v4.1 FIFO16 experiment: RX threshold 16B (baseline 32B)
SHWM v4.3 passive header diagnostics enabled; FIFO16 unchanged
RX_HEADER_DIAG cumulative hdr_timeout_empty=... hdr_timeout_partial=... hdr_unstable=... hdr_overflow=... hdr_invalid_fifo=... hdr_early_end=... hdr_other=... invalid_payload_length=...
```

Przez pierwsze 5 minut obserwuj szczególnie `RX FIFO overflow`, `Long RX: bytes=326`, odczyty GAMA i Apator. Jeżeli wystąpi powtarzający się overflow lub obydwa liczniki przestaną aktualizować pomiary, przerwij eksperyment — **nie zostawiaj takiej wersji na noc**.

## Powrót do działającego v4.1
Zmień tylko `@experiment/v4.3-passive-header` na `@experiment/v4.1-fifo16` i ponownie wybierz **Clean Build Files → Validate → Install → Wirelessly**.

## Warunki odbioru
- Od początku do końca zamknięta brama, bez przestawiania anteny ani zasilania.
- Przy poprawnych pierwszych 5 minutach zbierz 6 godzin logów (lub mniej, jeśli będzie regresja).
- Policz telegramy GAMA, Apator, 3-of-6, przepełnienia, `RX_DIAG` oraz `RX_HEADER_DIAG`.
- Odsetek transmisji GAMA pozostaje szacunkiem opartym na cyklu 30 sekund.
- **Brak scalania do `main` bez wyników testu i zgody użytkownika.** GitHub Actions niczego nie wgrywa na urządzenie.
