/* Adressbuch – Seitenleisten-Panel für Home Assistant (ohne Build-Schritt). */

const T = {
  de: {
    title: "Adressbuch", search: "Suchen …", new: "Neuer Kontakt", import: "CSV importieren",
    export: "Exportieren", count: (n, t) => (n === t ? `${t} Kontakte` : `${n} von ${t} Kontakten`),
    first_name: "Vorname", name: "Name", group_name: "Gruppenname", mobile: "Mobilnummer",
    whatsapp_id: "WhatsApp-ID", actions: "Aktionen", edit: "Bearbeiten", delete: "Löschen",
    save: "Speichern", cancel: "Abbrechen", close: "Schließen", back: "Zurück",
    new_title: "Neuer Kontakt", edit_title: "Kontakt bearbeiten",
    hint_required: "Vorname oder Gruppenname muss ausgefüllt sein.",
    hint_mobile: "Nur Ziffern, optional mit führendem +", hint_wa: "Nur Ziffern",
    empty: "Noch keine Kontakte", empty_sub: "Lege den ersten Kontakt an oder importiere eine CSV-Datei.",
    no_match: "Keine Treffer", confirm_delete: (n) => `„${n}“ wirklich löschen?`,
    saved: "Gespeichert", deleted: "Gelöscht", imported: (n) => `${n} Kontakte importiert`,
    load_error: "Kontakte konnten nicht geladen werden",
    import_title: "CSV importieren",
    drop: "CSV-Datei hier ablegen oder klicken zum Auswählen",
    drop_sub: "Trennzeichen (; , Tab) und Zeichensatz werden automatisch erkannt.",
    columns_hint: "Erste Zeile = Spaltenüberschriften: Name, Vorname, Gruppenname, Mobilnummer, WhatsApp-ID.",
    template: "Vorlage herunterladen", skip_dup: "Bereits vorhandene Kontakte überspringen",
    preview: "Vorschau", n_new: (n) => `${n} neu`, n_dup: (n) => `${n} Duplikate`,
    n_err: (n) => `${n} fehlerhaft`, ignored: (c) => `Ignorierte Spalten: ${c}`,
    do_import: (n) => `${n} Kontakte importieren`, nothing: "Nichts zu importieren",
    line: "Zeile", status: "Status", st_new: "neu", st_duplicate: "Duplikat", st_error: "Fehler",
    result_title: "Import abgeschlossen", result_imported: (n) => `${n} importiert`,
    result_dup: (n) => `${n} Duplikate übersprungen`, result_err: (n) => `${n} fehlerhaft`,
    working: "Bitte warten …",
    errors: {
      invalid_name: "Name: nur Buchstaben und Ziffern",
      invalid_first_name: "Vorname: nur Buchstaben und Ziffern",
      invalid_group_name: "Gruppenname: nur Buchstaben und Ziffern",
      invalid_mobile: "Mobilnummer: nur Ziffern, optional führendes +",
      invalid_whatsapp_id: "WhatsApp-ID: nur Ziffern",
      first_name_or_group_required: "Vorname oder Gruppenname fehlt",
      contact_not_found: "Kontakt nicht gefunden",
      empty_file: "Die Datei ist leer",
      no_known_columns: "Keine bekannten Spaltenüberschriften gefunden",
      too_many_rows: "Zu viele Zeilen (max. 5000)",
      file_too_large: "Datei zu groß (max. 5 MB)",
      db_error: "Fehler beim Zugriff auf den Speicher",
      address_book_not_loaded: "Das Adressbuch ist nicht geladen",
      admin_required: "Administratorrechte erforderlich",
      no_file: "Keine Datei erhalten",
    },
  },
  en: {
    title: "Address book", search: "Search …", new: "New contact", import: "Import CSV",
    export: "Export", count: (n, t) => (n === t ? `${t} contacts` : `${n} of ${t} contacts`),
    first_name: "First name", name: "Name", group_name: "Group name", mobile: "Mobile",
    whatsapp_id: "WhatsApp ID", actions: "Actions", edit: "Edit", delete: "Delete",
    save: "Save", cancel: "Cancel", close: "Close", back: "Back",
    new_title: "New contact", edit_title: "Edit contact",
    hint_required: "First name or group name is required.",
    hint_mobile: "Digits only, optional leading +", hint_wa: "Digits only",
    empty: "No contacts yet", empty_sub: "Add your first contact or import a CSV file.",
    no_match: "No matches", confirm_delete: (n) => `Really delete “${n}”?`,
    saved: "Saved", deleted: "Deleted", imported: (n) => `${n} contacts imported`,
    load_error: "Could not load contacts",
    import_title: "Import CSV",
    drop: "Drop a CSV file here or click to choose",
    drop_sub: "Delimiter (; , tab) and encoding are detected automatically.",
    columns_hint: "First row = column headers: Name, First name, Group name, Mobile, WhatsApp ID.",
    template: "Download template", skip_dup: "Skip contacts that already exist",
    preview: "Preview", n_new: (n) => `${n} new`, n_dup: (n) => `${n} duplicates`,
    n_err: (n) => `${n} invalid`, ignored: (c) => `Ignored columns: ${c}`,
    do_import: (n) => `Import ${n} contacts`, nothing: "Nothing to import",
    line: "Line", status: "Status", st_new: "new", st_duplicate: "duplicate", st_error: "error",
    result_title: "Import finished", result_imported: (n) => `${n} imported`,
    result_dup: (n) => `${n} duplicates skipped`, result_err: (n) => `${n} invalid`,
    working: "Please wait …",
    errors: {
      invalid_name: "Name: letters and digits only",
      invalid_first_name: "First name: letters and digits only",
      invalid_group_name: "Group name: letters and digits only",
      invalid_mobile: "Mobile: digits only, optional leading +",
      invalid_whatsapp_id: "WhatsApp ID: digits only",
      first_name_or_group_required: "First name or group name is missing",
      contact_not_found: "Contact not found",
      empty_file: "The file is empty",
      no_known_columns: "No known column headers found",
      too_many_rows: "Too many rows (max. 5000)",
      file_too_large: "File too large (max. 5 MB)",
      db_error: "Storage access failed",
      address_book_not_loaded: "The address book is not loaded",
      admin_required: "Administrator rights required",
      no_file: "No file received",
    },
  },
};

