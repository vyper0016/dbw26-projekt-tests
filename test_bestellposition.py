import requests
from common import HOST, invalid_id, required_fields_bestellposition


## -- Bestellposition -- ##

def test_bestellposition_endpoint():
    """Test the Bestellposition endpoint."""
    response = requests.get(f"{HOST}/bestellpositionen", timeout=2)

    assert response.status_code == 200, f"Failed to access Bestellposition endpoint. Code: {response.status_code}"


def test_bestellposition_get_all():
    """Test retrieving all Bestellpositionen."""
    response = requests.get(f"{HOST}/bestellpositionen", timeout=2)

    assert isinstance(response.json(), list), "Response is not a list of Bestellpositionen."
    assert len(response.json()) >= 10, "Expected at least 10 Bestellpositionen. (data.sql)"


def test_bestellposition_get_all_schema():
    """Test the schema of the Bestellposition data."""
    response = requests.get(f"{HOST}/bestellpositionen", timeout=2)
    bestellpositionen = response.json()

    for pos in bestellpositionen:
        assert required_fields_bestellposition.issubset(pos.keys()), f"Bestellposition data missing fields: {pos}"


def test_bestellposition_get_by_id():
    """Test retrieving a Bestellposition by positionsId."""
    position_id = 1
    response = requests.get(f"{HOST}/bestellpositionen?id={position_id}", timeout=2)
    assert response.status_code == 200, f"Failed to retrieve Bestellposition by ID. Code: {response.status_code}"
    pos = response.json()

    assert pos["positionsId"] == position_id
    assert required_fields_bestellposition.issubset(pos.keys()), f"Bestellposition data missing fields: {pos}"


def test_first_bestellposition_details():
    """Test the details of the first Bestellposition."""
    position_id = 1
    response = requests.get(f"{HOST}/bestellpositionen?id={position_id}", timeout=2)
    assert response.status_code == 200, f"Failed to retrieve Bestellposition by ID. Code: {response.status_code}"
    pos = response.json()

    expected = {
        "positionsId": 1,
        "bestellungId": 1,
        "produktSku": "SKU-1001",
        "menge": 5,
        "gesamtpreis": 699.99 * 5,
    }

    assert pos == expected, f"Bestellposition differs from expected: {pos}"


def test_bestellposition_get_by_invalid_id():
    """Test retrieving a Bestellposition with an invalid positionsId."""
    response = requests.get(f"{HOST}/bestellpositionen?id={invalid_id}", timeout=2)
    assert response.status_code == 404, f"Expected 404 for invalid positionsId, got {response.status_code}"


def test_bestellposition_post_delete():
    """Test creating and deleting a Bestellposition with auto-calculated gesamtpreis."""
    produkt_response = requests.get(f"{HOST}/produkte?sku=SKU-1002", timeout=2)
    assert produkt_response.status_code == 200, "Failed to retrieve product for test."
    produkt = produkt_response.json()
    produkt_preis = float(produkt["preis"])

    new_position = {"bestellungId": 1, "produktSku": "SKU-1002", "menge": 3}

    response = requests.post(f"{HOST}/bestellpositionen", json=new_position, timeout=2)
    assert response.status_code == 201, f"Failed to create Bestellposition. Code: {response.status_code}"
    created_position = response.json()
    assert required_fields_bestellposition.issubset(created_position.keys()), f"Created Bestellposition data missing fields: {created_position}"

    expected_gesamtpreis = new_position["menge"] * produkt_preis
    actual_gesamtpreis = float(created_position["gesamtpreis"])
    assert abs(actual_gesamtpreis - expected_gesamtpreis) < 0.01, f"Expected gesamtpreis {expected_gesamtpreis}, got {actual_gesamtpreis}"

    position_id = created_position["positionsId"]
    get_response = requests.get(f"{HOST}/bestellpositionen?id={position_id}", timeout=2)
    assert get_response.status_code == 200, f"Failed to retrieve created Bestellposition. Code: {get_response.status_code}"
    assert get_response.json() == created_position, "Retrieved Bestellposition does not match created Bestellposition."

    delete_response = requests.delete(f"{HOST}/bestellpositionen?id={position_id}", timeout=2)
    assert delete_response.status_code == 204, f"Failed to delete Bestellposition. Code: {delete_response.status_code}"


