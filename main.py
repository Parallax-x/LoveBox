from db import drop_table, create_table, engine

if __name__ == "__main__":
    drop_table(engine)
    create_table(engine)
    # vk = vk_api.VkApi(token=os.getenv('token_group'))
    # longpoll = VkLongPoll(vk)
    # bot.start()
