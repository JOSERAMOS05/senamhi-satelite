import requests
from pathlib import Path
from datetime import datetime, timedelta, timezone
import csv

# =====================================================
# CONFIGURACIÓN
# =====================================================

BASE_DIR = Path(__file__).resolve().parents[1]

DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

RUTA_LATEST = DATA_DIR / "latest.jpg"
RUTA_METADATA = DATA_DIR / "metadata.csv"

URL_BASE = "https://www.senamhi.gob.pe/usr/sat/G16D/Per/PerC13CP{fecha_hora}.jpg"


def descargar_imagen(fecha_hora):
    """
    Descarga una imagen específica de SENAMHI.
    fecha_hora debe tener formato YYYYMMDDHHMM.
    """

    url = URL_BASE.format(fecha_hora=fecha_hora)

    print(f"Probando URL: {url}")

    try:
        r = requests.get(url, timeout=30)
        content_type = r.headers.get("Content-Type", "")

        if r.status_code == 200 and "image" in content_type:
            with open(RUTA_LATEST, "wb") as f:
                f.write(r.content)

            dt_utc = datetime.strptime(fecha_hora, "%Y%m%d%H%M").replace(tzinfo=timezone.utc)
            dt_peru = dt_utc - timedelta(hours=5)

            with open(RUTA_METADATA, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow([
                    "fecha_hora_imagen_utc",
                    "fecha_hora_imagen_peru",
                    "url_original",
                    "archivo_publicado",
                    "actualizado_utc"
                ])

                writer.writerow([
                    dt_utc.strftime("%Y-%m-%d %H:%M UTC"),
                    dt_peru.strftime("%Y-%m-%d %H:%M hora Perú"),
                    url,
                    "data/latest.jpg",
                    datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
                ])

            print(f"Imagen actualizada: {RUTA_LATEST}")
            print(f"Metadata actualizada: {RUTA_METADATA}")
            return True

        print(f"No disponible. Estado: {r.status_code} | Content-Type: {content_type}")
        return False

    except Exception as e:
        print(f"Error descargando imagen: {e}")
        return False


def buscar_ultima_imagen():
    """
    Busca la última imagen disponible.
    SENAMHI usa horario UTC en el nombre del archivo.
    Ejemplo: 202606231850 = 2026-06-23 18:50 UTC.
    """

    ahora_utc = datetime.now(timezone.utc)

    horas_a_probar = [
        ahora_utc,
        ahora_utc - timedelta(hours=1),
        ahora_utc - timedelta(hours=2),
        ahora_utc - timedelta(hours=3)
    ]

    minutos_a_probar = [50, 40, 30, 20, 10, 0]

    for hora_base in horas_a_probar:
        for minuto in minutos_a_probar:
            intento = hora_base.replace(minute=minuto, second=0, microsecond=0)
            fecha_hora = intento.strftime("%Y%m%d%H%M")

            if descargar_imagen(fecha_hora):
                print(f"Última imagen encontrada: {fecha_hora}")
                return fecha_hora

    print("No se encontró ninguna imagen reciente.")
    return None


if __name__ == "__main__":
    resultado = buscar_ultima_imagen()

    if resultado is None:
        raise SystemExit("No se pudo actualizar latest.jpg")
