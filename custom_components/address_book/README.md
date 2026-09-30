# Adressbuch (address_book)

Persönliches Adressbuch für Home Assistant. Speicherort wählbar: **PostgreSQL**, **MariaDB** oder **Textdatei (JSON)**.

## Installation
1. Ordner `custom_components/address_book` nach `<config>/custom_components/` kopieren.
2. HA neu starten → *Einstellungen → Geräte & Dienste → Integration hinzufügen → Adressbuch*.
3. Speicherort wählen:
   - **PostgreSQL / MariaDB:** Host, Port, Datenbank, Benutzer, Passwort. Die Tabelle
     `address_book_contacts` wird automatisch angelegt (DB-Benutzer braucht `CREATE`).
     MariaDB ab 10.2 (CHECK-Constraints).
   - **Textdatei:** Pfad zur JSON-Datei (Standard `/config/address_book.json`). Liegt sie
     außerhalb von `/config`, muss der Ordner in `allowlist_external_dirs` stehen.

Pro Speicherort kann eine Instanz angelegt werden; ein späterer Wechsel des Backends
migriert Daten nicht automatisch.

## Felder
| Feld | Regel |
|---|---|
| `name` (Name) | alphanumerisch (inkl. Umlaute; Leerzeichen, `-`, `'`, `.` innerhalb erlaubt) |
| `first_name` (Vorname) | wie Name |
| `group_name` (Gruppenname) | wie Name |
| `mobile` (Mobilnummer) | nur Ziffern, optional ein führendes `+` |
| `whatsapp_id` | nur Ziffern |

**Vorname oder Gruppenname muss ausgefüllt sein** (Prüfung im Service und zusätzlich als CHECK-Constraint in der DB).

## Services
- `address_book.add_contact` – legt an, liefert den Datensatz (inkl. `id`) als Response
- `address_book.update_contact` – `id` + zu ändernde Felder (`null` leert ein Feld)
- `address_book.delete_contact` – `id`
- `address_book.search_contacts` – optional `query` (Teilstring über alle Felder), Response `contacts: [...]`

Zusätzlich gibt es den Sensor `Anzahl Kontakte`.
