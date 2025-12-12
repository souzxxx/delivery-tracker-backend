import httpx
from pydantic import BaseModel


class ViaCEPResponse(BaseModel):
    cep: str
    logradouro: str  # street
    complemento: str
    bairro: str  # neighborhood
    localidade: str  # city
    uf: str  # state
    erro: bool = False


class AddressFromCEP(BaseModel):
    """Endereço retornado pelo ViaCEP"""
    cep: str
    street: str
    neighborhood: str
    city: str
    state: str


async def fetch_address_by_cep(cep: str) -> AddressFromCEP | None:
    """
    Busca endereço pelo CEP usando a API ViaCEP (gratuita).
    
    Args:
        cep: CEP no formato "00000000" ou "00000-000"
    
    Returns:
        AddressFromCEP se encontrado, None se CEP inválido
    """
    # Remove caracteres não numéricos
    cep_clean = "".join(filter(str.isdigit, cep))
    
    if len(cep_clean) != 8:
        return None
    
    url = f"https://viacep.com.br/ws/{cep_clean}/json/"
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url)
            response.raise_for_status()
            data = response.json()
            
            # ViaCEP retorna {"erro": true} para CEPs não encontrados
            if data.get("erro"):
                return None
            
            return AddressFromCEP(
                cep=data.get("cep", "").replace("-", ""),
                street=data.get("logradouro", ""),
                neighborhood=data.get("bairro", ""),
                city=data.get("localidade", ""),
                state=data.get("uf", ""),
            )
    except Exception:
        return None

