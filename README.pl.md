# wM-Bus GAMA350 + Apator — ESPHome / Home Assistant

**Stabilny odbiornik v4.9 (ESP32 + CC1101).** Zweryfikowany na rzeczywistym sprzęcie z ESPHome 2026.10.1, 29 października 2026. Kod radiowy (osiem poprawek) pozostaje zamrożony po testach. GAMA350 wykorzystuje dekoder `amiplus`, a wodomierz `apatorna1`.

## Instalacja

W istniejącej konfiguracji ESPHome użyj:

```yaml
external_components:
  - source: github://smarthomewithme/wmbus-gama350-reader@main
    components: [wmbus_radio, wmbus_common, wmbus_meter, socket_transmitter]
```

W sekcji `wmbus_radio` ustaw dla sprawdzonego stanowiska częstotliwość `868.970MHz`; odpowiednia częstotliwość może zależeć od lokalnej instalacji. Nie zmieniaj swoich pinów, identyfikatorów liczników, ustawień Wi-Fi, API, OTA ani kluczy. Przed aktualizacją zrób kopię YAML i działającego firmware. Dla starszego cache wybierz **Clean Build Files**, a następnie Validate i Install.

[Przykładowy YAML (wyłącznie dane zastępcze)](config/wmbus-gama350.yaml) · [Szablon secrets](config/secrets.example.yaml) · [English](README.md)

**Uwaga:** przykład nie jest kopią prywatnej konfiguracji urządzenia. Wszystkie prawdziwe wartości przechowuj w `secrets.yaml` poza GitHubem.

## Kod źródłowy i pochodzenie

- Sprawdzona baza radiowa: commit `11b09de7f87ade632453f772c37940dbdb470c94` (v4.9).
- Oryginalne komponenty: [SzczepanLeon/esphome-components](https://github.com/SzczepanLeon/esphome-components), przypięty commit `a732dd0e52c48973fad57e4950a11d8e2f2d6820`.
- Bootstrap pobiera źródła upstream i aplikuje dokładnie osiem poprawek `patches/0001–0008`. Nie wymaga ręcznego klonowania.
- Ścieżka odbioru 326-bajtowych ramek GAMA została przetestowana; Apator zachowuje obsługę krótkich telegramów.
- Pliki `tests/` i `.github/workflows/` pomagają sprawdzać integralność kompilacji, ale testy komputerowe nie zastępują pomiarów radiowych.

## Wyniki i ograniczenia

W testach z odbiornikiem zamocowanym na ścianie (około 80 cm) obie częstotliwości 868.950 i 868.970 MHz pozwalały poprawnie dekodować około 99% **kompletnie odebranych** ramek GAMA350. Nie oznacza to 99% wszystkich nadanych telegramów; bez drugiego odbiornika nie można zmierzyć rzeczywistej utraty transmisji. Ostatecznie wybrano 868.970 MHz, bez wykazanej istotnej przewagi skuteczności dekodowania.

## Bezpieczeństwo i licencje

Nie publikuj haseł Wi-Fi, kluczy API/OTA/AES, identyfikatorów liczników ani rzeczywistych logów pomiarowych. Startowe logi tej wersji ukrywają klucz AES jako `[REDACTED]`; inne logi DEBUG nadal mogą zawierać prywatne dane. Własne pliki i poprawki są na licencji MIT; pobierany kod upstream zachowuje własne licencje. Zobacz [SECURITY.md](SECURITY.md) i [LICENSE](LICENSE).

To społecznościowy odbiornik odczytowy, a nie urządzenie certyfikowane do rozliczeń.
