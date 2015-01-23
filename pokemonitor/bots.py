bot_status = {
}

def update_status(data):
    if data is not None:
        username = data['username']
        status = data['status']
        if status == 'match':
            bot_status[username] = data
        elif status == 'done':
            if username in bot_status:
                del bot_status[username]

def get_bots():
    return bot_status
