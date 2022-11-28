# Alle Infos zu diesem Projekt befinden sich auf meinem Blog
https://www.michaelreitbauer.at/blog


# SmartMeterEVN
Dieses Projekt ermöglicht es den Smartmeter der EVN (Netz Niederösterreich) über die Kundenschnittstelle auszulesen.
Smart Meter werden von der Netz NÖ GmbH eingebaut, auf Basis der gesetzlichen Forderungen.

## Getting Started

Getestet auf einem Raspberry Pi 2 Model B Rev 1.1, debian 11.2

    sudo apt-get install python3-lxml
    sudo pip install -r requirements.txt

- update .env
 

### Voraussetzungen Hardware


* Passwort für die Kundenschnittstelle
  * Alle folgenden Informationen sind aus dem Folder der EVN. (https://www.netz-noe.at/Download-(1)/Smart-Meter/218_9_SmartMeter_Kundenschnittstelle_lektoriert_14.aspx)
  * Wenn bereits ein Smart Meter in der Kundenanlage eingebaut ist, kann hier das der Schlüssel angefordert werden: smartmeter@netz-noe.at
    * Kundennummer oder Vertragskontonummer
    * Zählernummer
    * Handynummer




### Zähler Hersteller
* Kaifa Drehstromzähler MA309


### Unterstützung
Spendenlink: https://www.paypal.me/greenMikeEU

## License

This project is licensed under the GNU General Public License v3.0 License - see the LICENSE.md file for details