import requests

HOST = "http://localhost:8080"

required_fields_mitarbeiter = {"personalNr", "passwort", "email", "vorname", "nachname"}
required_fields_kunde = {"kundeId", "email", "vorname", "nachname", "passwort", "adressen"}
required_fields_kunden_adresse = {"adresse", "typ"}
required_fields_adresse = {"adresseId", "aktiv", "strasse", "hausnummer", "plz", "ort", "land"}
required_fields_produkt = {"sku", "name", "preis", "lagerbestand", "angelegtVon"}
required_fields_bestellposition = {"positionsId", "bestellungId", "produktSku", "menge", "gesamtpreis"}

invalid_passwords = {
    "shorter_than_5": "Ab1?",
    "longer_than_20": "A" * 21 + "1a?",
    "no_number": "Password?",
    "no_letter": "12345678?",
    "no_special_char": "Password1",
}

invalid_id = 9999
invalid_sku = "INVALID-SKU-XYZ"
