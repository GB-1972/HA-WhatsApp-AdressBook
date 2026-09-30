"""Constants for the address book integration."""

DOMAIN = "address_book"

CONF_HOST = "host"
CONF_PORT = "port"
CONF_DATABASE = "database"
CONF_USERNAME = "username"
CONF_PASSWORD = "password"
CONF_SSL = "ssl"
CONF_BACKEND = "backend"
CONF_FILE_PATH = "file_path"

BACKEND_POSTGRES = "postgres"
BACKEND_MARIADB = "mariadb"
BACKEND_FILE = "file"

DEFAULT_PORT_MARIADB = 3306
DEFAULT_FILE_PATH = "/config/address_book.json"

DEFAULT_PORT = 5432

ATTR_ID = "id"
ATTR_NAME = "name"
ATTR_FIRST_NAME = "first_name"
ATTR_GROUP_NAME = "group_name"
ATTR_MOBILE = "mobile"
ATTR_WHATSAPP_ID = "whatsapp_id"
ATTR_QUERY = "query"

SERVICE_ADD_CONTACT = "add_contact"
SERVICE_UPDATE_CONTACT = "update_contact"
SERVICE_DELETE_CONTACT = "delete_contact"
SERVICE_SEARCH_CONTACTS = "search_contacts"

SIGNAL_CONTACTS_CHANGED = f"{DOMAIN}_contacts_changed"
