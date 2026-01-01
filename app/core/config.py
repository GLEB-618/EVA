from pydantic_settings import BaseSettings, SettingsConfigDict
from spotipy import Spotify
from spotipy.oauth2 import SpotifyClientCredentials, SpotifyOAuth


class Settings(BaseSettings):

    DB_HOST: str
    DB_PORT: str
    DB_USER: str
    DB_PASS: str
    DB_NAME: str

    BOT_TOKEN: str
    TELEGRAM_API_BASE_URL: str
    GROUP_ID: int

    EMBEDDING_MODEL: str
    LLM_MODEL: str
    URL_CHAT: str

    CLIENT_ID_SP: str
    CLIENT_SECRET_SP: str
    REDIRECT_URI_SP: str

    LOG_LEVEL: str
    
    @property
    def DATABASE_URL(self):
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    @property
    def spotify_oauth(self) -> SpotifyOAuth:
        return SpotifyOAuth(
            client_id=self.CLIENT_ID_SP,
            client_secret=self.CLIENT_SECRET_SP,
            redirect_uri=self.REDIRECT_URI_SP,
            scope="user-top-read user-library-read",
            # show_dialog=True,
        )
    
    @property
    def authorization(self):
        return Spotify(
            auth_manager=self.spotify_oauth
        )

    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()