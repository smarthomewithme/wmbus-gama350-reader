# wMBus GAMA 350 Reader — ESP32 + CC1101

**Oficjalne publiczne repozytorium kodu · v4 (wersja diagnostyczna, test na sprzęcie jeszcze przed nami).**

[English README](README.md) · [Instrukcja v4](docs/V4_DIAGNOSTICS.md) · [Testy](docs/TEST_PLAN.md)

Projekt umożliwia odczyt GAMA 350 (`amiplus`) i wodomierza Apator (`apatorna1`) w ESPHome/Home Assistant. Zamiast publikowania pełnego kodu zewnętrznego autora, repozytorium pobiera przypiętą wersję jego komponentów i nakłada sprawdzone, jawne poprawki.

## Co jest potwierdzone

**V3 działa na fizycznym ESP32.** W półgodzinnym logu z zamkniętą bramą GAMA poprawnie odczytano **39 razy na około 60 oczekiwanych transmisji**, odebrano 41 pełnych ramek 326 B, z czego dwie miały błąd 3-of-6. Apator został poprawnie zdekodowany 161 razy. Oznacza to, że dekoder energii działa, ale odbiór GAMA nadal nie jest stuprocentowy.

**V4 to diagnostyka na bazie v3**, bez zmiany pasma filtra (pozostaje 325 kHz), pinów, kluczy i konfiguracji modemu. Dodaje raport statystyk etapu odbioru co pięć minut, `FREQEST/LQI/MARCSTATE` po odebraniu długiej ramki oraz zasłania klucze AES w logach startowych.

V4 nie ma jeszcze potwierdzonej skuteczności na sprzęcie — zielony build nie zastępuje testu przy zamkniętej bramie.

## Instalacja (oficjalny kod z main)

```bash
cd /config/esphome/wmbus-gama350-reader
git fetch origin
git switch main
git pull --ff-only origin main
bash scripts/prepare_cc1101_v4.sh
```

Źródła powstaną w `vendor/cc1101_v4/components`. Skrypt nie nadpisuje istniejących katalogów ani firmware. **Najpierw zachowaj kopię działającego YAML i pliku firmware v3.**

W istniejącym `wmbus-reader.yaml` podmień wyłącznie sekcję:

```yaml
external_components:
  - source:
      type: local
      path: /config/esphome/wmbus-gama350-reader/vendor/cc1101_v4/components
    components:
      - wmbus_radio
      - wmbus_common
      - wmbus_meter
      - socket_transmitter
```

Nie podmieniaj całego YAML przykładową konfiguracją z repozytorium. Zachowaj dotychczasowe ID liczników, klucze AES, ESP32 GPIO18/19/23 (SPI), GPIO15 (CS), GPIO4 (IRQ), częstotliwość 868,950 MHz, API, Wi-Fi i UDP.

Po utworzeniu kopii użyj ESPHome **Clean Build Files → Validate → Install → Wirelessly**. Nic w GitHub Actions nie wgrywa firmware na urządzenie.

## Jak interpretować v4

- `RX_DIAG` — skumulowane liczniki przerwań, odebranych nagłówków i ramek, błędów i strat w kolejce. **Przerwanie nie oznacza poprawnego telegramu GAMA**.
- `RF_DIAG` — stan modemu (`freqest_raw`, `lqi_raw`, `marcstate`) po odebraniu długiej ramki; nie wykrywa brakujących transmisji.
- `Long RX`, `Long frame 3of6 error`, `RX FIFO overflow` — diagnostyka zachowana z v3.
- `Key: [REDACTED]` — klucz AES nie jest wyświetlany w logu rozruchowym v4.

Pełna procedura testowa i powrót do poprzedniej wersji: [docs/V4_DIAGNOSTICS.md](docs/V4_DIAGNOSTICS.md).

## Licencje i prywatność

Własne skrypty, testy, dokumentacja i poprawki na licencji MIT. Upstream [SzczepanLeon/esphome-components](https://github.com/SzczepanLeon/esphome-components) jest pobierany osobno z dokładnego commita; jego licencja i prawa autorów nie są przejmowane przez licencję tego repozytorium. Część zależności ma odrębne warunki, m.in. GPL.

Nigdy nie publikuj prawdziwych kluczy AES, danych API/OTA, `secrets.yaml` ani niezredagowanych logów ESPHome. Starsze wydania komponentu drukowały klucze przy uruchamianiu — publiczne skopiowane logi trzeba traktować jako wrażliwe.

To projekt społecznościowy do **odczytu** telegramów radiowych, nie rozwiązanie certyfikowane do rozliczeń energii.
