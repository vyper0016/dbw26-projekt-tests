import requests
from common import HOST, allowed_bestellung_status

required_fields_summe = {"kundeId", "email", "anzahlBestellungen", "gesamtsumme"}
required_fields_verkaufszahlen = {"sku", "name", "gesamtVerkaufteMenge", "umsatz", "anzahlBestellungen"}
required_fields_uebersicht = {'personalNr', 'anzahlVerwalteterBestellungen', 'anzahlAngelegterProdukte'}
required_fields_bestellstatus_uebersicht = {'personalNr', 'status', 'anzahlBestellungen'}

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
    
    # Commented out because deleting a kunde is not a requested feature
    # Make sure the kunde is gone from the report
    #report_response_after_delete = requests.get(f"{HOST}/report/kunde/summe-anzahl-bestellungen")
    #report_data_after_delete = report_response_after_delete.json()
    #for entry in report_data_after_delete:
    #    assert entry["kundeId"] != new_kunde_id, "Deleted kunde should not be present in report"
    
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
    
    # Make sure the produkt is gone from the report
    report_response_after_delete = requests.get(f"{HOST}/report/produkt/verkaufszahlen")
    report_data_after_delete = report_response_after_delete.json()
    for entry in report_data_after_delete:
        assert entry["sku"] != new_produkt_id, "Deleted produkt should not be present in report"
    
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
        
## -- test report/mitarbeiter/uebersicht --

def test_mitarbeiter_uebersicht_status_code():
    response = requests.get(f"{HOST}/report/mitarbeiter/uebersicht")
    assert response.status_code == 200, "Status code is not 200"
    
def test_mitarbeiter_uebersicht_schema():
    response = requests.get(f"{HOST}/report/mitarbeiter/uebersicht")
    data = response.json()
    
    for entry in data:
        assert required_fields_uebersicht.issubset(entry.keys()), f"Missing fields in response: {entry}"
        
def test_all_mitarbeiter_in_uebersicht_report():
    report_response = requests.get(f"{HOST}/report/mitarbeiter/uebersicht")
    report_data = report_response.json()
    mitarbeiter_nrs_in_report = {entry["personalNr"] for entry in report_data}
    for required_nr in range(1, 10+1):
        assert required_nr in mitarbeiter_nrs_in_report, f"Mitarbeiter with personalNr {required_nr} not found in report"
        
def test_mitarbeiter_new_in_uebersicht_report():
    new_mitarbeiter = {
        "passwort": "StrongPass1?",
        "email": "mustermann@exampledb.com",
        "vorname": "Max",
        "nachname": "Mustermann",
    }
    response = requests.post(f"{HOST}/mitarbeiter", json=new_mitarbeiter, timeout=2)
    response.raise_for_status()
    created_mitarbeiter = response.json()
    personal_nr = created_mitarbeiter["personalNr"]
    
    report_response = requests.get(f"{HOST}/report/mitarbeiter/uebersicht")
    report_data = report_response.json()
    for entry in report_data:
        if entry["personalNr"] == personal_nr:
            assert entry["anzahlVerwalteterBestellungen"] == 0, "Newly created mitarbeiter should have 0 verwalteter bestellungen"
            assert entry["anzahlAngelegterProdukte"] == 0, "Newly created mitarbeiter should have 0 angelegter produkte"
        break
    else:
        assert False, "Newly created mitarbeiter not found in report"
    

    # Clean up by deleting the created Mitarbeiter
    delete_response = requests.delete(f"{HOST}/mitarbeiter?id={personal_nr}", timeout=2)
    delete_response.raise_for_status()
    
def test_mitarbeiter_uebersicht_sorted_by_personalNr_asc():
    response = requests.get(f"{HOST}/report/mitarbeiter/uebersicht")
    report_data = response.json()
    
    last_nr = -1
    for entry in report_data:
        current_nr = entry["personalNr"]
        assert current_nr >= last_nr, "Report is not sorted by personalNr in ascending order"
        last_nr = current_nr
        
def test_mitarbeiter_uebersicht_counts_anna():
    response = requests.get(f"{HOST}/report/mitarbeiter/uebersicht")
    report_data = response.json()
    
    for entry in report_data:
        if entry["personalNr"] == 1:  # Anna Meier
            assert entry["anzahlVerwalteterBestellungen"] == 1, "Anna Meier should have 1 verwalteter bestellungen" # from bestellungId 1
            assert entry["anzahlAngelegterProdukte"] == 1, "Anna Meier should have 5 angelegter produkte" # for SKU-1001
            break
    else:
        assert False, "Anna Meier not found in report"
        
