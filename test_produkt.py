import requests
from common import HOST, invalid_sku, required_fields_produkt


## -- Produkt -- ##

def test_produkt_endpoint():
    """Test the Produkt endpoint."""
    response = requests.get(f"{HOST}/produkte", timeout=2)

    assert response.status_code == 200, f"Failed to access Produkt endpoint. Code: {response.status_code}"


def test_produkt_get_all():
    """Test retrieving all Produkte."""
    response = requests.get(f"{HOST}/produkte", timeout=2)

    assert isinstance(response.json(), list), "Response is not a list of Produkte."
    assert len(response.json()) >= 10, "Expected at least 10 Produkte. (data.sql)"


def test_produkt_get_all_schema():
    """Test the schema of the Produkt data."""
    response = requests.get(f"{HOST}/produkte", timeout=2)
    produkte = response.json()

    for produkt in produkte:
        assert required_fields_produkt.issubset(produkt.keys()), f"Produkt data missing fields: {produkt}"


def test_produkt_get_by_sku():
    """Test retrieving a Produkt by sku."""
    sku = "SKU-1002"
    response = requests.get(f"{HOST}/produkte?sku={sku}", timeout=2)
    assert response.status_code == 200, f"Failed to retrieve Produkt by sku. Code: {response.status_code}"
    produkt = response.json()

    expected = {
        "sku": sku,
        "name": "Notebook Pro",
        "preis": 1299.00,
        "lagerbestand": 8,
        "angelegtVon": 2,
    }

    assert produkt == expected, f"Produkt differs from expected: {produkt}"


def test_produkt_get_by_invalid_sku():
    """Test retrieving a Produkt with an invalid sku."""
    response = requests.get(f"{HOST}/produkte?sku={invalid_sku}", timeout=2)
    assert response.status_code == 404, f"Expected 404 for invalid sku, got {response.status_code}"


def test_produkt_post_delete():
    """Test creating and deleting a Produkt."""
    new_produkt = {
        "sku": "SKU-TEST-1",
        "name": "Test Produkt",
        "preis": 99.99,
        "lagerbestand": 5,
        "angelegtVon": 1,
    }
    response = requests.post(f"{HOST}/produkte", json=new_produkt, timeout=2)
    assert response.status_code == 201, f"Failed to create Produkt. Code: {response.status_code}"
    created_produkt = response.json()
    assert required_fields_produkt.issubset(created_produkt.keys()), f"Created Produkt data missing fields: {created_produkt}"

    get_response = requests.get(f"{HOST}/produkte?sku={new_produkt['sku']}", timeout=2)
    assert get_response.status_code == 200, f"Failed to retrieve created Produkt. Code: {get_response.status_code}"
    assert get_response.json() == created_produkt, "Retrieved Produkt does not match created Produkt."

    delete_response = requests.delete(f"{HOST}/produkte?sku={new_produkt['sku']}", timeout=2)
    assert delete_response.status_code == 204, f"Failed to delete Produkt. Code: {delete_response.status_code}"


def test_produkt_patch_lagerbestand_only():
    """Test updating only lagerbestand of a Produkt."""
    sku = "SKU-PATCH-1"
    new_produkt = {
        "sku": sku,
        "name": "Patch Produkt",
        "preis": 49.99,
        "lagerbestand": 3,
        "angelegtVon": 1,
    }
    create_response = requests.post(f"{HOST}/produkte", json=new_produkt, timeout=2)
    assert create_response.status_code == 201, f"Failed to create Produkt for patch test. Code: {create_response.status_code}"

    update_data = {"lagerbestand": 10}
    patch_response = requests.patch(f"{HOST}/produkte?sku={sku}", json=update_data, timeout=2)
    assert patch_response.status_code == 200, f"Failed to patch lagerbestand. Code: {patch_response.status_code}"
    updated_produkt = patch_response.json()

    assert updated_produkt["lagerbestand"] == 10
    assert updated_produkt["name"] == new_produkt["name"]
    assert float(updated_produkt["preis"]) == new_produkt["preis"]
    assert updated_produkt["sku"] == sku
    assert updated_produkt["angelegtVon"] == new_produkt["angelegtVon"]

    delete_response = requests.delete(f"{HOST}/produkte?sku={sku}", timeout=2)
    assert delete_response.status_code == 204, f"Failed to delete Produkt. Code: {delete_response.status_code}"


