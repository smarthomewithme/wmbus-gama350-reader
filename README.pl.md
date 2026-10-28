# SHWM GAMA350 / Apator — stabilna v4.9 + diagnostyka v4.27

**Wersją radiową do codziennego używania jest v4.9.** Nie wgrywaj v4.27 tylko po to, aby zebrać logi. Nowa gałąź v4.27 zawiera **zewnętrzny analizator logów**, a kod CC1101 / ISR / FIFO i oryginalne osiem patchy pozostają bajt w bajt takie same jak w v4.9.

## Stabilna konfiguracja ESPHome

```yaml
external_components:
  - source: github://smarthomewithme/wmbus-gama350-reader@experiment/v4.9-stable-marcstate-eof
    refresh: always
    components:
      - wmbus_radio
      - wmbus_common
      - wmbus_meter
      - socket_transmitter
```

Zachowaj dotychczasową konfigurację ESP32, Wi-Fi, OTA, klucze AES i identyfikatory liczników.

## Nowa diagnostyka — bez ryzyka dla ESP32

Zapisz log w formacie tekstowym (z włączonymi istniejącymi komunikatami `CC1101: DEBUG`). Pobierz plik [scripts/analyze_v427.py](scripts/analyze_v427.py), a następnie na Windowsie z Pythonem 3.10+:

```powershell
py -3 .\analyze_v427.py --input "C:\Users\Public\gama-log.txt" --out "C:\Users\Public\gama-report"
```

Otrzymasz:
- `report.md`: liczba pełnych ramek, błędów 3of6, lista niezaobserwowanych okien 30 s;
- `gama_slots.csv`: każdy oczekiwany termin nadawania GAMA i jego zaobserwowany status;
- `errors_3of6.csv`: konkretne offsety i symbole błędów, RSSI, surowe LQI/FREQEST;
- `summary.json`: statystyki do automatycznego porównywania wersji.

Ważne: **niezaobserwowane okno nie musi oznaczać błędu odbiornika**. Mogło nie być transmisji, nie uzyskaliśmy synchronizacji albo log jest niekompletny. Przy braku pełnej ramki nie ma czego dekodować i nie znamy RSSI tej transmisji.

Instrukcja i ograniczenia: [v4.27 Passive Diagnostic](docs/V427_PASSIVE_DIAGNOSTICS.md). Raporty możesz również wysyłać w tej rozmowie bez instalowania Pythona.

Starsze 34 gałęzie zostały usunięte, 29 historycznych PR-ów zamknięto; zachowano wyłącznie `main`, stabilną v4.9 i diagnostyczną v4.27. Lista commitów starych gałęzi: [archiwum](docs/LEGACY_REF_ARCHIVE_20261028.json).
