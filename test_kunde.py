import requests
from common import (
    HOST,
    invalid_id,
    invalid_passwords,
    required_fields_adresse,
    required_fields_kunde,
    required_fields_kunden_adresse,
)


## -- Kunde -- ##

def test_kunde_endpoint():
    """Test the Kunde endpoint."""
    response = requests.get(f"{HOST}/kunden", timeout=2)

    assert response.status_code == 200, f"Failed to access Kunde endpoint. Code: {response.status_code}"


def test_kunde_get_all():
    """Test retrieving all Kunden."""
    response = requests.get(f"{HOST}/kunden", timeout=2)

    assert isinstance(response.json(), list), "Response is not a list of Kunden."
    assert len(response.json()) >= 10, "Expected at least 10 Kunden. (data.sql)"


def test_kunde_get_all_schema():
    """Test the schema of the Kunde data."""
    response = requests.get(f"{HOST}/kunden", timeout=2)
    kunde_list = response.json()

    for kunde in kunde_list:
        assert required_fields_kunde.issubset(kunde.keys()), f"Kunde data missing fields: {kunde}"
        assert isinstance(kunde["adressen"], list), "Kunde 'adressen' field is not a list."
        for kunden_adresse in kunde["adressen"]:
            assert required_fields_kunden_adresse.issubset(kunden_adresse.keys()), f"Adresse data missing fields: {kunden_adresse}"
            adresse = kunden_adresse["adresse"]
            assert required_fields_adresse.issubset(adresse.keys()), f"Adresse data missing fields: {adresse}"


def test_kunde_get_by_id():
    """Test retrieving a Kunde by kundeId."""
    kunde_id = 1
    response = requests.get(f"{HOST}/kunden?id={kunde_id}", timeout=2)
    assert response.status_code == 200, f"Failed to retrieve Kunde by ID. Code: {response.status_code}"
    kunde = response.json()

    assert kunde["kundeId"] == kunde_id, f"Expected kundeId {kunde_id}, got {kunde['kundeId']}"
    assert required_fields_kunde.issubset(kunde.keys()), f"Kunde data missing fields: {kunde}"
    assert isinstance(kunde["adressen"], list), "Kunde 'adressen' field is not a list."
    for kunden_adresse in kunde["adressen"]:
        assert required_fields_kunden_adresse.issubset(kunden_adresse.keys()), f"Adresse data missing fields: {kunden_adresse}"
        adresse = kunden_adresse["adresse"]
        assert required_fields_adresse.issubset(adresse.keys()), f"Adresse data missing fields: {adresse}"


def test_kunde_get_by_id_max():
    """Test retrieving Kunde Max by kundeId."""
    kunde_id = 1
    response = requests.get(f"{HOST}/kunden?id={kunde_id}", timeout=2)
    kunde = response.json()

    assert kunde["kundeId"] == kunde_id
    assert kunde["vorname"] == "Max"
    assert kunde["nachname"] == "Muster"
    assert kunde["email"] == "123@test.db"


def test_kunde_max_addresses():
    """Test retrieving Max's addresses and verify count."""
    kunde_id = 1
    response = requests.get(f"{HOST}/kunden?id={kunde_id}", timeout=2)
    kunde = response.json()

    assert len(kunde["adressen"]) == 2, f"Expected 2 addresses for Max, got {len(kunde['adressen'])}"
    expected = [
        {
            "adresse": {
                "adresseId": 1,
                "aktiv": True,
                "strasse": "Hauptstrasse",
                "hausnummer": "12",
                "plz": 10115,
                "ort": "Berlin",
                "land": "Deutschland",
            },
            "typ": "Lieferadresse",
        },
        {
            "adresse": {
                "adresseId": 2,
                "aktiv": True,
                "strasse": "Bahnhofweg",
                "hausnummer": "7a",
                "plz": 80331,
                "ort": "Muenchen",
                "land": "Deutschland",
            },
            "typ": "Rechnungsadresse",
        },
    ]

    assert kunde["adressen"] == expected, f"Addresses differ: {kunde['adressen']}"


def test_kunde_get_by_invalid_id():
    """Test retrieving a Kunde with an invalid kundeId."""
    response = requests.get(f"{HOST}/kunden?id={invalid_id}", timeout=2)
    assert response.status_code == 404, f"Expected 404 for invalid kundeId, got {response.status_code}"


def test_kunde_get_by_email():
    """Test retrieving a Kunde by email."""
    email = "123@test.db"
    response = requests.get(f"{HOST}/kunden?email={email}", timeout=2)
    assert response.status_code == 200, f"Failed to retrieve Kunde by email. Code: {response.status_code}"
    kunde = response.json()
    assert kunde["email"] == email, f"Expected email {email}, got {kunde['email']}"
    assert required_fields_kunde.issubset(kunde.keys()), f"Kunde data missing fields: {kunde}"
    for kunden_adresse in kunde["adressen"]:
        assert required_fields_kunden_adresse.issubset(kunden_adresse.keys()), f"Adresse data missing fields: {kunden_adresse}"
        adresse = kunden_adresse["adresse"]
        assert required_fields_adresse.issubset(adresse.keys()), f"Adresse data missing fields: {adresse}"

    assert kunde["vorname"] == "Max"
    assert kunde["nachname"] == "Muster"


