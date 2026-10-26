# wMBus GAMA 350 Reader — instrukcja po polsku

**Stan na 26 października 2026: wersja eksperymentalna, niepotwierdzona na fizycznym ESP32.**

Celem projektu jest poprawny odczyt licznika energii elektrycznej GAMA 350 w Home Assistant. Na początek pracujemy wyłącznie nad GAMA 350 / CC1101 / ESP32, zachowując działający wodomierz Apator. Docelowo repozytorium będzie obsługiwać więcej liczników i odbiorników radiowych.

## Ustalenia

- ESP32 DevKit / ESP-IDF / ESPHome 2026.10.0.
- SPI: SCK `GPIO18`, MOSI `GPIO23`, MISO `GPIO19`, CS `GPIO15`, IRQ `GPIO4`.
- Częstotliwość 868,950 MHz.
- GAMA 350: `amiplus`, ID `0x12345678` (przykładowy), tryby `T1/C1`, pakiety około 326 bajtów, sensory energii i mocy pozostają `N/A`.
- Apator: `apatorna1`, ID `0x87654321` (przykładowy), `T1`, wodomierz działa. NIE zmieniamy pinów i nie ryzykujemy utraty odczytu wody.
- Nagłówek GAMA po dekodowaniu 3-of-6: `BE44ED14785634120102242A7A`. CRC pierwszego bloku: `242A`.
- Poprawki w tym repo są kandydatami. Nie potwierdzono jeszcze dekodowania pełnej ramki na urządzeniu.

## Co przygotowano

- Przypięcie kodu źródłowego SzczepanLeona do dokładnego SHA `a732dd0e52c48973fad57e4950a11d8e2f2d6820`, zamiast ruchomego `@main`.
- Skrypt pobierający ten commit i nakładający małą poprawkę na trzy pliki źródłowe.
- Konfigurację demonstracyjną ESPHome z GAMA 350 i Apatorem, z kluczami przechowywanymi poza GitHubem.
- Testy C++ (w tym AddressSanitizer) i model odczytu FIFO dla pakietów 53/326/430 bajtów.
- Plan weryfikacji sprzętowej, metryki sukcesów i sposób rollbacku.

## Instrukcja — Windows PowerShell

Po utworzeniu lokalnego katalogu projektu i wejściu do niego:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\prepare_sources.ps1
Copy-Item .\config\secrets.example.yaml .\config\secrets.yaml
# Następnie UZUPEŁNIJ config\secrets.yaml swoim Wi-Fi, API, OTA i kluczami AES.
# Na komputerze z ESPHome 2026.10.0:
esphome config .\config\wmbus-gama350.yaml
esphome compile .\config\wmbus-gama350.yaml
```

**To tylko przygotowanie i kompilacja. Nic nie wgrywa się na ESP32.** Nigdy nie wysyłaj `secrets.yaml` ani kluczy AES do publicznego repo.

**UWAGA:** przykładowy YAML nie zawiera konfiguracji przekazywania ramek przez `socket_transmitter`/UDP. Jeśli jest używana, należy zachować jej dotychczasowe ustawienia i scalić zmiany z istniejącą konfiguracją.

## Przed testem OTA

1. Zachowaj obecną działającą konfigurację i firmware, aby móc cofnąć zmianę.
2. Upewnij się, że `git` wskazuje dokładny commit i lokalnie nałożoną poprawkę (`git -C vendor/upstream diff --stat`).
3. Sprawdź kompilację ESPHome oraz stabilność Apatora.
4. Po **osobnej zgodzie** na flash monitoruj odczyty GAMA i wody oraz pełne CRC.

Szczegóły: [Plan testów](docs/TEST_PLAN.md) i [Aktualny stan](docs/STATUS.md).

## Status licencji

Repo publikuje tylko własne pliki, testy, instrukcje i niewielkie poprawki. Nie zawiera kopii kompletnego `esphome-components`. Samo repo autora nie ma rozpoznanej licencji GitHub, chociaż wybrane pliki driverów zawierają GPL-3.0-or-later. MIT w tym projekcie dotyczy tylko naszego kodu.