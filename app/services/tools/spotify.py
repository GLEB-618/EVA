from app.core.config import settings
from spotipy.exceptions import SpotifyException


sp = settings.authorization


def get_auth_url() -> str:
    return settings.spotify_oauth.get_authorize_url()

async def get_top_tracks(limit: int = 10, offset: int = 0, time_range: str = "medium_term") -> str:
    """
    Возвращает топ-треки пользователя.
    time_range может быть: "short_term", "medium_term" или "long_term".
    """
    try:
        results = sp.current_user_top_tracks(limit=limit, offset=offset, time_range=time_range)

        tracks = ''
        i = offset + 1
        for item in results.get("items", []):
            track_name = item.get("name")
            artists = ", ".join(artist["name"] for artist in item.get("artists", []))
            track_url = item.get("external_urls", {}).get("spotify")
            track = f"{track_name} - {artists}"
            tracks += f"{i}\. {link(track, track_url)}\n" # type: ignore
            i += 1
        return tracks
    except SpotifyException as e:
        # 401 = нет/просрочен токен => даём ссылку на авторизацию
        if getattr(e, "http_status", None) == 401:
            url = get_auth_url()
            return f"Нужна авторизация Spotify (токен истёк/нет доступа). Войди заново: {url}"
        raise