def test_kunde_get_by_invalid_email():
    """Test retrieving a Kunde with an invalid email."""
    invalid_email = "invalid_email@invalid.c"
    response = requests.get(f"{HOST}/kunden?email={invalid_email}", timeout=2)
    assert response.status_code == 404, f"Expected 404 for invalid email, got {response.status_code}"


# kunde POST

def test_kunde_post():
    """Test creating a new Kunde."""
    new_kunde = {
        "email": "example@test.db",
        "vorname": "Erika",
        "nachname": "Mustermann",
        "passwort": "StrongPass1?",
    }
    response = requests.post(f"{HOST}/kunden", json=new_kunde, timeout=2)
    assert response.status_code == 201, f"Failed to create Kunde. Code: {response.status_code}"
    created_kunde = response.json()
    assert required_fields_kunde.issubset(created_kunde.keys()), f"Created Kunde data missing fields: {created_kunde}"
    kunde_id = created_kunde["kundeId"]
    get_response = requests.get(f"{HOST}/kunden?id={kunde_id}", timeout=2)
    assert get_response.status_code == 200, f"Failed to retrieve created Kunde. Code: {get_response.status_code}"
    retrieved_kunde = get_response.json()
    assert retrieved_kunde == created_kunde, "Retrieved Kunde does not match created Kunde."
    delete_response = requests.delete(f"{HOST}/kunden?id={kunde_id}", timeout=2) # Code not checked here, not in specifications


# kunde PATCH

def test_kunde_patch_updates():
    """Test updating a Kunde partially."""
    new_kunde = {
        "email": "example2@chungus.com",
        "vorname": "Chungus",
        "nachname": "Big",
        "passwort": "StrongPass2?",
    }
    response = requests.post(f"{HOST}/kunden", json=new_kunde, timeout=2)
    assert response.status_code == 201, f"Failed to create Kunde for update test. Code: {response.status_code}"
    created_kunde = response.json()
    kunde_id = created_kunde["kundeId"]

    updated_email = "chungus@example.com"
    update_data = {"email": updated_email}
    put_response = requests.patch(f"{HOST}/kunden?id={kunde_id}", json=update_data, timeout=2)
    assert put_response.status_code == 200, f"Failed to update Kunde email. Code: {put_response.status_code}"
    updated_kunde = put_response.json()
    assert updated_kunde["email"] == updated_email, f"Expected updated email {updated_email}, got {updated_kunde['email']}"

    updated_vorname = "Big"
    updated_nachname = "Chungus"
    update_data = {"vorname": updated_vorname, "nachname": updated_nachname}
    put_response = requests.patch(f"{HOST}/kunden?id={kunde_id}", json=update_data, timeout=2)
    assert put_response.status_code == 200, f"Failed to update Kunde names. Code: {put_response.status_code}"
    updated_kunde = put_response.json()
    assert updated_kunde["vorname"] == updated_vorname, f"Expected updated vorname {updated_vorname}, got {updated_kunde['vorname']}"
    assert updated_kunde["nachname"] == updated_nachname, f"Expected updated nachname {updated_nachname}, got {updated_kunde['nachname']}"

    updated_passwort = "NewStrongPass3?"
    update_data = {"passwort": updated_passwort}
    put_response = requests.patch(f"{HOST}/kunden?id={kunde_id}", json=update_data, timeout=2)
    assert put_response.status_code == 200, f"Failed to update Kunde password. Code: {put_response.status_code}"
    updated_kunde = put_response.json()
    assert updated_kunde["passwort"] == updated_passwort, f"Expected updated passwort {updated_passwort}, got {updated_kunde['passwort']}"

    delete_response = requests.delete(f"{HOST}/kunden?id={kunde_id}", timeout=2)


# kunde PUT