def test_bestellposition_invalid_bestellung_id():
    """Test creating Bestellposition with invalid bestellungId returns conflict."""
    new_position = {"bestellungId": 99999, "produktSku": "SKU-1002", "menge": 1}
    response = requests.post(f"{HOST}/bestellpositionen", json=new_position, timeout=2)
    assert response.status_code in (400, 409), f"Expected 400 or 409 for invalid bestellungId, got {response.status_code}"


def test_bestellposition_invalid_produkt_sku():
    """Test creating Bestellposition with invalid produktSku returns conflict."""
    new_position = {"bestellungId": 1, "produktSku": "INVALID-SKU", "menge": 1}
    response = requests.post(f"{HOST}/bestellpositionen", json=new_position, timeout=2)
    assert response.status_code in (400, 409), f"Expected 400 or 409 for invalid produktSku, got {response.status_code}"

    
def test_bestellposition_zero_menge():
    """Test creating Bestellposition with zero menge returns 400."""
    new_position = {"bestellungId": 1, "produktSku": "SKU-1002", "menge": 0}
    response = requests.post(f"{HOST}/bestellpositionen", json=new_position, timeout=2)
    assert response.status_code == 400, f"Expected 400 for zero menge, got {response.status_code}"


def test_bestellposition_negative_menge():
    """Test creating Bestellposition with negative menge returns 400."""
    new_position = {"bestellungId": 1, "produktSku": "SKU-1002", "menge": -5}
    response = requests.post(f"{HOST}/bestellpositionen", json=new_position, timeout=2)
    assert response.status_code == 400, f"Expected 400 for negative menge, got {response.status_code}"


def test_bestellposition_missing_required_fields():
    """Test creating Bestellposition with missing required fields."""
    invalid_positions = [
        {"produktSku": "SKU-1002", "menge": 1},
        {"bestellungId": 1, "menge": 1},
        {"bestellungId": 1, "produktSku": "SKU-1002"},
    ]
    for invalid_pos in invalid_positions:
        response = requests.post(f"{HOST}/bestellpositionen", json=invalid_pos, timeout=2)
        assert response.status_code == 400, f"Expected 400 for missing fields in {invalid_pos}, got {response.status_code}"

# Triggers

def test_bestellposition_order_more_than_lagerbestand():
    """Test creating Bestellposition with menge exceeding lagerbestand returns Error."""
    produkt_response = requests.get(f"{HOST}/produkte?sku=SKU-1003", timeout=2)
    assert produkt_response.status_code == 200, "Failed to retrieve product for test."
    produkt = produkt_response.json()
    lagerbestand = int(produkt["lagerbestand"])

    new_position = {"bestellungId": 1, "produktSku": "SKU-1003", "menge": lagerbestand + 1}
    response = requests.post(f"{HOST}/bestellpositionen", json=new_position, timeout=2)
    assert response.status_code in (400, 409), f"Expected 400 or 409 for menge exceeding lagerbestand, got {response.status_code}"
    
