import requests
from common import HOST, invalid_id

def _make_login_payload_mitarbeiter(pnr: int = 1, password: str = "a#123") -> dict:
	return {
        "personalNr": pnr,
        "passwort": password
    }

def _make_login_payload_kunde(email: str = "123@test.db", password: str = "max12!") -> dict:
    return {
        "email": email,
        "passwort": password
    }
    
## -- login/mitarbeiter tests -- ##

return_fields_mitarbeiter = {"personalNr", "email", "vorname", "nachname", "passwort"}

def test_login_mitarbeiter_success():
    """Mitarbeiter can log in with correct credentials."""
    payload = _make_login_payload_mitarbeiter()
    response = requests.post(f"{HOST}/login/mitarbeiter", json=payload, timeout=2)
    assert response.status_code == 200, f"Login failed with status code: {response.status_code}"
    data = response.json()
    assert data['personalNr'] == 1
    assert data['email'] == "anna.meier@firma.db"
    assert data['vorname'] == "Anna"
    assert data['nachname'] == "Meier"
    assert data['passwort'] == None

def test_login_mitarbeiter_wrong_password():
    """Mitarbeiter login fails with incorrect password."""
    payload = _make_login_payload_mitarbeiter(password="wrongpassword")
    response = requests.post(f"{HOST}/login/mitarbeiter", json=payload, timeout=2)
    assert response.status_code == 401, f"Expected 401 for wrong password, got {response.status_code}"
    
    # test return is null fields
    data = response.json()
    for field in data:
        assert field in return_fields_mitarbeiter, f"Unexpected field in response: {field}"
        assert data[field] is None, f"Field {field} should be None on failed login"
    
def test_login_mitarbeiter_nonexistent_user():
    """Mitarbeiter login fails with non-existent personalNr."""
    payload = _make_login_payload_mitarbeiter(pnr=invalid_id)
    response = requests.post(f"{HOST}/login/mitarbeiter", json=payload, timeout=2)
    assert response.status_code == 401, f"Expected 401 for non-existent user, got {response.status_code}"
    
    # test return is null fields
    data = response.json()
    for field in data:
        assert field in return_fields_mitarbeiter, f"Unexpected field in response: {field}"
        assert data[field] is None, f"Field {field} should be None on failed login"
        
        
## -- login/kunde tests -- ##

return_fields_kunde = {"kundeId", "email", "vorname", "nachname", "passwort", "adressen"}

def test_login_kunde_success():
    """Kunde can log in with correct credentials."""
    payload = _make_login_payload_kunde()
    response = requests.post(f"{HOST}/login/kunde", json=payload, timeout=2)
    assert response.status_code == 200, f"Login failed with status code: {response.status_code}"
    data = response.json()
    assert data['kundeId'] == 1
    assert data['email'] == "123@test.db"
    assert data['vorname'] == "Max"
    assert data['nachname'] == "Muster"
    assert data['passwort'] == None
    assert data['adressen'] == []
    
def test_login_kunde_wrong_password():
    """Kunde login fails with incorrect password."""
    payload = _make_login_payload_kunde(password="wrongpassword")
    response = requests.post(f"{HOST}/login/kunde", json=payload, timeout=2)
    assert response.status_code == 401, f"Expected 401 for wrong password, got {response.status_code}"
    
    # test return is null fields
    data = response.json()
    for field in data:
        assert field in return_fields_kunde, f"Unexpected field in response: {field}"
        if field != "adressen":
            assert data[field] is None, f"Field {field} should be None on failed login"
        else:
            assert data[field] == [], f"Field {field} should be empty list on failed login"
        
def test_login_kunde_nonexistent_user():
    """Kunde login fails with non-existent email."""
    payload = _make_login_payload_kunde(email="nonexistent@test.db")
    response = requests.post(f"{HOST}/login/kunde", json=payload, timeout=2)
    assert response.status_code == 401, f"Expected 401 for non-existent user, got {response.status_code}"
    
    # test return is null fields
    data = response.json()
    for field in data:
        assert field in return_fields_kunde, f"Unexpected field in response: {field}"
        if field != "adressen":
            assert data[field] is None, f"Field {field} should be None on failed login"
        else:
            assert data[field] == [], f"Field {field} should be empty list on failed login"