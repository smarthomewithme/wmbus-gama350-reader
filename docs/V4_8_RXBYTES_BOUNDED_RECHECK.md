# v4.8 — ograniczony retry nieprawidłowego RXBYTES (eksperyment)

**Status: Draft PR / bez scalenia do main / bez automatycznego OTA.** v4.8 startuje dokładnie z `experiment/v4.5-isr-woken-init` (`c95f692e3a8bb357730e91f58b2cd45eba8aa29c`). NIE zawiera v4.6 ani obserwatora v4.7.

## Dowody przed eksperymentem

- v4.5, log 03:18:36–06:45:36 (ok. 207 min): 415 nominalnych okresów 30 s, 292 kompletne ramki 326 B (~70,4%), 267 poprawnych dekodowań GAMA (~64,3%), 25 błędów 3of6 oraz 123 okresy bez kompletnej ramki. Log zawiera też ok. 900 wpisów `RX timeout after 0 bytes`, lecz nie dowodzi ich związku przyczynowego z brakującymi ramkami.
- v4.5, ponowny test bezpośrednio po rollbacku 09:47–09:56: 16 pełnych i 16 zdekodowanych GAMA, `bursts=31–33`, `peak_fifo=33–40`, `unstable_rxbytes=0`, bez `RXBYTES=65`, overflow i błędów nagłówków/payloadów.
- v4.7, próba 09:38–09:43: 9 kompletnych ramek, 8 dekodowań GAMA, 3 `Invalid RX FIFO count: 65`, `bursts=19–22`, `unstable_rxbytes=0–2`. CI 4/4 zielone, ale odbiór fizyczny nie przeszedł bramki. Sama korelacja nie ustala mechanizmu.
- Porównanie brakujących okresów v4.5 z czasami **zdekodowanych** ramek Apatora nie wykazało wyraźnej zależności. Nie wyklucza to kolizji z transmisjami, których nie odebrano.

## Dokładnie jedna zmiana w odbiorniku

Łatka #0008 dotyka jedynie ścieżki błędu `available > 64` w `CC1101::read_in_task()` oraz dodaje czysty, testowalny szablon `retry_invalid_fifo_count()` w istniejącym nagłówku `cc1101_fifo.h`.

- Gdy **wcześniej zatwierdzony** odczyt RXBYTES jest niedozwolony (>64 bez flagi overflow), wykonujemy maksymalnie **3** powtórne stabilizowane odczyty, z pauzą 60 µs pomiędzy próbami.
- Jeżeli któraś próba zwróci stabilną wartość 0–64 bez bitu overflow, zachowujemy ją i kontynuujemy normalną obsługę pozostałych bajtów. Nie logujemy podczas trwającej ramki; w poprawnie ukończonym długim telegramie `peak_fifo=65` może posłużyć jako znacznik odzyskania.
- Jeżeli trzy próby nie pomogą, nie czytamy FIFO na podstawie wadliwej wartości. Zachowujemy dotychczasowe ostrzeżenie i `return false`; wywołujący `Radio::receive_frame()` wykonuje istniejące `restart_rx()`.
- Flaga sprzętowego overflow (`0x80`) **nadal natychmiast kończy odbiór** poprzednią ścieżką. Nie jest maskowana ani interpretowana jako 65.
- Nie zmieniamy poprawnego przepływu, funkcji ISR, `Radio::receive_frame`, `Radio::loop`, GPIO, parametrów SPI/CC1101, FIFO16, 868.950 MHz, 325 kHz, dekodera, AES ani UDP. Żadnych nowych atomików lub okresowych odczytów rejestrów.
- Uwaga diagnostyczna: `peak_fifo` w odzyskanej ramce może zawierać początkowy błędny odczyt 65, ponieważ istniejący pomiar maksimum wykonuje się przed warunkiem wykrywania błędu. Nie należy interpretować go wtedy jako fizycznej zajętości 65 bajtów.

TI CC1101 datasheet i errata SWRZ020E wyjaśniają zarówno problem synchronizacji RXBYTES podczas odbioru, jak i zasadę nieopróżniania FIFO do zera przed końcem pakietu. Ta poprawka NIE zastępuje wcześniejszego zabezpieczenia `read_stable_rxbytes()`.

Źródła:
- https://www.ti.com/lit/ds/symlink/cc1101.pdf
- https://www.ti.com/lit/er/swrz020e/swrz020e.pdf

## Co ta wersja potrafi, a czego nie

Jest to **test hipotezy naprawy pojedynczych nieprawidłowych odczytów**, nie rozwiązanie wszystkich brakujących 123 okien ani 25 błędów 3of6. Jeśli v4.5 nie wygeneruje wartości >64, nowa gałąź będzie pracowała dokładnie tym samym logicznym torem odbioru, co baza. Brak zdarzeń retry nie będzie dowodem poprawy.

## Weryfikacja

1. Pinned upstream `a732dd0e52c48973fad57e4950a11d8e2f2d6820`, łatki #0001–#0007 identyczne jak v4.5, plus jedna nowa #0008; `git apply --check` i `git diff --check`.
2. Testy natywne przypadków: 65→35, odczyt niestabilny→overflow→64, trwałe 65 po trzech próbach, overflow od razu, poprawne 64 bez retry, poprawne 0 po retry. Kontrakt zmian tylko w dwóch plikach CC1101.
3. Cache/shim po odświeżaniu GitHuba, statyczne testy, kompilacja ESPHome 2026.10.0 oraz test bezpośredniego `github://`. CI nie dotyka urządzenia.
4. Wyłącznie po zielonym CI właściciel może zdecydować o ręcznym OTA; najpierw 10–15 min, potem porównanie co najmniej 60 min z v4.5 przy niezmienionym położeniu anteny. Sprawdzać `Invalid RX FIFO count`, `peak_fifo>64` po zakończonej długiej ramce, `RX FIFO overflow`, `unstable_rxbytes`, `bursts`, `3of6`, kompletne 326 B i skuteczne dekodowania. Każdy wyraźny regres — rollback do v4.5.

```yaml
external_components:
  - source: github://smarthomewithme/wmbus-gama350-reader@experiment/v4.8-rxbytes-bounded-recheck
    refresh: always
    components:
      - wmbus_radio
      - wmbus_common
      - wmbus_meter
      - socket_transmitter
```

**Nie instalować przed potwierdzeniem zakończenia CI. Nie publikować jako stabilne wydanie i nie scalać do main bez fizycznego odbioru.**
