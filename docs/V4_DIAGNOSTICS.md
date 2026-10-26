# CC1101 v4 — instalacja i diagnostyka ESPHome

## Instalacja bez terminala

W ESPHome edytuj **istniejący plik YAML** swojego urządzenia, zachowując całą konfigurację. Zamień dotychczasową sekcję `external_components` na:

```yaml
external_components:
  - source: github://smarthomewithme/wmbus-gama350-reader@main
    components: [wmbus_radio, wmbus_common, wmbus_meter, socket_transmitter]
```

Zapisz, wybierz **Clean Build Files**, następnie **Validate** i **Install → Wirelessly**. Nie zmieniaj kluczy AES, GPIO, SPI, częstotliwości 868.950 MHz, sensorów ani automatyzacji. Zachowaj kopię działającego YAML i poprzedni firmware, aby móc cofnąć zmianę.

ESPHome podczas pierwszej walidacji sam pobierze kod SzczepanLeona w wersji przypiętej do SHA, nałoży cztery poprawki i skompiluje komponenty. Z tego powodu pierwsza walidacja wymaga internetu i może trwać dłużej.

## Diagnostyka po OTA

**Brama zamknięta, 30 minut bez restartowania ESP32.** W logach liczymy:
- `Telegram otrzymany od licznika prądu!` — poprawne odczyty GAMA;
- `Long RX: bytes=326` — odebrane przez radio pełne ramki;
- `Long frame 3of6 error` — uszkodzone symbole;
- `RX FIFO overflow` i `RX timeout` — nieudane odbiory;
- `Telegram otrzymany od licznika wody!` — regresje Apatora;
- `RX_DIAG cumulative` — co pięć minut łączna liczba przerwań, sukcesów i niepowodzeń podczas czytania nagłówków, payloadów i kolejki;
- `RF_DIAG` — `freqest_raw`, `lqi_raw`, `marcstate` po odebraniu długiej ramki.

**Nie utożsamiaj liczby przerwań GPIO4 z liczbą rzeczywistych telegramów GAMA.** Mierzy zdarzenia progu FIFO CC1101. Nie jest to sprzętowy licznik wszystkich transmisji.

W logach rozruchowych v4 powinien pojawić się komunikat `Key: [REDACTED]`. Nie publikuj starych logów, w których komponent wypisywał AES jawnie. Także inne logi DEBUG mogą zdradzać dane pomiarowe i adresy sieciowe.

## Przywrócenie wcześniejszej wersji

W edytorze ESPHome przywróć zapisaną sekcję `external_components` i wcześniejszy YAML, następnie wybierz **Clean Build Files → Validate → Install → Wirelessly**. Gdy dysponujesz poprzednim `.bin`, można go wgrać przez obsługiwany interfejs OTA. Sam restart urządzenia **nie** zmienia wersji firmware.

## Dlaczego pobieramy kod przy walidacji?

Główne repozytorium nie publikuje kopii komponentów autora ani bibliotek `wmbusmeters`. Kod pochodzi z [SzczepanLeon/esphome-components](https://github.com/SzczepanLeon/esphome-components) i jest pobierany automatycznie w dokładnej wersji `a732dd0e52c48973fad57e4950a11d8e2f2d6820`, po czym nakładane są cztery publiczne poprawki. To rozwiązanie spełnia wymaganie bezterminalowej instalacji i zachowuje prawa oryginalnych autorów.

## Status

V3 miało 39 poprawnych odczytów na około 60 oczekiwanych w 30 minut oraz 161 poprawnych telegramów Apatora przy zamkniętej bramie. V4 nie zmienia filtra 325 kHz i wnosi diagnostykę oraz redakcję sekretów; **wyniki v4 na fizycznym ESP32 pozostają do weryfikacji**.

### Opcjonalnie dla deweloperów

Skrypt `scripts/prepare_cc1101_v4.sh` umożliwia izolowany build lokalny, ale **nie jest wymagany do normalnej instalacji**.
