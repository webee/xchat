from django.conf import settings


def run():
    import xim_client
    xim_client.init(settings.XIM_APP, settings.XIM_PASSWORD, settings.CONFIG.etc.XIMClientConfig)

