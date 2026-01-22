import requests
from common import HOST


## -- GENERAL -- ##

def test_connection():
    """Test connection to the local web server."""
    response = requests.get(f"{HOST}/", timeout=2)

    assert response.status_code == 200, f"Failed to connect to the web server. Code: {response.status_code}"
    assert "<!DOCTYPE html>" in response.text, "Response is not a valid HTML document."


def test_connection_swagger():
    """Test connection to the Swagger UI of the web server."""
    response = requests.get(f"{HOST}/swagger-ui/index.html", timeout=2)

    assert response.status_code == 200, f"Failed to connect to the Swagger UI. Code: {response.status_code}"
    assert "<title>Swagger UI</title>" in response.text, "Swagger UI page not found."