## -- test report/mitarbeiter/bestellstatus-uebersicht --

def test_mitarbeiter_bestellstatus_uebersicht_status_code():
    response = requests.get(f"{HOST}/report/mitarbeiter/bestellstatus-uebersicht")
    assert response.status_code == 200, "Status code is not 200"
    
def test_mitarbeiter_bestellstatus_uebersicht_schema():
    response = requests.get(f"{HOST}/report/mitarbeiter/bestellstatus-uebersicht")
    data = response.json()
    
    for entry in data:
        assert required_fields_bestellstatus_uebersicht.issubset(entry.keys()), f"Missing fields in response: {entry}"
        
def test_all_mitarbeiter_in_bestellstatus_uebersicht_report():
    report_response = requests.get(f"{HOST}/report/mitarbeiter/bestellstatus-uebersicht")
    report_data = report_response.json()
    mitarbeiter_nrs_in_report = {entry["personalNr"] for entry in report_data}
    for required_nr in range(1, 10+1):
        assert required_nr in mitarbeiter_nrs_in_report, f"Mitarbeiter with personalNr {required_nr} not found in report"
    
    assert len(report_data) >= 10 * len(allowed_bestellung_status), "Report does not contain expected number of entries"
        
def test_new_mitarbeiter_in_bestellstatus_uebersicht_report():
    new_mitarbeiter = {
        "passwort": "StrongPass1?",
        "email": "mustermann@exampledb.com",
        "vorname": "Max",
        "nachname": "Mustermann",
    }
    response = requests.post(f"{HOST}/mitarbeiter", json=new_mitarbeiter, timeout=2)
    response.raise_for_status()
    created_mitarbeiter = response.json()
    personal_nr = created_mitarbeiter["personalNr"]
    
    report_response = requests.get(f"{HOST}/report/mitarbeiter/bestellstatus-uebersicht")
    report_data = report_response.json()
    
    new_reports = [entry for entry in report_data if entry["personalNr"] == personal_nr]
    assert len(new_reports) == len(allowed_bestellung_status), "Newly created mitarbeiter should have an entry for each allowed status"
    
    for entry in new_reports:
        assert entry["anzahlBestellungen"] == 0, "Newly created mitarbeiter should have 0 bestellungen for each status"
            
    # Clean up by deleting the created Mitarbeiter
    delete_response = requests.delete(f"{HOST}/mitarbeiter?id={personal_nr}", timeout=2)
    delete_response.raise_for_status()
    
    # Make sure the entries are gone after deletion
    report_response_after_delete = requests.get(f"{HOST}/report/mitarbeiter/bestellstatus-uebersicht")
    report_data_after_delete = report_response_after_delete.json()
    for entry in report_data_after_delete:
        assert entry["personalNr"] != personal_nr, "Entries for deleted mitarbeiter should not be present in report"
        
def test_mitarbeiter_bestellstatus_uebersicht_counts_anna():
    response = requests.get(f"{HOST}/report/mitarbeiter/bestellstatus-uebersicht")
    report_data = response.json()
    
    status_counts = {status: 0 for status in allowed_bestellung_status}
    for entry in report_data:
        if entry["personalNr"] == 1:  # Anna Meier
            status_counts[entry["status"]] = entry["anzahlBestellungen"]
    
    assert status_counts["neu"] == 1, "Anna Meier should have 1 'neu' bestellungen" # bestellungId 1
    assert status_counts["bezahlt"] == 0, "Anna Meier should have 0 'bezahlt' bestellungen"
    assert status_counts["versendet"] == 0, "Anna Meier should have 0 'versendet' bestellungen"
    assert status_counts["abgeschlossen"] == 0, "Anna Meier should have 0 'abgeschlossen' bestellungen"
    assert status_counts["storniert"] == 0, "Anna Meier should have 0 'storniert' bestellungen"
    
def test_mitarbeiter_bestellstatus_uebersicht_sorted_by_personalNr_asc():
    response = requests.get(f"{HOST}/report/mitarbeiter/bestellstatus-uebersicht")
    report_data = response.json()
    
    last_nr = -1
    for entry in report_data:
        current_nr = entry["personalNr"]
        assert current_nr >= last_nr, "Report is not sorted by personalNr in ascending order"
        last_nr = current_nr