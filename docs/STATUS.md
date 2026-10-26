# Status projektu — 26.10.2026

Priorytet: odbiór pełnych telegramów GAMA 350 przez CC1101 z deszyfrowaniem amiplus i publikacją kWh, taryf oraz mocy do Home Assistant. Apator musi nadal działać.

## Fakty z dotychczasowej diagnostyki

- ESP32 DevKit i CC1101, 868.950 MHz, GPIO18/23/19, CS15, IRQ4.
- Odbiór Apator T1 działa stabilnie; krótkie ramki przechodzą dekodowanie.
- GAMA 350 nadaje długie pakiety, w logach około 326 bajtów, lecz w dalszej części transmisji występują błędne symbole 3-of-6.
- Pierwsze 20 bajtów surowego telegramu daje poprawny nagłówek i CRC. Publiczna próbka ma zmieniony numer licznika i przeliczony CRC.
- Downgrade, Clean Build i próby zmiany warunków radiowych nie przywróciły GAMA.
- SzczepanLeon/esphome-components main z 24.10.2026: a732dd0e52c48973fad57e4950a11d8e2f2d6820.
- PR #345 i #407 są scalone; #420 potwierdza działający GAMA 350 z CC1101; #453 dokumentuje podobną usterkę długich ramek.

## Kandydackie poprawki

1. Bezpieczne ustalenie wskaźnika i pojemności Packet przed wywołaniem read_in_task().
2. Kontrola granic w decode3of6() dla trzybajtowego nagłówka.
3. Ochrona ostatniego bajtu RX FIFO i ponowna kontrola RXBYTES przy opróżnianiu końcowego fragmentu.

## Ograniczenia

Testy komputerowe oraz model FIFO nie zastępują potwierdzenia na ESP32. Brak pełnego oryginalnego telegramu 326 B oraz kompletnej surowej ramki Apatora. ESPHome nie został jeszcze pomyślnie skompilowany i sprawdzony na tym urządzeniu z proponowaną poprawką.

Za rozwiązanie uznajemy co najmniej 20 poprawnych telegramów GAMA 350 z CRC wszystkich bloków, prawidłowo działające kWh/taryfy/moc oraz nieprzerwany odczyt Apatora.
