
from django.core.exceptions import ValidationError


def banPalabra(texto):

    PALABRAS_BANEADAS = [
    "imbecil",
    "puto",
    "puta",
    "porno",
    "pene",
    "nepe",
    "teta",
    "tetas",
    "violacion",
    "pornografia",
    "morite",
    "desvivite",
    "violacion",
    "pornografia",
    "semen",
    "xxx",
    "pito",
    "trolo",
    "concha",
    "pussy",
    "pajero",
    "conchudo",
    "conchuda"
    ]
    ban = False
    for palabra in PALABRAS_BANEADAS:
        if palabra.lower() in texto:
            ban = True
    return ban


def riesgoPalabra(texto):

    PALABRAS_RIESGOSAS = [
        "zorete",
        "gil",
        "sexo",
        "muerto",
        "muer",
        "pete",
    ]
    ban = False
    for palabra in PALABRAS_RIESGOSAS:
        if palabra.lower() in texto:
            ban = True
    return ban