const FIELDS = ["first_name", "name", "group_name", "mobile", "whatsapp_id"];
const ALNUM = /^[\p{L}\p{N}]+(?:[ .'\-][\p{L}\p{N}]+)*\.?$/u;
const RULES = {
  name: [ALNUM, 100, "invalid_name"],
  first_name: [ALNUM, 100, "invalid_first_name"],
  group_name: [ALNUM, 100, "invalid_group_name"],
  mobile: [/^\+?[0-9]+$/, 20, "invalid_mobile"],
  whatsapp_id: [/^[0-9]+$/, 30, "invalid_whatsapp_id"],
};

const esc = (v) =>
  String(v ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[c]);

const CSS = `
:host { display:block; height:100%; background:var(--primary-background-color); color:var(--primary-text-color);
  font-family:var(--paper-font-body1_-_font-family, Roboto, sans-serif); }
* { box-sizing:border-box; }
.bar { position:sticky; top:0; z-index:5; display:flex; align-items:center; gap:12px; height:56px; padding:0 16px;
  background:var(--app-header-background-color, var(--primary-color)); color:var(--app-header-text-color, #fff); }
.bar h1 { font-size:20px; font-weight:500; margin:0; flex:1; }
.bar button.icon { background:none; border:0; color:inherit; cursor:pointer; padding:6px; border-radius:50%; display:flex; }
.wrap { max-width:1100px; margin:0 auto; padding:16px; }
.tools { display:flex; flex-wrap:wrap; gap:10px; align-items:center; margin-bottom:12px; }
.search { flex:1 1 240px; display:flex; align-items:center; gap:8px; padding:0 12px; height:44px; border-radius:22px;
  background:var(--card-background-color); border:1px solid var(--divider-color); }
.search:focus-within { border-color:var(--primary-color); }
.search input { flex:1; border:0; outline:0; background:none; color:inherit; font:inherit; min-width:0; }
.search ha-icon { --mdc-icon-size:20px; color:var(--secondary-text-color); }
button.btn { display:inline-flex; align-items:center; gap:6px; height:40px; padding:0 16px; border-radius:20px; cursor:pointer;
  font:inherit; font-weight:500; border:1px solid var(--divider-color); background:var(--card-background-color); color:var(--primary-text-color); }
button.btn:hover { background:var(--secondary-background-color); }
button.btn.primary { background:var(--primary-color); color:var(--text-primary-color, #fff); border-color:transparent; }
button.btn.primary:hover { filter:brightness(1.08); }
button.btn.danger { color:var(--error-color); }
button.btn:disabled { opacity:.5; cursor:default; filter:none; }
button.btn ha-icon { --mdc-icon-size:18px; }
.count { color:var(--secondary-text-color); font-size:13px; margin:0 4px 8px; }
.card { background:var(--card-background-color); border-radius:var(--ha-card-border-radius, 12px);
  box-shadow:var(--ha-card-box-shadow, none); border:1px solid var(--divider-color); overflow:hidden; }
.row { display:grid; grid-template-columns:1.1fr 1.1fr 1fr 1.2fr 1.2fr 92px; gap:8px; align-items:center;
  padding:10px 16px; border-bottom:1px solid var(--divider-color); }
.row:last-child { border-bottom:0; }
.row.head { background:var(--secondary-background-color); font-size:12px; text-transform:uppercase; letter-spacing:.04em;
  color:var(--secondary-text-color); user-select:none; padding-top:12px; padding-bottom:12px; }
.row.head > div[data-sort] { cursor:pointer; display:flex; align-items:center; gap:4px; }
.row.head > div[data-sort]:hover { color:var(--primary-text-color); }
.row:not(.head):hover { background:var(--secondary-background-color); }
.cell.title { display:none; }
.cell { overflow:hidden; text-overflow:ellipsis; white-space:nowrap; min-width:0; }
.cell a { color:var(--primary-color); text-decoration:none; }
.cell a:hover { text-decoration:underline; }
.muted { color:var(--disabled-text-color); }
.chip { display:inline-block; padding:2px 10px; border-radius:12px; font-size:13px;
  background:color-mix(in srgb, var(--primary-color) 14%, transparent); color:var(--primary-color); }
.acts { display:flex; justify-content:flex-end; gap:2px; }
.acts button { background:none; border:0; cursor:pointer; padding:6px; border-radius:50%; color:var(--secondary-text-color); display:flex; }
.acts button:hover { background:var(--divider-color); color:var(--primary-text-color); }
.acts button.del:hover { color:var(--error-color); }
.empty { text-align:center; padding:56px 16px; color:var(--secondary-text-color); }
.empty ha-icon { --mdc-icon-size:56px; opacity:.5; }
.empty h2 { margin:8px 0 4px; color:var(--primary-text-color); font-weight:500; font-size:18px; }
@media (max-width:800px) {
  .row.head { display:none; }
  .row { grid-template-columns:1fr auto; row-gap:2px; padding:12px 14px; }
  .row .cell.first, .row .cell.name { display:none; }
  .row .cell.none { display:none; }
  .row .cell.title { display:block; grid-column:1; font-weight:500; font-size:16px; }
  .row .cell { white-space:normal; }
  .row .cell[data-label]::before { content:attr(data-label) ": "; color:var(--secondary-text-color); font-size:12px; }
  .row .acts { grid-column:2; grid-row:1 / span 4; align-self:start; }
}
dialog { border:0; border-radius:var(--ha-card-border-radius, 16px); padding:0; width:min(560px, calc(100vw - 24px));
  max-height:calc(100vh - 32px); background:var(--card-background-color); color:var(--primary-text-color);
  box-shadow:0 12px 40px rgba(0,0,0,.35); }
dialog.wide { width:min(780px, calc(100vw - 24px)); }
dialog::backdrop { background:rgba(0,0,0,.5); }
.dlg { display:flex; flex-direction:column; max-height:calc(100vh - 32px); }
.dlg header { padding:18px 24px 6px; font-size:20px; font-weight:500; }
.dlg .body { padding:8px 24px 16px; overflow:auto; }
.dlg footer { display:flex; justify-content:flex-end; gap:8px; padding:12px 24px 18px; border-top:1px solid var(--divider-color); }
.field { margin-bottom:14px; }
.field label { display:block; font-size:12px; color:var(--secondary-text-color); margin-bottom:4px; }
.field input[type=text], .field input[type=tel] { width:100%; height:44px; padding:0 12px; font:inherit; color:inherit;
  background:var(--secondary-background-color); border:1px solid var(--divider-color); border-radius:8px; outline:0; }
.field input:focus { border-color:var(--primary-color); }
.field.bad input { border-color:var(--error-color); }
.field .msg { color:var(--error-color); font-size:12px; min-height:0; margin-top:3px; }
.field .hint { color:var(--secondary-text-color); font-size:12px; margin-top:3px; }
.grid2 { display:grid; grid-template-columns:1fr 1fr; gap:0 14px; }
@media (max-width:520px) { .grid2 { grid-template-columns:1fr; } }
.formerr { color:var(--error-color); font-size:13px; margin:0 0 10px; }
.drop { border:2px dashed var(--divider-color); border-radius:12px; padding:32px 16px; text-align:center; cursor:pointer;
  color:var(--secondary-text-color); transition:.15s; }
.drop:hover, .drop.over { border-color:var(--primary-color); background:color-mix(in srgb, var(--primary-color) 8%, transparent); }
.drop ha-icon { --mdc-icon-size:40px; color:var(--primary-color); }
.drop .t { color:var(--primary-text-color); margin:6px 0 2px; }
.drop .f { margin-top:8px; color:var(--primary-text-color); font-weight:500; }
.opt { display:flex; align-items:center; gap:8px; margin:14px 0 4px; }
.small { font-size:12px; color:var(--secondary-text-color); }
a.link { color:var(--primary-color); cursor:pointer; text-decoration:none; font-size:13px; }
.chips { display:flex; gap:8px; flex-wrap:wrap; margin-bottom:12px; }
.chips .chip { font-size:13px; padding:4px 12px; }
.chip.ok { background:color-mix(in srgb, var(--success-color, #43a047) 18%, transparent); color:var(--success-color, #43a047); }
.chip.warn { background:color-mix(in srgb, var(--warning-color, #ffa600) 20%, transparent); color:var(--warning-color, #ffa600); }
.chip.err { background:color-mix(in srgb, var(--error-color) 16%, transparent); color:var(--error-color); }
table { width:100%; border-collapse:collapse; font-size:13px; }
th { text-align:left; font-weight:500; font-size:11px; text-transform:uppercase; letter-spacing:.04em; color:var(--secondary-text-color);
  padding:6px 8px; position:sticky; top:0; background:var(--card-background-color); }
td { padding:6px 8px; border-top:1px solid var(--divider-color); max-width:150px; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; }
.tablewrap { max-height:320px; overflow:auto; border:1px solid var(--divider-color); border-radius:8px; }
.toast { position:fixed; left:50%; bottom:24px; transform:translate(-50%, 20px); opacity:0; pointer-events:none; z-index:20;
  background:var(--primary-text-color); color:var(--primary-background-color); padding:10px 18px; border-radius:8px; transition:.2s; max-width:90vw; }
.toast.show { opacity:1; transform:translate(-50%, 0); }
.toast.err { background:var(--error-color); color:#fff; }
`;

class AddressBookPanel extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: "open" });
    this._contacts = [];
    this._q = "";
    this._sort = { key: "name", dir: 1 };
    this._narrow = false;
    this._import = { file: null, skipDup: true };
  }

  set hass(hass) {
    const first = !this._hass;
    this._hass = hass;
    if (first) {
      this._build();
      this._load();
    }
  }
  set narrow(v) { this._narrow = v; if (this._menu) this._menu.style.display = v ? "flex" : "none"; }
  set panel(_) {}
  set route(_) {}

  get _t() { return T[(this._hass?.language || "en").startsWith("de") ? "de" : "en"]; }
  _err(key) { return this._t.errors[key] || key; }

  // ------------------------------------------------------------------ skeleton
  _build() {
    const t = this._t;
    this.shadowRoot.innerHTML = `
      <style>${CSS}</style>
      <div class="bar">
        <button class="icon" id="menu" style="display:${this._narrow ? "flex" : "none"}" aria-label="Menu"><ha-icon icon="mdi:menu"></ha-icon></button>
        <h1>${esc(t.title)}</h1>
      </div>
      <div class="wrap">
        <div class="tools">
          <label class="search"><ha-icon icon="mdi:magnify"></ha-icon><input id="q" type="search" placeholder="${esc(t.search)}" autocomplete="off"></label>
          <button class="btn primary" id="new"><ha-icon icon="mdi:account-plus"></ha-icon>${esc(t.new)}</button>
          <button class="btn" id="imp"><ha-icon icon="mdi:file-upload-outline"></ha-icon>${esc(t.import)}</button>
          <button class="btn" id="exp"><ha-icon icon="mdi:file-download-outline"></ha-icon>${esc(t.export)}</button>
        </div>
        <div class="count" id="count"></div>
        <div class="card" id="list"></div>
      </div>
      <dialog id="dlg"></dialog>
      <dialog id="idlg" class="wide"></dialog>
      <div class="toast" id="toast"></div>`;
    const $ = (s) => this.shadowRoot.querySelector(s);
    this._menu = $("#menu");
    this._menu.addEventListener("click", () => this.dispatchEvent(new Event("hass-toggle-menu", { bubbles: true, composed: true })));
    $("#q").addEventListener("input", (e) => { this._q = e.target.value; this._renderList(); });
    $("#new").addEventListener("click", () => this._openForm());
    $("#imp").addEventListener("click", () => this._openImport());
    $("#exp").addEventListener("click", () => this._export());
    $("#list").addEventListener("click", (e) => this._onListClick(e));
  }

  async _load() {
    try {
      const res = await this._hass.callWS({ type: "address_book/list" });
      this._contacts = res.contacts;
      this._renderList();
    } catch (err) {
      this._toast(this._t.load_error + (err?.message ? `: ${this._err(err.message)}` : ""), true);
    }
  }

  // ------------------------------------------------------------------ list
  _label(c) { return [c.first_name, c.name].filter(Boolean).join(" ") || c.group_name || ""; }

  _renderList() {
    const t = this._t;
    const q = this._q.trim().toLowerCase();
    const { key, dir } = this._sort;
    const rows = this._contacts
      .filter((c) => !q || FIELDS.some((f) => (c[f] || "").toLowerCase().includes(q)))
      .sort((a, b) => {
        const x = a[key] || "", y = b[key] || "";
        if (!x !== !y) return x ? -1 : 1; // empty values always last
        return dir * x.localeCompare(y, undefined, { sensitivity: "base", numeric: true }) || a.id - b.id;
      });
    this.shadowRoot.querySelector("#count").textContent = t.count(rows.length, this._contacts.length);
    const list = this.shadowRoot.querySelector("#list");
    if (!this._contacts.length) {
      list.innerHTML = `<div class="empty"><ha-icon icon="mdi:contacts-outline"></ha-icon><h2>${esc(t.empty)}</h2><div>${esc(t.empty_sub)}</div></div>`;
      return;
    }
    if (!rows.length) {
      list.innerHTML = `<div class="empty"><ha-icon icon="mdi:magnify-close"></ha-icon><h2>${esc(t.no_match)}</h2></div>`;
      return;
    }
    const arrow = (k) => (key === k ? `<ha-icon icon="mdi:arrow-${dir > 0 ? "up" : "down"}" style="--mdc-icon-size:14px"></ha-icon>` : "");
    const head = ["first_name", "name", "group_name", "mobile", "whatsapp_id"]
      .map((k) => `<div data-sort="${k}">${esc(t[k])}${arrow(k)}</div>`).join("");
    const dash = `<span class="muted">–</span>`;
    const body = rows.map((c) => `
      <div class="row" data-id="${c.id}">
        <div class="cell title">${esc(this._label(c))}</div>
        <div class="cell first" data-label="${esc(t.first_name)}">${c.first_name ? esc(c.first_name) : dash}</div>
        <div class="cell name" data-label="${esc(t.name)}">${c.name ? esc(c.name) : dash}</div>
        <div class="cell${c.group_name ? "" : " none"}" data-label="${esc(t.group_name)}">${c.group_name ? `<span class="chip">${esc(c.group_name)}</span>` : dash}</div>
        <div class="cell${c.mobile ? "" : " none"}" data-label="${esc(t.mobile)}">${c.mobile ? `<a href="tel:${esc(c.mobile)}">${esc(c.mobile)}</a>` : dash}</div>
        <div class="cell${c.whatsapp_id ? "" : " none"}" data-label="${esc(t.whatsapp_id)}">${c.whatsapp_id ? `<a href="https://wa.me/${esc(c.whatsapp_id)}" target="_blank" rel="noopener">${esc(c.whatsapp_id)}</a>` : dash}</div>
        <div class="acts">
          <button data-act="edit" title="${esc(t.edit)}"><ha-icon icon="mdi:pencil"></ha-icon></button>
          <button data-act="del" class="del" title="${esc(t.delete)}"><ha-icon icon="mdi:delete-outline"></ha-icon></button>
        </div>
      </div>`).join("");
    list.innerHTML = `<div class="row head">${head}<div></div></div>${body}`;
  }

  _onListClick(e) {
    const sort = e.target.closest("[data-sort]");
    if (sort) {
      const k = sort.dataset.sort;
      this._sort = { key: k, dir: this._sort.key === k ? -this._sort.dir : 1 };
      this._renderList();
      return;
    }
    const btn = e.target.closest("button[data-act]");
    const row = e.target.closest(".row[data-id]");
    if (!btn || !row) return;
    const c = this._contacts.find((x) => x.id === Number(row.dataset.id));
    if (!c) return;
    if (btn.dataset.act === "edit") this._openForm(c);
    else this._confirmDelete(c);
  }

  // ------------------------------------------------------------------ contact form
  _validate(values) {
    const errors = {};
    for (const f of Object.keys(RULES)) {
      const v = (values[f] || "").trim();
      if (!v) continue;
      const [re, max, key] = RULES[f];
      if (v.length > max || !re.test(v)) errors[f] = key;
    }
    const needs = !(values.first_name || "").trim() && !(values.group_name || "").trim();
    return { errors, needs };
  }

  _openForm(contact = null) {
    const t = this._t;
    const dlg = this.shadowRoot.querySelector("#dlg");
    const c = contact || {};
    const input = (f, type = "text", hint = "") => `
      <div class="field" data-f="${f}">
        <label for="f_${f}">${esc(t[f])}</label>
        <input id="f_${f}" type="${type}" value="${esc(c[f] || "")}" autocomplete="off" ${f === "mobile" ? 'inputmode="tel"' : f === "whatsapp_id" ? 'inputmode="numeric"' : ""}>
        ${hint ? `<div class="hint">${esc(hint)}</div>` : ""}<div class="msg"></div>
      </div>`;
    dlg.className = "";
    dlg.innerHTML = `
      <form class="dlg" method="dialog" novalidate>
        <header>${esc(contact ? t.edit_title : t.new_title)}</header>
        <div class="body">
          <div class="grid2">${input("first_name")}${input("name")}</div>
          ${input("group_name")}
          <div class="grid2">${input("mobile", "tel", t.hint_mobile)}${input("whatsapp_id", "text", t.hint_wa)}</div>
          <p class="formerr" id="req"></p>
        </div>
        <footer>
          <button class="btn" type="button" id="cancel">${esc(t.cancel)}</button>
          <button class="btn primary" type="submit" id="save">${esc(t.save)}</button>
        </footer>
      </form>`;
    const $ = (s) => dlg.querySelector(s);
    const read = () => Object.fromEntries(FIELDS.map((f) => [f, $(`#f_${f}`).value.trim()]));
    const refresh = (showReq) => {
      const values = read();
      const { errors, needs } = this._validate(values);
      for (const f of FIELDS) {
        const box = $(`.field[data-f="${f}"]`);
        box.classList.toggle("bad", !!errors[f]);
        box.querySelector(".msg").textContent = errors[f] ? this._err(errors[f]) : "";
      }
      $("#req").textContent = needs && showReq ? t.hint_required : "";
      return { errors, needs, values };
    };
    dlg.querySelectorAll("input").forEach((i) => i.addEventListener("input", () => refresh(false)));
    $("#cancel").addEventListener("click", () => dlg.close());
    $("form").addEventListener("submit", async (e) => {
      e.preventDefault();
      const { errors, needs, values } = refresh(true);
      if (needs || Object.keys(errors).length) return;
      const msg = { type: "address_book/save" };
      if (contact) msg.contact_id = contact.id;
      for (const f of FIELDS) msg[f] = values[f] || null;
      $("#save").disabled = true;
      try {
        await this._hass.callWS(msg);
        dlg.close();
        this._toast(t.saved);
        await this._load();
      } catch (err) {
        $("#req").textContent = this._err(err?.message || "db_error");
        $("#save").disabled = false;
      }
    });
    dlg.showModal();
    $("#f_first_name").focus();
  }

  _confirmDelete(c) {
    const t = this._t;
    const dlg = this.shadowRoot.querySelector("#dlg");
    dlg.className = "";
    dlg.innerHTML = `
      <div class="dlg">
        <header>${esc(t.delete)}</header>
        <div class="body">${esc(t.confirm_delete(this._label(c)))}</div>
        <footer>
          <button class="btn" id="no">${esc(t.cancel)}</button>
          <button class="btn primary danger" id="yes" style="background:var(--error-color);color:#fff">${esc(t.delete)}</button>
        </footer>
      </div>`;
    dlg.querySelector("#no").addEventListener("click", () => dlg.close());
    dlg.querySelector("#yes").addEventListener("click", async () => {
      try {
        await this._hass.callWS({ type: "address_book/delete", contact_id: c.id });
        dlg.close();
        this._toast(t.deleted);
        await this._load();
      } catch (err) {
        dlg.close();
        this._toast(this._err(err?.message || "db_error"), true);
      }
    });
    dlg.showModal();
  }

  // ------------------------------------------------------------------ CSV import
  _openImport() {
    this._import = { file: null, skipDup: true };
    this._importStep1();
    this.shadowRoot.querySelector("#idlg").showModal();
  }

  _csvTemplate() {
    this._download("adressbuch-vorlage.csv", [], true);
  }

  _importStep1(error = "") {
    const t = this._t;
    const dlg = this.shadowRoot.querySelector("#idlg");
    const f = this._import.file;
    dlg.innerHTML = `
      <div class="dlg">
        <header>${esc(t.import_title)}</header>
        <div class="body">
          <div class="drop" id="drop">
            <ha-icon icon="mdi:file-delimited-outline"></ha-icon>
            <div class="t">${esc(t.drop)}</div>
            <div class="small">${esc(t.drop_sub)}</div>
            ${f ? `<div class="f">${esc(f.name)}</div>` : ""}
            <input type="file" id="file" accept=".csv,.txt,text/csv" hidden>
          </div>
          <p class="small">${esc(t.columns_hint)} <a class="link" id="tpl">${esc(t.template)}</a></p>
          <label class="opt"><input type="checkbox" id="skip" ${this._import.skipDup ? "checked" : ""}> ${esc(t.skip_dup)}</label>
          <p class="formerr" id="err">${esc(error)}</p>
        </div>
        <footer>
          <button class="btn" id="close">${esc(t.close)}</button>
          <button class="btn primary" id="next" ${f ? "" : "disabled"}>${esc(t.preview)}</button>
        </footer>
      </div>`;
    const $ = (s) => dlg.querySelector(s);
    const drop = $("#drop"), input = $("#file");
    const pick = (file) => { if (file) { this._import.file = file; this._importStep1(); } };
    drop.addEventListener("click", () => input.click());
    input.addEventListener("change", () => pick(input.files[0]));
    ["dragenter", "dragover"].forEach((ev) => drop.addEventListener(ev, (e) => { e.preventDefault(); drop.classList.add("over"); }));
    ["dragleave", "drop"].forEach((ev) => drop.addEventListener(ev, (e) => { e.preventDefault(); drop.classList.remove("over"); }));
    drop.addEventListener("drop", (e) => pick(e.dataTransfer.files[0]));
    $("#skip").addEventListener("change", (e) => { this._import.skipDup = e.target.checked; });
    $("#tpl").addEventListener("click", () => this._csvTemplate());
    $("#close").addEventListener("click", () => dlg.close());
    $("#next").addEventListener("click", () => this._importPreview());
  }

  async _upload(dry) {
    const fd = new FormData();
    fd.append("file", this._import.file);
    const url = `/api/address_book/import?dry_run=${dry ? 1 : 0}&skip_duplicates=${this._import.skipDup ? 1 : 0}`;
    const res = await this._hass.fetchWithAuth(url, { method: "POST", body: fd });
    let json = {};
    try { json = await res.json(); } catch (_) { /* non-JSON error page */ }
    if (!res.ok) throw new Error(json.error || "db_error");
    return json;
  }

  _busy(text) {
    this.shadowRoot.querySelector("#idlg").innerHTML = `<div class="dlg"><div class="body" style="padding:40px;text-align:center">${esc(text)}</div></div>`;
  }

  async _importPreview() {
    const t = this._t;
    this._busy(t.working);
    let data;
    try { data = await this._upload(true); }
    catch (err) { this._importStep1(this._err(err.message)); return; }
    const dlg = this.shadowRoot.querySelector("#idlg");
    const s = data.summary;
    const stLabel = { new: t.st_new, duplicate: t.st_duplicate, error: t.st_error };
    const stClass = { new: "ok", duplicate: "warn", error: "err" };
    const rows = data.rows.map((r) => `
      <tr><td>${r.line}</td>
        ${FIELDS.map((f) => `<td title="${esc(r.data[f])}">${esc(r.data[f])}</td>`).join("")}
        <td><span class="chip ${stClass[r.status]}">${esc(stLabel[r.status])}</span>${r.error ? ` <span class="small">${esc(this._err(r.error))}</span>` : ""}</td></tr>`).join("");
    dlg.innerHTML = `
      <div class="dlg">
        <header>${esc(t.preview)} – ${esc(this._import.file.name)}</header>
        <div class="body">
          <div class="chips">
            <span class="chip ok">${esc(t.n_new(s.new))}</span>
            ${s.duplicate ? `<span class="chip warn">${esc(t.n_dup(s.duplicate))}</span>` : ""}
            ${s.error ? `<span class="chip err">${esc(t.n_err(s.error))}</span>` : ""}
          </div>
          ${data.ignored_columns.length ? `<p class="small">${esc(t.ignored(data.ignored_columns.join(", ")))}</p>` : ""}
          <div class="tablewrap"><table>
            <thead><tr><th>${esc(t.line)}</th>${FIELDS.map((f) => `<th>${esc(t[f])}</th>`).join("")}<th>${esc(t.status)}</th></tr></thead>
            <tbody>${rows}</tbody></table></div>
        </div>
        <footer>
          <button class="btn" id="back">${esc(t.back)}</button>
          <button class="btn primary" id="go" ${s.new ? "" : "disabled"}>${esc(s.new ? t.do_import(s.new) : t.nothing)}</button>
        </footer>
      </div>`;
    dlg.querySelector("#back").addEventListener("click", () => this._importStep1());
    dlg.querySelector("#go").addEventListener("click", () => this._importRun());
  }

  async _importRun() {
    const t = this._t;
    this._busy(t.working);
    let res;
    try { res = await this._upload(false); }
    catch (err) { this._importStep1(this._err(err.message)); return; }
    await this._load();
    const dlg = this.shadowRoot.querySelector("#idlg");
    const errRows = res.rows.map((r) => `<tr><td>${r.line}</td><td colspan="${FIELDS.length + 1}">${esc(this._err(r.error))}</td></tr>`).join("");
    dlg.innerHTML = `
      <div class="dlg">
        <header>${esc(t.result_title)}</header>
        <div class="body">
          <div class="chips">
            <span class="chip ok">${esc(t.result_imported(res.imported))}</span>
            ${res.duplicates ? `<span class="chip warn">${esc(t.result_dup(res.duplicates))}</span>` : ""}
            ${res.errors ? `<span class="chip err">${esc(t.result_err(res.errors))}</span>` : ""}
          </div>
          ${errRows ? `<div class="tablewrap"><table><tbody>${errRows}</tbody></table></div>` : ""}
        </div>
        <footer><button class="btn primary" id="done">${esc(t.close)}</button></footer>
      </div>`;
    dlg.querySelector("#done").addEventListener("click", () => dlg.close());
  }

  // ------------------------------------------------------------------ export
  _export() { this._download("adressbuch.csv", this._contacts); }

  _download(filename, contacts, template = false) {
    const head = ["Name", "Vorname", "Gruppenname", "Mobilnummer", "WhatsApp-ID"];
    const cell = (v) => `"${String(v ?? "").replace(/"/g, '""')}"`;
    const lines = [head.map(cell).join(";")];
    if (template) lines.push(["Müller", "Anna", "", "+491701234567", "491701234567"].map(cell).join(";"));
    for (const c of contacts) lines.push([c.name, c.first_name, c.group_name, c.mobile, c.whatsapp_id].map(cell).join(";"));
    const blob = new Blob(["﻿" + lines.join("\r\n") + "\r\n"], { type: "text/csv;charset=utf-8" });
    const a = document.createElement("a");
    a.href = URL.createObjectURL(blob);
    a.download = filename;
    this.shadowRoot.appendChild(a);
    a.click();
    a.remove();
    setTimeout(() => URL.revokeObjectURL(a.href), 1000);
  }

  _toast(text, isError = false) {
    const el = this.shadowRoot.querySelector("#toast");
    el.textContent = text;
    el.className = `toast show${isError ? " err" : ""}`;
    clearTimeout(this._toastTimer);
    this._toastTimer = setTimeout(() => (el.className = "toast"), 3500);
  }
}

customElements.define("address-book-panel", AddressBookPanel);
