# HA-WhatsApp-AdressBook

Home-Assistant-Integration: persönliches Adressbuch mit Name, Vorname, Gruppe, Mobilnummer und WhatsApp-ID.
Speicherung wahlweise in **PostgreSQL**, **MariaDB** oder als **JSON-Datei**.

## Installation
**HACS:** ⋮ → *Benutzerdefinierte Repositories* → `https://github.com/GB-1972/ha-whatsapp-adressbook`, Kategorie *Integration* → installieren.
**Manuell:** Ordner `custom_components/address_book` nach `<config>/custom_components/` kopieren.

Danach Home Assistant neu starten und *Einstellungen → Geräte & Dienste → Integration hinzufügen → Adressbuch* wählen.

## Oberfläche (Seitenleiste „Adressbuch“)
Nach der Einrichtung erscheint in der Seitenleiste (nur für Administratoren) der Eintrag **Adressbuch**:
- Kontakte suchen, sortieren, anlegen, bearbeiten und löschen – mit Live-Prüfung der Felder
- Mobilnummer und WhatsApp-ID sind direkt anklickbar (`tel:` bzw. `wa.me`)
- **CSV-Import** per Datei-Upload oder Drag & Drop, mit Vorschau vor dem Import
- **CSV-Export** (Excel-tauglich, `;`-getrennt, UTF-8) und eine Import-Vorlage
- Dunkel-/Hell-Modus, Deutsch/Englisch, Smartphone-Ansicht

### CSV-Import
- Erste Zeile = Spaltenüberschriften. Erkannt werden u. a. `Name`/`Nachname`, `Vorname`/`First name`,
  `Gruppenname`/`Gruppe`, `Mobilnummer`/`Mobil`/`Handy`/`Telefon`, `WhatsApp-ID`/`WhatsApp`. Weitere Spalten werden ignoriert.
- Trennzeichen (`;` `,` Tab) und Zeichensatz (UTF-8 oder Windows-1252) werden automatisch erkannt.
- Leerzeichen, `-`, `/`, `()` in Nummern werden entfernt, `0049…` wird zu `+49…`; bei der WhatsApp-ID wird ein führendes `+` entfernt.
- Jede Zeile wird nach den Feldregeln unten geprüft. Fehlerhafte Zeilen werden in der Vorschau markiert und nicht importiert.
- Optional werden bereits vorhandene Kontakte übersprungen (gleicher Name, Vorname, Gruppe und Mobilnummer).
- Maximal 5000 Zeilen / 5 MB pro Datei.

## Speicherort
- **PostgreSQL / MariaDB:** Host, Port, Datenbank, Benutzer, Passwort (optional SSL). Die Tabelle
  `address_book_contacts` wird automatisch angelegt (der DB-Benutzer braucht `CREATE`). MariaDB ab 10.2.
- **Textdatei:** Pfad zur JSON-Datei (Standard `/config/address_book.json`). Außerhalb von `/config`
  muss der Ordner in `allowlist_external_dirs` stehen.

Pro Speicherort ist eine Instanz möglich; ein Wechsel migriert keine Daten.

## Felder
| Feld | Regel |
|---|---|
| `name` (Name) | alphanumerisch (inkl. Umlaute; Leerzeichen, `-`, `'`, `.` innerhalb erlaubt) |
| `first_name` (Vorname) | wie Name |
| `group_name` (Gruppenname) | wie Name |
| `mobile` (Mobilnummer) | nur Ziffern, optional ein führendes `+` |
| `whatsapp_id` | nur Ziffern |

**Vorname oder Gruppenname muss ausgefüllt sein** (Prüfung im Service, bei den Datenbanken zusätzlich als CHECK-Constraint).

## Services
- `address_book.add_contact` – legt an, liefert den Datensatz (inkl. `id`) als Response
- `address_book.update_contact` – `id` + zu ändernde Felder (`null` leert ein Feld)
- `address_book.delete_contact` – `id`
- `address_book.search_contacts` – optional `query` (Teilstring über alle Felder), Response `contacts: [...]`

Zusätzlich gibt es den Sensor *Anzahl Kontakte*.

## Tests
`pip install pytest && pytest tests`
