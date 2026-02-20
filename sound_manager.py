import pygame


class SoundManager:

    def __init__(self):
        pygame.mixer.pre_init(44100, -16, 2, 512)
        pygame.mixer.init()

        self.ding_sound = self._load_sound('ressources/ding.mp3')
        self.crash_sound = self._load_sound('ressources/crash.mp3')
        self._start_background_music('ressources/bg_music_1.mp3')

    # Méthodes internes

    def _load_sound(self, path: str):
        try:
            sound = pygame.mixer.Sound(path)
            return sound
        except Exception as e:
            print(f"[SoundManager] Impossible de charger '{path}' : {e}")
            return None

    def _start_background_music(self, path: str):
        try:
            pygame.mixer.music.load(path)
            pygame.mixer.music.set_volume(0.4)
            pygame.mixer.music.play(loops=-1)
        except Exception as e:
            print(f"[SoundManager] Impossible de charger la musique de fond '{path}' : {e}")


    def play_ding(self):
        if self.ding_sound:
            self.ding_sound.play()

    def play_crash(self):
        """À appeler quand le serpent se cogne (mur ou propre corps)."""
        if self.crash_sound:
            self.crash_sound.play()

    def pause_music(self):
        """Met la musique de fond en pause ."""
        pygame.mixer.music.pause()

    def resume_music(self):
        """Reprend la musique de fond."""
        pygame.mixer.music.unpause()

    def stop_music(self):
        """Arrête définitivement la musique de fond."""
        pygame.mixer.music.stop()