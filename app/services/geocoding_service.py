import httpx
from pydantic import BaseModel


class Coordinates(BaseModel):
    latitude: float
    longitude: float


async def geocode_address(
    street: str,
    number: str,
    city: str,
    state: str,
    country: str = "Brazil",
) -> Coordinates | None:
    """
    Converte endereço em coordenadas usando Nominatim (OpenStreetMap).
    
    API gratuita com limite de 1 request/segundo.
    https://nominatim.org/release-docs/develop/api/Search/
    
    Returns:
        Coordinates se encontrado, None se não encontrar
    """
    # Monta query de busca
    query = f"{street}, {number}, {city}, {state}, {country}"
    
    url = "https://nominatim.openstreetmap.org/search"
    params = {
        "q": query,
        "format": "json",
        "limit": 1,
    }
    headers = {
        # Nominatim exige User-Agent identificando a aplicação
        "User-Agent": "DeliveryTracker/1.0 (delivery-tracker-backend)"
    }
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url, params=params, headers=headers)
            response.raise_for_status()
            data = response.json()
            
            if not data:
                return None
            
            result = data[0]
            return Coordinates(
                latitude=float(result["lat"]),
                longitude=float(result["lon"]),
            )
    except Exception:
        return None


async def geocode_by_cep(
    cep: str,
    country: str = "Brazil",
) -> Coordinates | None:
    """
    Busca coordenadas usando apenas o CEP (fallback simples).
    """
    cep_clean = "".join(filter(str.isdigit, cep))
    
    url = "https://nominatim.openstreetmap.org/search"
    params = {
        "postalcode": cep_clean,
        "country": country,
        "format": "json",
        "limit": 1,
    }
    headers = {
        "User-Agent": "DeliveryTracker/1.0 (delivery-tracker-backend)"
    }
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url, params=params, headers=headers)
            response.raise_for_status()
            data = response.json()
            
            if not data:
                return None
            
            result = data[0]
            return Coordinates(
                latitude=float(result["lat"]),
                longitude=float(result["lon"]),
            )
    except Exception:
        return None

