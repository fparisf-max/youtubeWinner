import requests
import random
import argparse
import sys

# CONFIGURACIÓN
API_KEY = 'API-KEY de GCP'  # Reemplaza con tu clave de API de YouTube Data API v3

def obtener_nombres_unicos(api_key: str, video_id: str, unique_by: str = 'channel'):
    """
    Devuelve la lista de nombres visibles de comentaristas únicos de un video.
    unique_by: 'channel' (recomendado) o 'name'
    """
    base_url = 'https://www.googleapis.com/youtube/v3/commentThreads'
    params = {
        'part': 'snippet',
        'videoId': video_id,
        'key': api_key,
        'maxResults': 100000,
        'textFormat': 'plainText'
    }

    unique_names = []
    seen_keys = set()
    next_page_token = None

    while True:
        if next_page_token:
            params['pageToken'] = next_page_token

        resp = requests.get(base_url, params=params, timeout=30)
        data = resp.json()

        if 'error' in data:
            raise RuntimeError(data['error']['message'])

        for item in data.get('items', []):
            snip = item['snippet']['topLevelComment']['snippet']
            name = (snip.get('authorDisplayName') or '').strip()
            channel_id = (snip.get('authorChannelId', {}) or {}).get('value', '')

            key = (channel_id or name.lower()) if unique_by == 'channel' else name.lower()

            if name and key and key not in seen_keys:
                seen_keys.add(key)
                unique_names.append(name)

        next_page_token = data.get('nextPageToken')
        if not next_page_token:
            break

    return unique_names

def main():
    # ÚNICO parámetro posicional: video_id
    parser = argparse.ArgumentParser(
        description="Selecciona al azar un comentarista único de un video de YouTube."
    )
    parser.add_argument("video_id", help="ID del video de YouTube (ej. dQw4w9WgXcQ)")
    args = parser.parse_args()

    try:
        nombres = obtener_nombres_unicos(API_KEY, args.video_id, unique_by='channel')

        if not nombres:
            print("No se encontraron comentarios en este video.")
            sys.exit(0)

        print("Nombres visibles (sin repetidos):")
        for i, n in enumerate(nombres, 1):
            print(f"{i}. {n}")

        ganador = random.choice(nombres)
        print("\n🎉 Usuario seleccionado al azar:", ganador)

    except Exception as e:
        print("Error:", e)
        sys.exit(1)

if __name__ == "__main__":
    main()
