from bot_vk.bot_vk import Bot

if __name__ == '__main__':

    bot1 = Bot()
    print('Работа бота в процессе')
    try:
        bot1.longpoll_event()
    except KeyboardInterrupt:
        print('Работа приостановлена.')
