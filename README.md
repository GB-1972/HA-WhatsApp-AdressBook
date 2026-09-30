# HA-WhatsApp-AdressBook

Home-Assistant-Integration: persönliches Adressbuch mit Name, Vorname, Gruppe, Mobilnummer und WhatsApp-ID.
Speicherung wahlweise in **PostgreSQL**, **MariaDB** oder als **JSON-Datei**.

## Installation
**HACS:** ⋮ → *Benutzerdefinierte Repositories* → `https://github.com/GB-1972/ha-whatsapp-adressbook`, Kategorie *Integration* → installieren.
**Manuell:** Ordner `custom_components/address_book` nach `<config>/custom_components/` kopieren.

Danach Home Assistant neu starten und *Einstellungen → Geräte & Dienste → Integration hinzufügen → Adressbuch* wählen.

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
