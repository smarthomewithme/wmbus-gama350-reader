# wMBus GAMA 350 Reader — ESP32 + CC1101

Odczyt licznika GAMA 350 i wodomierza Apator przez ESPHome / Home Assistant.

**Oficjalny wariant v4: instalacja prosto z GitHuba. Bez terminala, pobierania repozytorium, ręcznego nakładania poprawek czy kopiowania plików.**

[English README](README.md) · [Diagnostyka i przywracanie](docs/V4_DIAGNOSTICS.md) · [Źródła SzczepanLeona](https://github.com/SzczepanLeon/esphome-components)

## Instalacja w ESPHome — jedyna zmiana w YAML

W edytorze istniejącego urządzenia ESPHome znajdź sekcję `external_components` i **zastąp ją** następującą:

```yaml
external_components:
  - source: github://smarthomewithme/wmbus-gama350-reader@main
    components: [wmbus_radio, wmbus_common, wmbus_meter, socket_transmitter]
```

Zapisz konfigurację i użyj **Validate → Install → Wirelessly**. Gdy przechodzisz z innej wersji komponentów, najpierw wybierz **Clean Build Files**. Przed pierwszym OTA zachowaj kopię obecnego YAML i działającego firmware.

Nie zmieniaj istniejących pinów, częstotliwości radia, kluczy AES, identyfikatorów liczników, sensorów, automatyzacji ani UDP. Nie podmieniaj własnej konfiguracji plikiem demonstracyjnym z repozytorium.

**To wszystko.** ESPHome samo pobiera i przygotowuje komponenty podczas walidacji. Pierwsza walidacja może potrwać dłużej; serwer ESPHome musi mieć dostęp do GitHuba. Testowane wydanie ESPHome: 2026.10.0.

## Co robi instalacja automatycznie?

W repozytorium są małe komponenty instalacyjne, które pobierają kod autora z dokładnego commita `a732dd0e52c48973fad57e4950a11d8e2f2d6820`, nakładają poprawki `0001–0004` i udostępniają wynik kompilatorowi ESPHome. Nie trzeba do tego terminala.

Nie rozpowszechniamy bezpośrednio cudzego kodu ze względu na prawa autorów i odrębne licencje bibliotek `wmbusmeters`. Kod jest pobierany z pierwotnego źródła na urządzeniu, na którym kompilujesz firmware.

## Co już działa?

**V3 zostało przetestowane fizycznie:** przez około 30 minut poprawnie odczytano 39 telegramów GAMA (około 65% oczekiwanych), odebrano 41 pełnych ramek 326 B i poprawnie zdekodowano 161 telegramów Apatora. Nie jest to 100% niezawodności.

**V4 zachowuje działający tor radiowy v3** (filtr 325 kHz) i dodaje:
- `RX_DIAG` co 5 minut — liczba notyfikacji przerwań, poprawnych nagłówków, odczytów danych i błędów;
- `RF_DIAG` — `FREQEST`, `LQI`, `MARCSTATE` po odebraniu długiej ramki;
- `Key: [REDACTED]` — brak jawnego klucza AES w logu konfiguracji.

**Odbiór v4 nie jest jeszcze przetestowany na fizycznym CC1101.** Zaliczenie testów i kompilacji nie zastępuje pomiaru jakości odbioru przy zamkniętej bramie.

## Bezpieczeństwo i licencje

Zachowaj prywatność identyfikatorów liczników i kluczy. Starsze wydania mogły ujawniać klucz AES w logach startowych. Nawet v4 na poziomie DEBUG może wypisywać prywatne odczyty pomiarowe.

Nasze pliki i poprawki są na licencji MIT. Część kodu zewnętrznego ma odrębne warunki, m.in. GPL; ten projekt ich nie zmienia.

Szczegóły testowania oraz przywrócenia poprzedniej wersji: [docs/V4_DIAGNOSTICS.md](docs/V4_DIAGNOSTICS.md).

### Dla programistów

`scripts/prepare_cc1101_v4.sh` nadal służy do ręcznego budowania izolowanej kopii źródeł, ale **zwykły użytkownik ESPHome nigdy nie musi go uruchamiać**.