# produkt constraints

def test_produkt_duplicate_sku_conflict():
    """Test creating Produkte with duplicate sku returns conflict."""
    new_produkt = {
        "sku": "SKU-DUP-1",
        "name": "Duplicate Produkt",
        "preis": 19.99,
        "lagerbestand": 2,
        "angelegtVon": 1,
    }
    first = requests.post(f"{HOST}/produkte", json=new_produkt, timeout=2)
    assert first.status_code == 201, f"Failed to create Produkt for duplicate test. Code: {first.status_code}"

    second = requests.post(f"{HOST}/produkte", json=new_produkt, timeout=2)
    assert second.status_code in (400, 409), f"Expected 400 or 409 for duplicate sku, got {second.status_code}"

    delete_response = requests.delete(f"{HOST}/produkte?sku={new_produkt['sku']}", timeout=2)
    assert delete_response.status_code == 204, f"Failed to delete Produkt. Code: {delete_response.status_code}"


def test_produkt_patch_negative_lagerbestand():
    """Test updating lagerbestand to a negative value returns 400."""
    sku = "SKU-NEG-PATCH"
    new_produkt = {
        "sku": sku,
        "name": "Neg Patch Produkt",
        "preis": 9.99,
        "lagerbestand": 1,
        "angelegtVon": 1,
    }
    create_response = requests.post(f"{HOST}/produkte", json=new_produkt, timeout=2)
    assert create_response.status_code == 201, f"Failed to create Produkt for negative patch test. Code: {create_response.status_code}"

    patch_response = requests.patch(f"{HOST}/produkte?sku={sku}", json={"lagerbestand": -1}, timeout=2)
    assert patch_response.status_code == 400, f"Expected 400 for negative lagerbestand, got {patch_response.status_code}"

    delete_response = requests.delete(f"{HOST}/produkte?sku={sku}", timeout=2)
    assert delete_response.status_code == 204, f"Failed to delete Produkt. Code: {delete_response.status_code}"


def test_produkt_negative_lagerbestand_on_create():
    """Test creating Produkt with negative lagerbestand returns 400."""
    new_produkt = {
        "sku": "SKU-NEG-CREATE",
        "name": "Invalid Produkt",
        "preis": 9.99,
        "lagerbestand": -5,
        "angelegtVon": 1,
    }
    response = requests.post(f"{HOST}/produkte", json=new_produkt, timeout=2)
    assert response.status_code == 400, f"Expected 400 for negative lagerbestand, got {response.status_code}"


def test_produkt_negative_preis():
    """Test creating Produkt with negative preis returns 400."""
    new_produkt = {
        "sku": "SKU-NEG-PREIS",
        "name": "Invalid Preis Produkt",
        "preis": -1.00,
        "lagerbestand": 1,
        "angelegtVon": 1,
    }
    response = requests.post(f"{HOST}/produkte", json=new_produkt, timeout=2)
    assert response.status_code == 400, f"Expected 400 for negative preis, got {response.status_code}"


def test_long_preis():
    """Test creating Produkt with overly long preis returns 400."""
    new_produkt = {
        "sku": "SKU-LONG-PREIS",
        "name": "Long Preis Produkt",
        "preis": 100000000.99,
        "lagerbestand": 1,
        "angelegtVon": 1,
    }
    response = requests.post(f"{HOST}/produkte", json=new_produkt, timeout=2)
    assert response.status_code == 400, f"Expected 400 for overly long preis, got {response.status_code}"
