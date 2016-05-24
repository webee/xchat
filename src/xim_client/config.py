

class XIMClientConfig:
    HOST_URL = 'http://localhost:6980'

    APP_NEW_TOKEN_URL = '/xim/app.new_token'
    APP_NEW_USER_TOKEN_URL = '/xim/app.new_user_token'

    APP_CREATE_CHANNEL_URL = '/xim/app/channels/'
    APP_CHANNEL_URL = '/xim/app/channels/{channel}/'
    APP_CHANNEL_PUBLISHERS_URL = '/xim/app/channels/{channel}.publishers'
    APP_CHANNEL_SUBSCRIBERS_URL = '/xim/app/channels/{channel}.subscribers'
    APP_CHANNEL_MSG_LAST_ID = '/xim/app/msg/{channel}/last_id'
