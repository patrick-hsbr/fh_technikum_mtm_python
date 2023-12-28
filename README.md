# OptimistPrime Trader im Python Kurs der FH Technikum

Dieses Skript ist ein automatisierter Tradingbot, der die Binance API verwendet, um Kursdaten für verschiedene Kryptowährungen abzurufen, Handelsentscheidungen basierend auf einer Strategie zu treffen und Kauf-/Verkaufsaufträge an Binance zu schicken.

## Pakete importieren

Zu Beginn des Skripts werden alle erforderlichen Python-Pakete importiert, die für den reibungslosen Betrieb des Bots benötigt werden. Hier sind die wichtigsten Pakete und ihre Verwendungszwecke. Die aktuellen Version zur Installation sind unter requirements.txt zu finden:

- **logging**: Dieses Paket wird für das Logging von Meldungen während der Ausführung des Skripts verwendet, um Fehler leichter zu erkennen und zu beheben.
- **binance.client**: Der Binance API-Client ermöglicht die Abfrage von Kursdaten und die Ausführung von Kauf- und Verkaufsaufträgen.
- **pandas as pd**: Pandas wird verwendet, um die erhaltenen Kursdaten in DataFrames zu manipulieren, insbesondere für die Arbeit mit Tabellenstrukturen.
- **json**: Hiermit können Konfigurationsdaten aus der Datei "config.json" geladen werden, in der API-Schlüssel gespeichert sind.
- **pandas_ta as ta**: Dieses Paket ermöglicht die Anwendung von technischen Analyseindikatoren auf Pandas DataFrames. Hier wird der MACD-Indikator berechnet, der als Grundlage für Handelssignale dient.
- **time**: Es wird verwendet, um Verzögerungen zwischen den Iterationen einzuführen, um die Ausführung der Hauptschleife zu steuern.
- **pytz**: Dieses Paket wird verwendet, um mit Zeitzonen zu arbeiten und Zeitstempel in die gewünschte Zeitzone zu konvertieren.
- **csv**: Hiermit können Informationen über Kauf- und Verkaufsaufträge in eine CSV-Datei geschrieben werden, die als Art Orderbuch fungiert.

## Logging einrichten

Ein Logging-System wird konfiguriert, um Meldungen während der Ausführung des Skripts aufzuzeichnen. Die Meldungen werden in einer Datei mit dem Namen "optimistprimetrader.log" gespeichert.

## API-Schlüssel laden

Das Skript lädt API-Schlüssel aus der Datei "config.json". Diese Schlüssel sind erforderlich, um auf die Binance-API zugreifen zu können.

## MACD-Indikator und Datenabfrage

Es wird eine Funktion "get_macd" definiert, um den MACD-Indikator für Kursdaten zu berechnen. Eine weitere Funktion "get_bars" wird definiert, um historische Kursdaten von Binance abzurufen, die dann in ein Pandas DataFrame umgewandelt werden.

## Konfiguration der Handelsstrategie

Es wird eine Liste von Assets definiert, für die Kursdaten abgefragt werden. Für jedes Asset werden Informationen wie Asset-Name, Bestandsstatus und Bestellgröße festgelegt.

## Haupt-Handelsschleife

Die Haupt-Handelsschleife des Bots läuft endlos und führt die folgenden Schritte aus:

1. Abfrage von Kontoinformationen über die Binance-API, um den aktuellen Bestand des jeweiligen Assets abzurufen.

2. Iteration über die definierten Assets und Überprüfung, ob Kauf- oder Verkaufssignale basierend auf der MACD-Strategie vorliegen.

3. Anzeige von Handelsinformationen, wie Asset-Name, Bestandsstatus und Handelsentscheidungen.

4. Ausführung von Marktkauf- oder Verkaufsaufträgen über die Binance-API, falls die Handelsbedingungen erfüllt sind.

5. Aktualisierung des Orderbuchs in einer CSV-Datei mit Handelsdetails.

6. Das Skript pausiert für 5 Sekunden, bevor die nächste Iteration beginnt.

## Fehlerbehandlung und Logging

Das Skript enthält auch Mechanismen zur Fehlerbehandlung, um unerwartete Fehler während der Ausführung zu erkennen und zu protokollieren. Alle Fehlermeldungen werden in der "optimistprimetrader.log"-Datei festgehalten.

## Hinweis

Um dieses Skript erfolgreich auszuführen, ist es wichtig sicherzustellen, dass die erforderlichen API-Schlüssel in der "config.json"-Datei korrekt und sicher gespeichert sind.
