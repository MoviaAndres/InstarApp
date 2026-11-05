
from django.core.exceptions import ValidationError


def banPalabra(texto):

    PALABRAS_BANEADAS = [
    "imbecil",
    "imbécil",
    "puto",
    "puta",
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
    ]
    ban = False
    for palabra in PALABRAS_RIESGOSAS:
        if palabra.lower() in texto:
            ban = True
    return ban