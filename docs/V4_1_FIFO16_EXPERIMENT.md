# CC1101 v4.1 — eksperyment FIFO16 (nie jest wydaniem stabilnym)

## Zakres eksperymentu

Na gałęzi `experiment/v4.1-fifo16` zmieniamy **wyłącznie próg RX FIFO** w układzie CC1101:

- v4 `FIFOTHR=0x07`: IRQ gdy w FIFO jest 32 B;
- v4.1 `FIFOTHR=0x03`: IRQ gdy w FIFO jest 16 B.

Pozostawiamy bez zmian: `868.950 MHz`, `MDMCFG4=0x5C` (filtr 325 kHz), SPI, wejście IRQ GPIO4, mechanizm 3-of-6, AES, dekodery GAMA i Apator, harmonogram logowania oraz sposób obsługi ramki. Zmiana progu może wywoływać więcej powiadomień IRQ, lecz pozwala na wcześniejsze rozpoczęcie opróżniania FIFO.

Uwaga: `RXBYTES=65` nie jest automatycznie dowodem błędnego odczytu SPI. Dokument TI SWRZ020E opisuje dodatkowy bufor prefetch, przez który rejestr może pokazać wartość 65. W tym kontrolowanym eksperymencie **nie zmieniamy** zachowania związanego z takimi wskazaniami, aby izolować wpływ progu.

## Instalacja tylko przez ESPHome GUI

W istniejącym YAML podmień **tylko** sekcję źródła:

```yaml
external_components:
  - source: github://smarthomewithme/wmbus-gama350-reader@experiment/v4.1-fifo16
    refresh: always
    components: [wmbus_radio, wmbus_common, wmbus_meter, socket_transmitter]
```

Nie wklejaj przykładowego YAML zamiast własnych identyfikatorów liczników, sekretów, sensora, SPI ani GPIO.

W ESPHome: **Clean Build Files → Validate → Install → Wirelessly**. To jest OTA wykonywane na urządzeniu dopiero przez użytkownika, a nie przez GitHub Actions. Po uruchomieniu poszukaj linii:

```
SHWM v4.1 FIFO16 experiment: RX threshold 16B (baseline 32B)
```

Jeżeli jej nie ma, nie zakładaj, że eksperyment jest aktywny.

## Procedura A/B

1. Zachowaj stabilne v4 i poprzedni log. Ostatni test v4: około 51/101 poprawnych transmisji GAMA przez ~51 minut przy ograniczonym DEBUG; 184 Apator, 27 overflow i 35 raportów `Invalid RX FIFO count: 65`. Liczba 101 jest **szacunkiem** (cykl 30s), nie sprzętowym licznikiem TX.
2. Utrzymaj te same położenie/antenę, zamkniętą bramę, warunki zasilania i poziomy loggera (`CC1101: DEBUG`, `main: INFO`, `wmbus: INFO`, `packet: WARN`, `wmbusmeters: WARN`).
3. Zbierz 30–60 minut po OTA, bez restartowania urządzenia podczas testu.
4. Raportuj poprawne `Telegram otrzymany od licznika prądu!`, `Long RX: bytes=326`, błędy `Long frame 3of6 error`, `RX FIFO overflow`, `Invalid RX FIFO count: 65`, `RX_DIAG cumulative` i odczyty Apatora.
5. Porównaj w przeliczeniu na czas, a nie tylko bezwzględną liczbę wiadomości; pojedynczy eksperyment nie dowodzi jednoznacznie poprawy w różnych warunkach radiowych.

## Powrót do stabilnego v4

W tym samym miejscu YAML podmień tylko `@experiment/v4.1-fifo16` z powrotem na `@main`, zachowując `refresh: always`. Zastosuj **Clean Build Files → Validate → Install → Wirelessly**.

Ograniczenia: GitHub Actions potwierdza źródła i kompilację, lecz nie testuje fizycznego CC1101. Gałąź jest eksperymentalna; nic nie jest scalane do `main` przed testem urządzenia.
