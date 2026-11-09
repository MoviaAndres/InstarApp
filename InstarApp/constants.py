
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
    "semen",
    "xxx",
    "pito",
    "trolo",
    "concha",
    "pussy",
    "pajero",
    "conchudo",
    "conchuda",
    "chupame",
    "chupa me",
    "chupa mie",
    "boludo",
    "pelotudo",
    "idiota",
    "estupido",
    "tarado",
    "forro",
    "concha de tu madre",
    "puto",
    "puta",
    "putita",
    "malparido",
    "bastardo",
    "fracasado",
    "retrasado",
    "mogolico",
    "cagon",
    "verga",
    "pija",
    "concha",
    "culo",
    "pajero",
    "cornudo",
    "sorete",
    "escoria",
    "lacra",
    "maldito",
    "degenerado",
    "pito",
    "trolo",
    ]
    ban = False
    for palabra in PALABRAS_BANEADAS:
        if palabra.lower() in texto:
            ban = True
    return ban


def riesgoPalabra(texto):

    PALABRAS_RIESGOSAS = [
    "cagada",
    "salame",
    "enfermo",
    "asqueroso",
    "rata",
    "perra",
    "zorra",
        "zorete",
        "gil",
        "sexo",
        "muerto",
        "muer",
        "pete",
        "chupa",
        "basura",
        "inutil",
    ]
    ban = False
    for palabra in PALABRAS_RIESGOSAS:
        if palabra.lower() in texto:
            ban = True
    return ban