import requests
from common import HOST, invalid_id, invalid_passwords, required_fields_mitarbeiter


## -- Mitarbeiter -- ##

def test_mitarbeiter_endpoint():
    """Test the Mitarbeiter endpoint."""
    response = requests.get(f"{HOST}/mitarbeiter", timeout=2)

    assert response.status_code == 200, f"Failed to access Mitarbeiter endpoint. Code: {response.status_code}"


def test_mitarbeiter_get_all():
    """Test retrieving all Mitarbeiter."""
    response = requests.get(f"{HOST}/mitarbeiter", timeout=2)

    assert isinstance(response.json(), list), "Response is not a list of Mitarbeiter."
    assert len(response.json()) >= 10, "Expected at least 10 Mitarbeiter. (data.sql)"


def test_mitarbeiter_get_all_schema():
    """Test the schema of the Mitarbeiter data."""
    response = requests.get(f"{HOST}/mitarbeiter", timeout=2)
    mitarbeiter_list = response.json()

    for mitarbeiter in mitarbeiter_list:
        assert required_fields_mitarbeiter.issubset(mitarbeiter.keys()), f"Mitarbeiter data missing fields: {mitarbeiter}"


def test_mitarbeiter_get_by_id():
    """Test retrieving a Mitarbeiter by personalNr."""
    personal_nr = 1
    response = requests.get(f"{HOST}/mitarbeiter?id={personal_nr}", timeout=2)
    assert response.status_code == 200, f"Failed to retrieve Mitarbeiter by ID. Code: {response.status_code}"
    mitarbeiter = response.json()

    assert mitarbeiter["personalNr"] == personal_nr, f"Expected personalNr {personal_nr}, got {mitarbeiter['personalNr']}"
    assert required_fields_mitarbeiter.issubset(mitarbeiter.keys()), f"Mitarbeiter data missing fields: {mitarbeiter}"


def test_mitarbeiter_get_by_id_anna():
    """Test retrieving Mitarbeiter Anna by personalNr."""
    personal_nr = 1
    response = requests.get(f"{HOST}/mitarbeiter?id={personal_nr}", timeout=2)
    mitarbeiter = response.json()

    assert mitarbeiter["personalNr"] == personal_nr
    assert mitarbeiter["vorname"] == "Anna"
    assert mitarbeiter["nachname"] == "Meier"
    assert mitarbeiter["email"] == "anna.meier@firma.db"


def test_mitarbeiter_get_by_invalid_id():
    """Test retrieving a Mitarbeiter with an invalid personalNr."""
    response = requests.get(f"{HOST}/mitarbeiter?id={invalid_id}", timeout=2)
    assert response.status_code == 404, f"Expected 404 for invalid personalNr, got {response.status_code}"


# mitarbeiter POST

def test_mitarbeiter_post_delete():
    """Test creating a new Mitarbeiter."""
    new_mitarbeiter = {
        "passwort": "securePass123?",
        "email": "email@example.com",
        "vorname": "Max",
        "nachname": "Mustermann",
    }
    response = requests.post(f"{HOST}/mitarbeiter", json=new_mitarbeiter, timeout=2)
    assert response.status_code == 201, f"Failed to create Mitarbeiter. Code: {response.status_code}"
    created_mitarbeiter = response.json()
    assert required_fields_mitarbeiter.issubset(created_mitarbeiter.keys()), f"Created Mitarbeiter data missing fields: {created_mitarbeiter}"
    personal_nr = created_mitarbeiter["personalNr"]

    # Verify the Mitarbeiter was created
    get_response = requests.get(f"{HOST}/mitarbeiter?id={personal_nr}", timeout=2)
    assert get_response.status_code == 200, f"Failed to retrieve created Mitarbeiter. Code: {get_response.status_code}"
    retrieved_mitarbeiter = get_response.json()
    assert retrieved_mitarbeiter == created_mitarbeiter, "Retrieved Mitarbeiter does not match created Mitarbeiter."

    # Clean up by deleting the created Mitarbeiter
    delete_response = requests.delete(f"{HOST}/mitarbeiter?id={personal_nr}", timeout=2)
    assert delete_response.status_code == 204, f"Failed to delete Mitarbeiter. Code: {delete_response.status_code}"


# mitarbeiter constraints

def test_mitarbeiter_invalid_passwords():
    """Test creating Mitarbeiter with invalid passwords."""
    for case, password in invalid_passwords.items():
        new_mitarbeiter = {
            "passwort": password,
            "email": f"{case}@example.com",
            "vorname": "Max",
            "nachname": "Mustermann",
        }
        response = requests.post(f"{HOST}/mitarbeiter", json=new_mitarbeiter, timeout=2)
        assert response.status_code == 400, f"Expected 400 for case {case}, got {response.status_code}"


def test_mitarbeiter_accept_no_uppercase_password():
    """Test creating Mitarbeiter with passwords without uppercase letters."""
    new_mitarbeiter = {
        "passwort": "lowercase1?",
        "email": "lowercase@example.com",
        "vorname": "Max",
        "nachname": "Mustermann",
    }
    response = requests.post(f"{HOST}/mitarbeiter", json=new_mitarbeiter, timeout=2)
    assert response.status_code == 201, f"Expected 201 for no uppercase password, got {response.status_code}"

    # Clean up by deleting the created Mitarbeiter
    created_mitarbeiter = response.json()
    personal_nr = created_mitarbeiter["personalNr"]
    delete_response = requests.delete(f"{HOST}/mitarbeiter?id={personal_nr}", timeout=2)
    assert delete_response.status_code == 204, f"Failed to delete Mitarbeiter. Code: {delete_response.status_code}"
