import requests
from common import HOST, required_fields_bestellung, required_fields_produkt, allowed_bestellung_status

# AI GENERATED NOT AUDITED
## -- Bestellung -- ##


position_required_fields = {"positionsId", "bestellungId", "produkt", "menge", "gesamtpreis"}

def _make_bestellung_payload(status="neu"):
	return {
		"kundeId": 1,
		"personalNr": 1,
		"datum": "2024-01-19T14:05:00Z",
		"status": status,
	}


def test_bestellung_endpoint():
	"""Bestellungen endpoint should be reachable."""
	response = requests.get(f"{HOST}/bestellungen", timeout=2)
	assert response.status_code == 200, f"Failed to access Bestellungen endpoint. Code: {response.status_code}"


def test_bestellung_get_all():
	"""Retrieving all Bestellungen returns a list with entries."""
	response = requests.get(f"{HOST}/bestellungen", timeout=2)
	bestellungen = response.json()

	assert isinstance(bestellungen, list), "Response is not a list of Bestellungen."
	assert len(bestellungen) >= 10, "Expected at least 10 Bestellungen (data.sql)."


def test_bestellung_get_all_schema():
	"""All Bestellungen expose the expected schema including positionen list."""
	response = requests.get(f"{HOST}/bestellungen", timeout=2)
	bestellungen = response.json()

	for bestellung in bestellungen:
		for required_field in required_fields_bestellung:
			assert required_field in bestellung, f"Bestellung missing field: {required_field}"
		assert required_fields_bestellung.issubset(bestellung.keys()), f"Bestellung data missing fields: {bestellung}"
		assert isinstance(bestellung["positionen"], list), "Bestellung 'positionen' is not a list."
		for position in bestellung["positionen"]:
			assert position_required_fields.issubset(position.keys()), f"Position data missing fields: {position}"
			if "produkt" in position:
				assert required_fields_produkt.issubset(position["produkt"].keys()), f"Produkt data missing fields: {position['produkt']}"


def test_bestellung_get_by_id():
	"""A single Bestellung can be fetched by id parameter."""
	bestellung_id = 1
	response = requests.get(f"{HOST}/bestellungen?id={bestellung_id}", timeout=2)
	assert response.status_code == 200, f"Failed to retrieve Bestellung by ID. Code: {response.status_code}"
	bestellung = response.json()

	assert bestellung["bestellungId"] == bestellung_id
	assert bestellung['kundeId'] == 1
	assert bestellung['personalNr'] == 1
	assert "2026-01-10" in bestellung['datum']
	assert bestellung['status'] == "neu"


def test_bestellung_status_values():
	"""All existing Bestellungen use allowed status values."""
	response = requests.get(f"{HOST}/bestellungen", timeout=2)
	bestellungen = response.json()

	for bestellung in bestellungen:
		assert bestellung["status"] in allowed_bestellung_status, f"Invalid status found: {bestellung['status']}"


def test_bestellung_post_delete():
	"""Create a Bestellung with required fields and delete it again."""
	payload = _make_bestellung_payload(status="neu")
	create_response = requests.post(f"{HOST}/bestellungen", json=payload, timeout=2)
	assert create_response.status_code == 201, f"Failed to create Bestellung. Code: {create_response.status_code}"
	created_bestellung = create_response.json()
	bestellung_id = created_bestellung["bestellungId"]

	assert required_fields_bestellung.issubset(created_bestellung.keys()), f"Created Bestellung missing fields: {created_bestellung}"
	assert created_bestellung["status"] == payload["status"]
	assert created_bestellung["kundeId"] == payload["kundeId"]
	assert created_bestellung["personalNr"] == payload["personalNr"]
	assert isinstance(created_bestellung.get("positionen", []), list)

	get_response = requests.get(f"{HOST}/bestellungen?id={bestellung_id}", timeout=2)
	assert get_response.status_code == 200, f"Failed to retrieve created Bestellung. Code: {get_response.status_code}"
	assert get_response.json() == created_bestellung, "Retrieved Bestellung does not match created Bestellung."

	delete_response = requests.delete(f"{HOST}/bestellungen?id={bestellung_id}", timeout=2)
	assert delete_response.status_code == 204, f"Failed to delete Bestellung. Code: {delete_response.status_code}"


def test_bestellung_missing_required_fields():
	"""Creating a Bestellung without all required fields returns 400."""
	invalid_payloads = [
		{"personalNr": 1, "datum": "2024-01-19T14:05:00Z", "status": "neu"},
		{"kundeId": 1, "datum": "2024-01-19T14:05:00Z", "status": "neu"},
		{"kundeId": 1, "personalNr": 1, "status": "neu"},
		{"kundeId": 1, "personalNr": 1, "datum": "2024-01-19T14:05:00Z"},
	]
	for payload in invalid_payloads:
		response = requests.post(f"{HOST}/bestellungen", json=payload, timeout=2)
		assert response.status_code == 400, f"Expected 400 for invalid payload {payload}, got {response.status_code}"


def test_bestellung_invalid_status_on_create():
	"""Status must be within the allowed set when creating a Bestellung."""
	payload = _make_bestellung_payload(status="unbekannt")
	response = requests.post(f"{HOST}/bestellungen", json=payload, timeout=2)
	assert response.status_code == 400, f"Expected 400 for invalid status, got {response.status_code}"

def test_bestellung_wartend_status_on_create():
	"""Status must be within the allowed set when creating a Bestellung."""
	payload = _make_bestellung_payload(status="wartend")
	response = requests.post(f"{HOST}/bestellungen", json=payload, timeout=2)
	assert response.status_code == 400, f"Expected 400 for invalid status, got {response.status_code}"