def test_kunde_put_full_update():
    """Test fully updating a Kunde."""
    new_kunde = {
        "email": "example3@chungus.com",
        "vorname": "Chungus",
        "nachname": "Big",
        "passwort": "StrongPass2?",
    }
    response = requests.post(f"{HOST}/kunden", json=new_kunde, timeout=2)
    assert response.status_code == 201, f"Failed to create Kunde for update test. Code: {response.status_code}"
    created_kunde = response.json()
    kunde_id = created_kunde["kundeId"]

    updated_kunde_data = {
        "email": "updated3@chungus.com",
        "vorname": "UpdatedBig",
        "nachname": "UpdatedChungus",
        "passwort": "NewStrongPass4?",
    }
    put_response = requests.put(f"{HOST}/kunden?id={kunde_id}", json=updated_kunde_data, timeout=2)

    assert put_response.status_code == 200, f"Failed to fully update Kunde. Code: {put_response.status_code}"
    updated_kunde = put_response.json()

    assert updated_kunde["email"] == updated_kunde_data["email"], f"Expected updated email {updated_kunde_data['email']}, got {updated_kunde['email']}"
    assert updated_kunde["vorname"] == updated_kunde_data["vorname"], f"Expected updated vorname {updated_kunde_data['vorname']}, got {updated_kunde['vorname']}"
    assert updated_kunde["nachname"] == updated_kunde_data["nachname"], f"Expected updated nachname {updated_kunde_data['nachname']}, got {updated_kunde['nachname']}"
    assert updated_kunde["passwort"] == updated_kunde_data["passwort"], f"Expected updated passwort {updated_kunde_data['passwort']}, got {updated_kunde['passwort']}"

    delete_response = requests.delete(f"{HOST}/kunden?id={kunde_id}", timeout=2)


# kunde constraints

def test_kunde_invalid_passwords():
    """Test creating Kunden with invalid passwords."""
    for case, password in invalid_passwords.items():
        new_kunde = {
            "email": f"{case}@example.com",
            "vorname": "Test",
            "nachname": "User",
            "passwort": password,
        }
        response = requests.post(f"{HOST}/kunden", json=new_kunde, timeout=2)
        assert response.status_code == 400, f"Expected 400 for invalid password case '{case}', got {response.status_code}"


def test_kunde_duplicate_email():
    """Test creating Kunden with duplicate emails."""
    email = "duplicate@example.com"
    new_kunde = {
        "email": email,
        "vorname": "First",
        "nachname": "User",
        "passwort": "ValidPass1?",
    }
    response1 = requests.post(f"{HOST}/kunden", json=new_kunde, timeout=2)
    assert response1.status_code == 201, f"Failed to create first Kunde. Code: {response1.status_code}"
    response2 = requests.post(f"{HOST}/kunden", json=new_kunde, timeout=2)
    expect_codes = [400, 409]
    assert response2.status_code in expect_codes, f"Expected 400 or 409 for duplicate email, got {response2.status_code}"

    created_kunde = response1.json()
    kunde_id = created_kunde["kundeId"]
    delete_response = requests.delete(f"{HOST}/kunden?id={kunde_id}", timeout=2)


def test_kunde_invalid_email_format():
    """Test creating Kunden with invalid email formats."""
    invalid_emails = ["plainaddress", "at.after@", "nopoint@com", "noat.com", "long" * 256 + "@email.com"]
    for email in invalid_emails:
        new_kunde = {
            "email": email,
            "vorname": "Test",
            "nachname": "User",
            "passwort": "ValidPass1?",
        }
        response = requests.post(f"{HOST}/kunden", json=new_kunde, timeout=2)
        assert response.status_code == 400, f"Expected 400 for invalid email '{email}', got {response.status_code}"


def test_kunde_name_constraints():
    """Test creating Kunden with invalid name lengths."""
    invalid_names = {
        "too_long": "A" * 33,
        "numbers": "John123",
        "special_chars": "Jane@Doe",
    }
    for case, name in invalid_names.items():
        new_kunde = {
            "email": f"{case}@example.com",
            "vorname": name,
            "nachname": "User",
            "passwort": "ValidPass1?",
        }
        response = requests.post(f"{HOST}/kunden", json=new_kunde, timeout=2)
        assert response.status_code == 400, f"Expected 400 for invalid name case '{case}', got {response.status_code}"


def test_kunde_accept_umlauts():
    """Test creating Kunden with names containing umlauts."""
    new_kunde = {
        "email": "umlaut@example.com",
        "vorname": "Jürgen",
        "nachname": "Müller",
        "passwort": "ValidPass1?",
    }
    response = requests.post(f"{HOST}/kunden", json=new_kunde, timeout=2)
    assert response.status_code == 201, f"Expected 201 for valid umlaut name, got {response.status_code}"

    created_kunde = response.json()
    kunde_id = created_kunde["kundeId"]
    delete_response = requests.delete(f"{HOST}/kunden?id={kunde_id}", timeout=2)


def test_kunde_accept_no_uppercase_password():
    """Test creating Kunden with passwords without uppercase letters."""
    new_kunde = {
        "email": "lowercase@example.com",
        "vorname": "Max",
        "nachname": "Mustermann",
        "passwort": "lowercase1?",
    }
    response = requests.post(f"{HOST}/kunden", json=new_kunde, timeout=2)
    assert response.status_code == 201, f"Expected 201 for no uppercase password, got {response.status_code}"

    created_kunde = response.json()
    kunde_id = created_kunde["kundeId"]
    delete_response = requests.delete(f"{HOST}/kunden?id={kunde_id}", timeout=2)
