import requests
from common import HOST

required_fields_summe = {"kundeId", "email", "anzahlBestellungen", "gesamtsumme"}
required_fields_verkaufszahlen = {"sku", "name", "gesamtVerkaufteMenge", "umsatz", "anzahlBestellungen"}


## -- test report/kunde/summe-anzahl-bestellungen --

def test_kunde_summe_anzahl_bestellungen_status_code():
    response = requests.get(f"{HOST}/report/kunde/summe-anzahl-bestellungen")
    assert response.status_code == 200
    
def test_kunde_summe_anzahl_bestellungen_schema():
    response = requests.get(f"{HOST}/report/kunde/summe-anzahl-bestellungen")
    
    for entry in response.json():
        assert required_fields_summe.issubset(entry.keys()), f"Missing fields in response: {entry}"


def test_kunde_ohne_bestellungen_in_report():
    
    new_kunde = {
        "email": "example12@test.db",
        "vorname": "Erika",
        "nachname": "Mustermann",
        "passwort": "StrongPass1?",
    }
    response = requests.post(f"{HOST}/kunden", json=new_kunde, timeout=2)
    new_kunde_id = response.json().get("kundeId")
    
    report_response = requests.get(f"{HOST}/report/kunde/summe-anzahl-bestellungen")
    report_data = report_response.json()
    for entry in report_data:
        if entry["kundeId"] == new_kunde_id:
            assert entry["anzahlBestellungen"] == 0, "Newly created kunde should have 0 bestellungen in report"
            assert entry["gesamtsumme"] == 0.0, "Newly created kunde should have 0.0 gesamtsumme in report"
        break
    else:
        assert False, "Newly created kunde not found in report"
        
    # Cleanup
    requests.delete(f"{HOST}/kunden?id={new_kunde_id}")
    
def test_all_kunden_in_report():
    
    report_response = requests.get(f"{HOST}/report/kunde/summe-anzahl-bestellungen")
    report_data = report_response.json()
    kunde_ids_in_report = {entry["kundeId"] for entry in report_data}
    for required_id in range(1, 10+1):
        assert required_id in kunde_ids_in_report, f"Kunde with ID {required_id} not found in report"

def test_kunde_report_sorted_by_id_asc():
    response = requests.get(f"{HOST}/report/kunde/summe-anzahl-bestellungen")
    report_data = response.json()
    
    last_id = -1
    for entry in report_data:
        current_id = entry["kundeId"]
        assert current_id >= last_id, "Report is not sorted by kundeId in ascending order"
        last_id = current_id
        
def test_kunde_report_first_summe():
    response = requests.get(f"{HOST}/report/kunde/summe-anzahl-bestellungen")
    report_data = response.json()
    
    first_entry = report_data[0]
    
    assert first_entry["kundeId"] == 1, "First kundeId should be 1"
    assert first_entry["gesamtsumme"] == 5*699.99 + 2*1299.00, "First kunde's gesamtsumme does not match expected value"
    
## -- test report/produkt/verkaufszahlen --
def test_produkt_verkaufszahlen_status_code():
    response = requests.get(f"{HOST}/report/produkt/verkaufszahlen")
    assert response.status_code == 200, "Status code is not 200"
    
def test_produkt_verkaufszahlen_schema():
    response = requests.get(f"{HOST}/report/produkt/verkaufszahlen")
    data = response.json()
    
    for entry in data:
        assert required_fields_verkaufszahlen.issubset(entry.keys()), f"Missing fields in response: {entry}"
        
def test_new_produkt_in_verkaufszahlen_report():
    
    new_produkt_id = 'SKU-TEST'
    new_produkt = {
        'sku': new_produkt_id,
        "name": "Test Produkt XYZ",
        "preis": 49.99,
        "lagerbestand": 100,
        'angelegtVon': 1
    }
    response = requests.post(f"{HOST}/produkte", json=new_produkt, timeout=2)
    response.raise_for_status()
    
    report_response = requests.get(f"{HOST}/report/produkt/verkaufszahlen")
    report_data = report_response.json()
    for entry in report_data:
        if entry["sku"] == new_produkt_id:
            assert entry["gesamtVerkaufteMenge"] == 0, "Newly created produkt should have 0 gesamtVerkaufteMenge in report"
            assert entry["umsatz"] == 0.0, "Newly created produkt should have 0.0 umsatz in report"
        break
    else:
        assert False, "Newly created produkt not found in report"
        
    # Cleanup
    requests.delete(f"{HOST}/produkte?sku={new_produkt_id}")
    
def test_all_produkte_in_verkaufszahlen_report():
    report_response = requests.get(f"{HOST}/report/produkt/verkaufszahlen")
    report_data = report_response.json()
    produkt_skus_in_report = {entry["sku"] for entry in report_data}
    for required_sku in range(1001, 1010+1):
        assert f'SKU-{required_sku}' in produkt_skus_in_report, f"Produkt with SKU-{required_sku} not found in report"
        
def test_verkaufszahlen_report_for_neu():
    '''neu Bestellungen should not be counted in the report'''
    
    response = requests.get(f"{HOST}/report/produkt/verkaufszahlen")
    report_data = response.json()
    
    for entry in report_data:
        if entry["sku"] == "SKU-1006":
            assert entry["gesamtVerkaufteMenge"] == 1 # 1 from bestellungId 6 with status 'bezahlt'
            assert entry["umsatz"] == 279.9 
        
def test_verkaufszahlen_report_for_storniert():
    '''storniert Bestellungen should not be counted in the report'''
    
    response = requests.get(f"{HOST}/report/produkt/verkaufszahlen")
    report_data = response.json()
    
    for entry in report_data:
        if entry["sku"] == "SKU-1009":
            assert entry["gesamtVerkaufteMenge"] == 0 # 0 since the only bestellungId 9 with this produkt is 'storniert'
            
def test_verkaufszahlen_report_for_other():
    '''other Bestellungen should be counted in the report'''
    
    response = requests.get(f"{HOST}/report/produkt/verkaufszahlen")
    report_data = response.json()
    
    for entry in report_data:
        if entry["sku"] == "SKU-1010":
            assert entry["gesamtVerkaufteMenge"] == 3 # from bestellungId 2, 6 and 10
            assert entry["umsatz"] == 239.97 # 3 * 79.99
            
def test_verkaufszahlen_report_sorted_by_menge_desc():
    response = requests.get(f"{HOST}/report/produkt/verkaufszahlen")
    report_data = response.json()
    
    last_menge = float('inf')
    for entry in report_data:
        current_menge = entry["gesamtVerkaufteMenge"]
        assert current_menge <= last_menge, "Report is not sorted by gesamtVerkaufteMenge in descending order"
        last_menge = current_menge