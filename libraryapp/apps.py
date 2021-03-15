from django.apps import AppConfig


class LibraryappConfig(AppConfig):
    name = 'libraryapp'

    def ready(self):
        import libraryapp.signal
