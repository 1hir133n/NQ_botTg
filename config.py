from pathlib import Path
import os

BASE_DIR = Path(__file__).parent.resolve()

def make_abs(path):
    return str(BASE_DIR / path)

COMPROBANTE1_CONFIG = {
    "template": make_abs("img/plantilla1.jpg"),
    "output": make_abs("comprobante1_generado.png"),
    "styles": {
        "nombre": {"size": 22, "color": "#200021", "pos": (48, 600)},
        "telefono": {"size": 22, "color": "#200021", "pos": (48, 765)},
        "valor1": {"size": 22, "color": "#200021", "pos": (48, 683)},
        "fecha": {"size": 22, "color": "#200021", "pos": (48, 850)},
        "referencia": {"size": 22, "color": "#200021", "pos": (48, 935)},
        "disponible": {"size": 22, "color": "#200021", "pos": (48, 1023)},
    },
    "font": make_abs("fuentes/Manrope-Medium.ttf"),
}

COMPROBANTE4_CONFIG = {
    "template": make_abs("img/plantilla4.jpg"),
    "output": make_abs("comprobante4_generado.png"),
    "styles": {
        "telefono": {"size": 22, "color": "#200021", "pos": (47, 262)},
        "valor1": {"size": 22, "color": "#200021", "pos": (47, 342)},
        "fecha": {"size": 22, "color": "#200021", "pos": (47, 423)},
        "referencia": {"size": 22, "color": "#200021", "pos": (47, 500)},
        "disponible": {"size": 22, "color": "#200021", "pos": (47, 580)},
    },
    "font": make_abs("fuentes/Manrope-Medium.ttf")
}

COMPROBANTE_MOVIMIENTO_CONFIG = {
    "template": make_abs("img/comprobante_movimiento.jpg"),
    "output": make_abs("comprobante_movimiento_generado.png"),
    "styles": {
        "nombre": {"size": 18, "color": "#1b0b19", "pos": (87, 324), "font": make_abs("fuentes/Manrope-Medium.ttf")},
        "valor1": {"size": 21, "color": "#D32F2F", "pos": (450, 333), "max_width": 200, "font": make_abs("fuentes/Manrope-Bold.ttf")},
        "valor_decimal": {"size": 26, "color": "#D32F2F", "pos": (0, 0), "font": make_abs("fuentes/Manrope-Bold.ttf")},
    },
    "font": make_abs("fuentes/Manrope-Medium.ttf"),
}

COMPROBANTE_MOVIMIENTO2_CONFIG = {
    "template": make_abs("img/plantilla2.jpg"),
    "output": make_abs("comprobante_movimiento2_generado.png"),
    "styles": {
        "nombre": {"size": 18, "color": "#1b0b19", "pos": (87, 324), "font": make_abs("fuentes/Manrope-Medium.ttf")},
        "valor1": {"size": 21, "color": "#D32F2F", "pos": (450, 333), "max_width": 200, "font": make_abs("fuentes/Manrope-Bold.ttf")},
        "valor_decimal": {"size": 26, "color": "#D32F2F", "pos": (0, 0), "font": make_abs("fuentes/Manrope-Bold.ttf")},
    },
    "font": make_abs("fuentes/Manrope-Medium.ttf"),
}

COMPROBANTE_QR_CONFIG = {
    "template": make_abs("img/plantilla_qr.jpg"),
    "output": make_abs("comprobante_qr_generado.png"),
    "styles": {
        "nombre": {"size": 40, "color": "#2e2b33", "pos": (230, 1180)},       # Debajo de "Para"
        "llave": {"size": 40, "color": "#2e2b33", "pos": (230, 1260)},        # Debajo de "Llave"
        "banco_destino": {"size": 40, "color": "#2e2b33", "pos": (230, 1340)}, # Debajo de "Banco destino"
        "valor1": {"size": 40, "color": "#2e2b33", "pos": (230, 1420)},       # Debajo de "¿Cuánto?"
        "fecha": {"size": 40, "color": "#2e2b33", "pos": (230, 1500)},        # Debajo de "Fecha"
        "referencia": {"size": 40, "color": "#2e2b33", "pos": (230, 1580)},   # Debajo de "Referencia"
        "origen_envio": {"size": 40, "color": "#2e2b33", "pos": (230, 1660)}, # Debajo de "Desde donde se hizo el envío"
        "disponible": {"size": 40, "color": "#2e2b33", "pos": (230, 1740)}    # Debajo de "¿De dónde salió la plata?"
    },
    "font": make_abs("fuentes/Manrope-Medium.ttf"),
}

COMPROBANTE_MOVIMIENTO3_CONFIG = {
    "template": make_abs("img/comprobante_movimiento3.jpg"),
    "output": make_abs("comprobante_movimiento3_generado.png"),
    "styles": {
        "nombre": {"size": 18, "color": "#1b0b19", "pos": (87, 324), "font": make_abs("fuentes/Manrope-Medium.ttf")},
        "valor1": {"size": 21, "color": "#b14253", "pos": (450, 333), "max_width": 200, "font": make_abs("fuentes/Manrope-Bold.ttf")},
        "valor_decimal": {"size": 26, "color": "#b14253", "pos": (0, 0), "font": make_abs("fuentes/Manrope-Bold.ttf")},
    },
    "font": make_abs("fuentes/Manrope-Medium.ttf")
}