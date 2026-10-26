# CC1101 v4 — instalacja, diagnostyka i wycofanie

## Status i zakres

Projekt publikuje oficjalny, powtarzalny **kandydat v4 do testów sprzętowych**. Działający v3 odebrał 39 poprawnych telegramów GAMA na około 60 oczekiwanych w 30 minut. v4 zachowuje tor odbioru v3 i filtr 325 kHz, ale dodaje diagnostykę oraz maskowanie kluczy AES przy starcie.

Nie jest to gwarancja odbioru wszystkich transmisji przy zamkniętej bramie.

## Przygotowanie

W terminalu Home Assistanta (repozytorium umieszczone w `/config/esphome/wmbus-gama350-reader`):

```bash
cd /config/esphome/wmbus-gama350-reader
git fetch origin
git switch main
git pull --ff-only origin main
bash scripts/prepare_cc1101_v4.sh
```

Skrypt odmówi nadpisania istniejącego `vendor/cc1101_v4`. Nie modyfikuje wgranego firmware ani YAML. Repo nie zawiera prywatnych kluczy.

Utwórz kopię **właściwego** YAML, zachowując zaszyfrowane ustawienia OTA i Wi-Fi:

```bash
mkdir -p /config/esphome/backups
cp -p /config/esphome/wmbus-reader.yaml \
  "/config/esphome/backups/wmbus-reader-$(date +%Y%m%d-%H%M%S).yaml"
```

Jeśli posiadasz sprawdzone firmware v3, zachowaj też jego `.bin`.

## Zmiana YAML (bez innych zmian)

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

W pliku YAML ma istnieć tylko jedna sekcja `external_components`. Nie zmieniaj pinów, parametrów CC1101, kluczy, częstotliwości, nazw sensorów ani przekazywania UDP. W ESPHome użyj **Clean Build Files → Validate → Install → Wirelessly** dopiero po sprawdzeniu zielonej kompilacji CI i utworzeniu kopii.

## Nowe komunikaty

Co 5 minut pojawia się zbiorcze `[wmbus] RX_DIAG cumulative` z polami:

- `irq_notifications` — liczba notyfikacji przerwania FIFO (nie liczba transmisji GAMA);
- `header_ok` / `header_fail` — udane i nieudane pobrania pierwszych trzech bajtów;
- `payload_ok` / `payload_fail` — ilości odbiorów po rozpoznaniu nagłówka, liczone dla wszystkich liczników;
- `long_radio_frames` — długie ramki odebrane przez radio, niezależnie od wyniku 3-of-6/CRC;
- `queue_drops` — utrata ramki przy kolejce.

Po kompletnym długim telegramie `[CC1101] RF_DIAG` wypisuje `freqest_raw` (wartość ze znakiem), `lqi_raw` i `marcstate`. To **chwilowe dane modemu przy odbiorze**, nie informacje o telegramach, które w ogóle nie wywołały przerwania. Zachowano `Long RX` i `Long frame 3of6 error` z v3.

W logu rozruchowym `Key: [REDACTED]` zastępuje surowy klucz AES. To nie usuwa klucza z wcześniejszych logów i nie anonimizuje surowych telegramów.

## Próba porównawcza

Zamknij bramę i zbieraj dane przez 30 minut bez restartu. Policz prawidłowe `Telegram otrzymany od licznika prądu!` oraz `Long RX`, błędy 3-of-6 i FIFO oraz odczyty Apatora. Nie interpretuj liczby `irq_notifications` jako liczby nadanych ramek przez GAMA. Przyjmij 30 s tylko jako zaobserwowany przybliżony okres.

Jeżeli odczyty się pogorszą, przywróć poprzedni YAML i wcześniejszy `.bin` przez OTA. Sam reboot **nie** przywróci poprzedniej wersji sterownika.

## Zasady publikacji

Nie przesyłaj publicznie pełnych logów debugowania przed usunięciem kluczy, identyfikatorów, adresów sieciowych i prywatnych danych pomiarowych. Kod zewnętrzny jest pobierany ze wskazanego upstream; jego licencja nie jest zastępowana licencją MIT tego projektu.

V4 oznacza oficjalnie opublikowany kod źródłowy i procedurę testową, a **nie** certyfikowany odbiornik czy gwarantowaną poprawkę RF.
