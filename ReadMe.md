# Campaign Copy Automation (Selenium & Python)

Dieses Projekt automatisiert die Anmeldung und das Kopieren von Kampagnen innerhalb eines internen Web-Portals.  
Über eine Excel-Liste werden Kampagnen gesucht, die höchste Version identifiziert und anschließend geklont.

️ **Wichtig:**  
Dieses Tool arbeitet mit vertraulichen Zugangsdaten. **Speichere niemals Passwörter im Code oder in GitHub!**  
Alle Credentials werden sicher über **Environment Variables** geladen.

---

##  Features

- Automatisierte Anmeldung via Selenium
- Auslesen einer Kampagnentabelle (BeautifulSoup)
- Ermitteln der höchsten Version + Wave (z. B. *V3 W2*)
- Automatisiertes Kopieren einer Kampagne
- Excel-basierte Input-Liste (`.xlsx`)
- Konfigurierbar für **Integration** oder **Produktion**

---

##  Voraussetzungen

Installiere die benötigten Pakete:

```bash
pip install selenium beautifulsoup4 pandas
