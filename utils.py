from PIL import Image, ImageDraw, ImageFont
from datetime import datetime
import uuid
import random
import os  # ← Importante para verificar rutas

# --- IMPORTACIÓN SEGURA DE PYTZ ---
try:
    import pytz
    BOGOTA_TZ = pytz.timezone("America/Bogota")
except ImportError:
    BOGOTA_TZ = None

# --- FUNCIÓN AUXILIAR: OBTENER FECHA EN ESPAÑOL ---
def obtener_fecha_es():
    meses_es = {
        "january": "enero", "february": "febrero", "march": "marzo", "april": "abril",
        "may": "mayo", "june": "junio", "july": "julio", "august": "agosto",
        "september": "septiembre", "october": "octubre", "november": "noviembre", "december": "diciembre"
    }
    try:
        if BOGOTA_TZ:
            now = datetime.now(BOGOTA_TZ)
        else:
            now = datetime.utcnow()
        mes_en = now.strftime("%B").lower()
        mes = meses_es.get(mes_en, mes_en)
        fecha = now.strftime(f"%d de {mes} de %Y a las %I:%M %p").lower().replace("am", "a. m.").replace("pm", "p. m.")
        return fecha
    except:
        return datetime.utcnow().strftime("%d/%m/%Y %I:%M %p")

def draw_text_with_outline(draw, position, text, font, fill, outline_fill="white", outline_width=2):
    x, y = position
    for dx in range(-outline_width, outline_width + 1):
        for dy in range(-outline_width, outline_width + 1):
            if dx != 0 or dy != 0:
                draw.text((x + dx, y + dy), text, font=font, fill=outline_fill)
    draw.text((x, y), text, font=font, fill=fill)

def dibujar_valor_movimiento(draw, base_style, valor, font_path, ancho_imagen, decimal_style=None):
    try:
        valor_formateado = f"{abs(valor):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        valor_str = f"-$ {valor_formateado}" if valor < 0 else f"$ {valor_formateado}"
        entero, decimal = valor_str[:-3], valor_str[-3:]

        pos_y = base_style["pos"][1]
        limite_izquierdo = 100
        limite_derecho = 580
        margen_derecho = 20

        size_entero = base_style["size"]
        size_decimal = int(size_entero * 0.75)

        font_entero = ImageFont.truetype(base_style.get("font", font_path), size_entero)
        font_decimal = ImageFont.truetype(
            decimal_style.get("font", font_path) if decimal_style else font_path,
            size_decimal
        )

        ancho_entero = draw.textlength(entero, font=font_entero)
        ancho_decimal = draw.textlength(decimal, font=font_decimal)

        while (ancho_entero + ancho_decimal) > (limite_derecho - limite_izquierdo - margen_derecho) and size_entero > 8:
            size_entero -= 1
            size_decimal = int(size_entero * 0.75)
            font_entero = ImageFont.truetype(base_style.get("font", font_path), size_entero)
            font_decimal = ImageFont.truetype(
                decimal_style.get("font", font_path) if decimal_style else font_path,
                size_decimal
            )
            ancho_entero = draw.textlength(entero, font=font_entero)
            ancho_decimal = draw.textlength(decimal, font=font_decimal)

        x_decimal = limite_derecho - margen_derecho
        x_entero = x_decimal - ancho_entero

        if x_entero < limite_izquierdo:
            x_entero = limite_izquierdo
            x_decimal = x_entero + ancho_entero

        x_entero -= 13
        x_decimal -= 13

        bbox_entero = font_entero.getbbox("0")
        bbox_decimal = font_decimal.getbbox("0")
        offset_y = bbox_entero[3] - bbox_decimal[3]
        decimal_y = pos_y + offset_y

        draw_text_with_outline(draw, (x_entero, pos_y), entero, font_entero, base_style["color"], "white", 2)
        draw.text((x_decimal, decimal_y), decimal, font=font_decimal, fill=decimal_style.get("color", base_style["color"]) if decimal_style else base_style["color"])
    except Exception:
        fallback_font = ImageFont.load_default()
        draw.text((base_style["pos"][0], base_style["pos"][1]), str(valor), font=fallback_font, fill=base_style["color"])

def generar_comprobante(data, config):
    template_path = config["template"]
    font_path = config["font"]
    styles = config["styles"]

    # ✅ VERIFICACIÓN CRÍTICA: ¿EXISTEN LOS ARCHIVOS?
    if not os.path.exists(template_path):
        raise FileNotFoundError(f"❌ PLANTILLA NO ENCONTRADA: {template_path}")
    if not os.path.exists(font_path):
        raise FileNotFoundError(f"❌ FUENTE NO ENCONTRADA: {font_path}")

    # Cargar imagen
    image = Image.open(template_path).convert("RGB")
    draw = ImageDraw.Draw(image)

    # Detectar tipo
    tipo_movimiento = "valor1" in styles and "nombre" in styles and "valor_decimal" in styles
    es_comprobante_qr = config.get("output", "").endswith("comprobante_qr_generado.png")
    es_comprobante4 = config.get("output", "").endswith("comprobante4_generado.png")

    if tipo_movimiento:
        # --- MOVIMIENTO ---
        decimal_style = styles.get("valor_decimal")
        dibujar_valor_movimiento(draw, styles["valor1"], data["valor"], font_path, image.width, decimal_style)
        try:
            font_nombre = ImageFont.truetype(styles["nombre"].get("font", font_path), styles["nombre"]["size"])
            draw_text_with_outline(draw, styles["nombre"]["pos"], data["nombre"], font_nombre, styles["nombre"]["color"])
        except:
            fallback_font = ImageFont.load_default()
            draw.text(styles["nombre"]["pos"], data["nombre"], font=fallback_font, fill=styles["nombre"]["color"])
    else:
        # --- COMPROBANTE NORMAL ---
        fecha = obtener_fecha_es()
        valor = data["valor"]
        valor_formateado = "$ {:,.2f}".format(valor).replace(",", "X").replace(".", ",").replace("X", ".")

        telefono_raw = data.get("telefono", "")
        telefono_formateado = (
            telefono_raw if es_comprobante4 or es_comprobante_qr else
            f"{telefono_raw[:3]} {telefono_raw[3:6]} {telefono_raw[6:]}" if telefono_raw.isdigit() and len(telefono_raw) == 10 else telefono_raw
        )

        datos = {
            "telefono": telefono_formateado,
            "nombre": data.get("nombre", ""),
            "valor1": valor_formateado,
            "fecha": fecha,
            "referencia": f"M{random.randint(10000000, 99999999)}",
            "disponible": "Disponible",
        }

        if es_comprobante_qr:
            datos = {
                "nombre": data.get("nombre", ""),
                "valor1": valor_formateado,
                "fecha": fecha,
                "referencia": f"M{random.randint(10000000, 99999999)}",
                "disponible": "Disponible",
            }

        for campo, texto in datos.items():
            if campo in styles:
                style = styles[campo]
                try:
                    font = ImageFont.truetype(font_path, style["size"])
                except:
                    font = ImageFont.load_default()
                if campo == "valor1":
                    pos_x, pos_y = style["pos"]
                    draw_text_with_outline(draw, (pos_x, pos_y), str(texto), font, style["color"])
                else:
                    draw_text_with_outline(draw, style["pos"], str(texto), font, style["color"])

    # Guardar y devolver
    output_path = f"gen_{uuid.uuid4().hex}.png"
    image.save(output_path)
    return output_path