import requests
from common import HOST, invalid_id, required_fields_adresse


## -- Adresse -- ##

def test_adresse_endpoint():
    """Test the Adresse endpoint."""
    response = requests.get(f"{HOST}/adressen", timeout=2)

    assert response.status_code == 200, f"Failed to access Adresse endpoint. Code: {response.status_code}"


def test_adresse_get_all():
    """Test retrieving all Adressen."""
    response = requests.get(f"{HOST}/adressen", timeout=2)

    assert isinstance(response.json(), list), "Response is not a list of Adressen."
    assert len(response.json()) >= 14, "Expected at least 14 Adressen. (data.sql)"


def test_adresse_get_all_schema():
    """Test the schema of the Adresse data."""
    response = requests.get(f"{HOST}/adressen", timeout=2)
    adressen = response.json()

    for adresse in adressen:
        assert required_fields_adresse.issubset(adresse.keys()), f"Adresse data missing fields: {adresse}"


def test_adresse_get_by_id():
    """Test retrieving an Adresse by adresseId."""
    adresse_id = 1
    response = requests.get(f"{HOST}/adressen?id={adresse_id}", timeout=2)
    assert response.status_code == 200, f"Failed to retrieve Adresse by ID. Code: {response.status_code}"
    adresse = response.json()

    expected = {
        "adresseId": adresse_id,
        "aktiv": True,
        "strasse": "Hauptstrasse",
        "hausnummer": "12",
        "plz": 10115,
        "ort": "Berlin",
        "land": "Deutschland",
    }

    assert adresse == expected, f"Adresse differs from expected: {adresse}"


def test_adresse_get_by_invalid_id():
    """Test retrieving an Adresse with an invalid adresseId."""
    response = requests.get(f"{HOST}/adressen?id={invalid_id}", timeout=2)

    assert response.status_code == 404, f"Expected 404 for invalid adresseId, got {response.status_code}"


def test_adresse_post_creates_without_id():
    """Test creating a new Adresse without specifying adresseId."""
    new_adresse = {
        "aktiv": True,
        "strasse": "Teststraße",
        "hausnummer": "99",
        "plz": 54321,
        "ort": "Testort",
        "land": "Testland",
    }

    response = requests.post(f"{HOST}/adressen", json=new_adresse, timeout=2)
    assert response.status_code == 201, f"Failed to create Adresse. Code: {response.status_code}"
    created_adresse = response.json()

    assert required_fields_adresse.issubset(created_adresse.keys()), f"Created Adresse data missing fields: {created_adresse}"
    adresse_id = created_adresse["adresseId"]

    get_response = requests.get(f"{HOST}/adressen?id={adresse_id}", timeout=2)
    assert get_response.status_code == 200, f"Failed to retrieve created Adresse. Code: {get_response.status_code}"
    assert get_response.json() == created_adresse, "Retrieved Adresse does not match created Adresse."

    delete_response = requests.delete(f"{HOST}/adressen?id={adresse_id}", timeout=2)


def test_adresse_put_full_update():
    """Test fully updating an Adresse."""
    new_adresse = {
        "aktiv": True,
        "strasse": "Neustrasse",
        "hausnummer": "50",
        "plz": 123456,
        "ort": "Neuort",
        "land": "Neuland",
    }
    create_response = requests.post(f"{HOST}/adressen", json=new_adresse, timeout=2)
    assert create_response.status_code == 201, f"Failed to create Adresse for update test. Code: {create_response.status_code}"
    created_adresse = create_response.json()
    adresse_id = created_adresse["adresseId"]

    updated_data = {
        "aktiv": False,
        "strasse": "Altstrasse",
        "hausnummer": "51b",
        "plz": 987654,
        "ort": "Altort",
        "land": "Altland",
    }

    put_response = requests.put(f"{HOST}/adressen?id={adresse_id}", json=updated_data, timeout=2)
    assert put_response.status_code == 200, f"Failed to fully update Adresse. Code: {put_response.status_code}"
    updated_adresse = put_response.json()

    assert updated_adresse["aktiv"] is False
    assert updated_adresse["strasse"] == updated_data["strasse"]
    assert updated_adresse["hausnummer"] == updated_data["hausnummer"]
    assert updated_adresse["plz"] == updated_data["plz"]
    assert updated_adresse["ort"] == updated_data["ort"]
    assert updated_adresse["land"] == updated_data["land"]


# adresse constraints

def test_adresse_invalid_strasse():
    """Test creating Adresse with invalid strasse format"""
    invalid_streets = {
        "too_long": "a" * 51,
        "with_numbers": "Strasse123",
        "with_special_chars": "Strasse@Main",
        "capital_in_middle": "mainStreet",
    }
    for case, strasse in invalid_streets.items():
        invalid_adresse = {
            "aktiv": True,
            "strasse": strasse,
            "hausnummer": "12",
            "plz": 12345,
            "ort": "Testort",
            "land": "Testland",
        }
        response = requests.post(f"{HOST}/adressen", json=invalid_adresse, timeout=2)
        assert response.status_code == 400, f"Expected 400 for invalid strasse case '{case}', got {response.status_code}"


def test_adresse_invalid_hausnummer():
    """Test creating Adresse with invalid hausnummer format."""
    invalid_hausnummern = {
        "letters_only": "ABCD",
        "special_chars": "12@#",
        "empty_string": "",
        "too_many_letters": "123ab",
    }
    for case, hausnummer in invalid_hausnummern.items():
        invalid_adresse = {
            "aktiv": True,
            "strasse": "Validstrasse",
            "hausnummer": hausnummer,
            "plz": 12345,
            "ort": "Testort",
            "land": "Testland",
        }
        response = requests.post(f"{HOST}/adressen", json=invalid_adresse, timeout=2)
        assert response.status_code == 400, f"Expected 400 for invalid hausnummer case '{case}', got {response.status_code}"


def test_adresse_invalid_plz():
    """Test creating Adresse with invalid plz format."""
    invalid_plz = {
        "too_long": 100_000_000_000_0,
        "letters_instead_of_numbers": "ABCDE",
        "special_chars": "12@34",
    }
    for case, plz in invalid_plz.items():
        invalid_adresse = {
            "aktiv": True,
            "strasse": "Validstrasse",
            "hausnummer": "12",
            "plz": plz,
            "ort": "Testort",
            "land": "Testland",
        }
        response = requests.post(f"{HOST}/adressen", json=invalid_adresse, timeout=2)
        assert response.status_code == 400, f"Expected 400 for invalid plz case '{case}', got {response.status_code}"


def test_adresse_missing_required_fields():
    """Test creating Adresse with missing required fields."""
    invalid_adresse = {
        "aktiv": True,
        "hausnummer": "12",
        "plz": 12345,
        "ort": "Testort",
        "land": "Testland",
    }
    response = requests.post(f"{HOST}/adressen", json=invalid_adresse, timeout=2)
    assert response.status_code == 400, f"Expected 400 when required fields are missing, got {response.status_code}"