def test_bestellposition_lagerbestand_decreased():
    '''On bestellposition insert, the corresponding product lagerbestand is decreased.'''
    produkt_sku = "SKU-1005"
    menge = 2
    produkt_response = requests.get(f"{HOST}/produkte?sku={produkt_sku}", timeout=2)
    assert produkt_response.status_code == 200, "Failed to retrieve product for test."
    produkt = produkt_response.json()
    initial_lagerbestand = int(produkt["lagerbestand"])
    new_position = {"bestellungId": 1, "produktSku": produkt_sku, "menge": menge}
    response = requests.post(f"{HOST}/bestellpositionen", json=new_position, timeout=2)
    assert response.status_code == 201, f"Failed to create Bestellposition. Code: {response.status_code}"
    position_id = response.json()["positionsId"]
    produkt_response_after = requests.get(f"{HOST}/produkte?sku={produkt_sku}", timeout=2)
    assert produkt_response_after.status_code == 200, "Failed to retrieve product after creating Bestellposition."
    produkt_after = produkt_response_after.json()
    updated_lagerbestand = int(produkt_after["lagerbestand"])
    assert updated_lagerbestand == initial_lagerbestand - menge, f"Lagerbestand not decreased correctly. Expected {initial_lagerbestand - menge}, got {updated_lagerbestand}"
    
    # Cleanup
    delete_response = requests.delete(f"{HOST}/bestellpositionen?id={position_id}", timeout=2)
    assert delete_response.status_code == 204, f"Failed to delete Bestellposition. Code: {delete_response.status_code}"

    
def test_bestellposition_lagerbestand_restored_on_delete():
    '''If a bestellposition is deleted or bestellung set to "storniert", the corresponding product lagerbestand is increased.'''
    # assumes bestellungId 5, 
    # SKU-1005 increases lagerbestand by 3 on deletion
    # SKU-1001 increases lagerbestand by 2 on deletion
    # deletes positions and checks lagerbestand restoration
    
    bestellung_id = 5
    produkt_skus_mengen = [("SKU-1005", 3), ("SKU-1001", 2)]
    initial_bestellung_response = requests.get(f"{HOST}/bestellungen?id={bestellung_id}", timeout=2)
    assert initial_bestellung_response.status_code == 200, f"Failed to retrieve Bestellung {bestellung_id} for test."
    initial_bestellung = initial_bestellung_response.json()
    
    for produkt_sku, menge in produkt_skus_mengen:
        produkt_response = requests.get(f"{HOST}/produkte?sku={produkt_sku}", timeout=2)
        assert produkt_response.status_code == 200, "Failed to retrieve product for test."
        produkt = produkt_response.json()
        initial_lagerbestand = int(produkt["lagerbestand"])

        position_response = requests.get(f"{HOST}/bestellpositionen", timeout=2)
        assert position_response.status_code == 200, "Failed to retrieve Bestellpositionen for test."
        position_id = next((p["positionsId"] for p in position_response.json() if p["bestellungId"] == bestellung_id and p["produktSku"] == produkt_sku), None)
        assert position_id is not None, f"Failed to find Bestellposition for {produkt_sku} in Bestellung {bestellung_id}."

        delete_response = requests.delete(f"{HOST}/bestellpositionen?id={position_id}", timeout=2)
        assert delete_response.status_code == 204, f"Failed to delete Bestellposition {position_id}. Code: {delete_response.status_code}"

        produkt_response_after = requests.get(f"{HOST}/produkte?sku={produkt_sku}", timeout=2)
        assert produkt_response_after.status_code == 200, "Failed to retrieve product after deletion."
        produkt_after = produkt_response_after.json()
        updated_lagerbestand = int(produkt_after["lagerbestand"])
        assert updated_lagerbestand == initial_lagerbestand + menge, f"Lagerbestand not restored correctly for {produkt_sku}. Expected {initial_lagerbestand + menge}, got {updated_lagerbestand}"
        
    # Restore the deleted bestellposition for test idempotency
    for produkt_sku, menge in produkt_skus_mengen:
        new_position = {"bestellungId": bestellung_id, "produktSku": produkt_sku, "menge": menge}
        response = requests.post(f"{HOST}/bestellpositionen", json=new_position, timeout=2)
        assert response.status_code == 201, f"Failed to recreate Bestellposition for {produkt_sku}. Code: {response.status_code}"
        