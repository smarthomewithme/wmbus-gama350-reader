# CC1101 v4.2 — diagnostyka IRQ i nagłówków (GitHub OTA)

Ta gałąź eksperymentalna bazuje na sprawdzonym `experiment/v4.1-fifo16`. **Nie zmienia** częstotliwości, parametrów modemu, dekodowania 3-of-6, kodu AES, konfiguracji liczników, tempa SPI ani ścieżki opróżniania FIFO.

## Co dokładnie dodaje v4.2?

- Stempel czasu w ISR po zboczu GPIO4 (próg FIFO 16 B); w ISR nie ma logowania ani SPI.
- Jedna próbka `IRQ → tuż przed odczytem 3-bajtowego nagłówka` po wybudzeniu zadania. Raport co 5 minut. Taki pomiar obejmuje czas planowania zadania i przygotowanie obiektu pakietu, a nie dokładny czas pierwszego transferu po magistrali SPI.
- Przyczyny odrzucenia **3-bajtowego nagłówka**: `hdr_timeout_empty`, `hdr_timeout_partial`, `hdr_unstable`, `hdr_overflow`, `hdr_invalid_fifo`, `hdr_early_end`, `hdr_other`.
- `invalid_payload_length`: nagłówek odczytany, ale rozmiar ładunku odrzucony.
- Podsumowanie `RX_START_DIAG` wypisywane **raz na 5 minut**, obok istniejącego `RX_DIAG`. Liczniki nagłówków i błędów są narastające, a opóźnienia IRQ są liczone w 5-minutowym oknie.

Przykładowa struktura (wartości wyłącznie ilustracyjne):

```
RX_START_DIAG window_samples=... irq_to_read_avg_us=... irq_to_read_max_us=... irq_gt1000us=... stale_irq=... hdr_timeout_empty=... hdr_timeout_partial=... hdr_unstable=... hdr_overflow=... hdr_invalid_fifo=... hdr_early_end=... hdr_other=... invalid_payload_length=...
```

**Interpretacja:** IRQ na GPIO4 oznacza przekroczenie progu FIFO, niekoniecznie początek telegramu GAMA. Otrzymana próbka to czas od **ostatniego** zgłoszenia IRQ do chwili tuż przed odczytem nagłówka. Nie wykryje transmisji, która nigdy nie osiągnęła progu FIFO. `RX_DIAG header_fail` obejmuje także ramki inne niż GAMA.

## Test wieczorny przez ESPHome (bez pobierania repo)

Zachowaj swój YAML i wszystkie jego sekrety/sensory. Zmień tylko istniejące źródło komponentów:

```yaml
external_components:
  - source: github://smarthomewithme/wmbus-gama350-reader@experiment/v4.2-irq-header-diagnostics
    refresh: always
    components:
      - wmbus_radio
      - wmbus_common
      - wmbus_meter
      - socket_transmitter
```

Po zielonych testach GitHub Actions: w ESPHome wybierz `Clean Build Files → Validate → Install → Wirelessly`. W logu rozruchowym szukaj:

```
SHWM v4.1 FIFO16 experiment: RX threshold 16B (baseline 32B)
SHWM v4.2 IRQ/header diagnostics enabled; FIFO16 unchanged
```

Zostaw ograniczony logger: `CC1101: DEBUG`, `main: INFO`, `wmbus: INFO`, `packet: WARN`, `wmbusmeters: WARN`. Testuj 1–3 godziny z zamkniętą bramą. Zbierz wszystkie `RX_START_DIAG` i `RX_DIAG` oraz liczbę wiadomości GAMA i Apator, ewentualne `overflow`, `3of6 error` i `queue_drops`. Oceniamy skuteczność na podstawie czasu i szacunku nadawania co 30 sekund — nie uznajemy go za potwierdzoną liczbę emisji.

## Cofnięcie v4.2

Zmień tylko `@experiment/v4.2-irq-header-diagnostics` na `@experiment/v4.1-fifo16`, potem `Clean Build Files → Validate → Install → Wirelessly`. Nie trzeba przestawiać ani usuwać żadnych sensorów. Stabilne `main` pozostaje niezmienione.

## Bezpieczeństwo zmian

Nie podnosimy częstotliwości logowania, nie zapisujemy surowych telegramów, nie zmieniamy sposobu ponawiania RX i nie modyfikujemy wartości zmierzonego zużycia. Ta gałąź nie może trafić do `main` bez odbioru wyników fizycznego testu i świadomej akceptacji użytkownika.
