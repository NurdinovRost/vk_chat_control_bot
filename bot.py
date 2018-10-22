import vk_api
import time
import datetime
from vk_api.longpoll import VkLongPoll, VkEventType
import config
from operator import itemgetter


def parse_group(group):
    index = 0
    posts = []
    flag = True
    t = datetime.datetime.now()
    c = datetime.datetime(t.year, t.month, t.day, hour=0, minute=0, second=0, microsecond=0)
    t = datetime.datetime.timestamp(c)
    while flag:
        print(group)
        try:
            temp = vk.wall.search(owner_id=group, query="@id513166325 Phoebe Halliwell", owners_only=0, count=100,
                                  offset=index * 100, extended=0)
        except Exception as err:
            print(err)
            return []
        index += 1
        if temp['items']:
            if temp['count'] < 100 and (t > int(temp['items'][-1]['date'])):
                flag = False
            for elem in temp['items']:
                if t < int(elem['date']):
                    posts.append(elem['from_id'])
        else:
            flag = False
    return posts


def check_post(cmd, chat_num):
    file = open('time.txt', 'r')
    time_last_start = float(file.read())
    time_now = time.time()
    file.close()
    if time_now - time_last_start < 18000:
        t = time.strftime('%H:%M:%S', time.gmtime(18000 - (time_now - time_last_start)))
        vk.messages.send(chat_id=chat_num, message="До использовании функции осталось: {t}".format(t=t))
        return 0
    else:
        users_in_chat = []
        dict_name_users = {}
        temp = vk.messages.getChat(chat_id=chat_num, fields='first_name')['users']
        print(temp)
        for i in temp:
            users_in_chat.append(i['id'])
            dict_name_users[i['id']] = i['first_name'] + " " + i['last_name']
        dict_users = {}
        for user in users_in_chat:
            dict_users[user] = 0
        groups = config.groups
        for group in groups:
            posts = parse_group(group)
            for i in posts:
                if i in dict_users:
                    dict_users[i] += 1
        users_in_chat = sorted(dict_users.items(), key=itemgetter(1))
        users_in_chat.reverse()
        text = "Было создано постов\n"
        text += "_____________________\n"

        for user in users_in_chat:
            text += '@id' + str(user[0]) + " " + dict_name_users[user[0]] + ': ' + str(user[1]) + '\n'
        text += "_____________________"
        vk.messages.send(chat_id=chat_num, message=text)
        file = open('time.txt', 'w')
        file.write(str(time.time()))
        file.close()


def get_followers(user_id):
    index = 0
    list_followers = []
    flag = True
    while flag:
        temp = vk.users.getFollowers(user_id=user_id, offset=index * 1000, count=1000)['items']
        index += 1
        if len(temp) < 1000:
            flag = False
        for elem in temp:
            list_followers.append(elem)
    return list_followers


def check_friends(users, chat_num):
    users_in_chat = vk.messages.getChat(chat_id=chat_num)['users']
    list_users = users.split(' ')
    print(list_users)
    for i in range(len(list_users)):
        if '@id' in list_users[i]:
            list_users[i] = list_users[i].split('|')[0][3:]
            print(list_users[i])
    if len(list_users) < 2:
        print("function !add callable with arguments (users id)!!")
    else:
        print(list_users)
        for i in range(1, len(list_users)):
            info = {'friends': 0, 'followers': 0, 'not_friends': []}
            temp = vk.friends.get(user_id=list_users[i], count=8000)
            friends = temp['items']
            for user in users_in_chat:
                if user in friends:
                    info['friends'] += 1
                else:
                    print(list_users[i])
                    print(get_followers(user))
                    if int(list_users[i]) in get_followers(user):
                        info['followers'] += 1
                    else:
                        info['not_friends'].append(user)
            text = ""
            for i in range(len(info['not_friends'])):
                text += str(i) + '. ' + '@id' + str(info['not_friends'][i]) + '\n'
            vk.messages.send(chat_id=chat_num, message="Есть в друзьях: {friends}\n"
                                                      "Есть в подписчиках: {followers}\n"
                                                      "Не добавлено: {not_friends}\n"
                                                      "\n"
                                                      "{text}".format(friends=str(info['friends']),
                                                                      followers=str(info['followers']),
                                                                      not_friends=str(len(info['not_friends'])),
                                                                      text=text))


def add(users, chat_num):
    user_in_chat = vk.messages.getChat(chat_id=chat_num)['users']
    list_users = users.split(' ')
    for i in range(len(list_users)):
        if '@id' in list_users[i]:
            list_users[i] = list_users[i].split('|')[0][3:]
            # print(list_users[i])
    if len(list_users) < 2:
        print("function !add callable with arguments (users id)!!")
    else:
        for i in range(1, len(list_users)):
            try:
                if int(list_users[i]) not in user_in_chat:
                    try:
                        vk.messages.addChatUser(chat_id=chat_num, user_id=list_users[i])
                    except Exception as err:
                        print(err)
            except ValueError as err:
                print(err)


def delete(users, chat_num):
    user_in_chat = vk.messages.getChat(chat_id=chat_num)['users']
    list_users = users.split(' ')
    for i in range(len(list_users)):
        if '@id' in list_users[i]:
            list_users[i] = list_users[i].split('|')[0][3:]
            # print(list_users[i])
    if len(list_users) < 2:
        print("function !add callable with arguments (users id)!!")
    else:
        for i in range(1, len(list_users)):
            try:
                if int(list_users[i]) in user_in_chat:
                    try:
                        vk.messages.removeChatUser(chat_id=chat_num, user_id=list_users[i])
                    except Exception as e:
                        print(e)
                else:
                    try:
                        vk.messages.removeChatUser(chat_id=chat_num, member_id=list_users[i])
                    except Exception as e:
                        print('error')
            except ValueError as err:
                print(err)


day = 86400
commands = {'!add': add, '!delete': delete, '!check': check_friends, '!post': check_post}
chat_id = config.chat_id
vk_session = vk_api.VkApi(config.login, config.password)
vk_session.auth()

vk = vk_session.get_api()


def main():
    try:
        vk_session.auth(token_only=True)
    except vk_api.AuthError as error_msg:
        print(error_msg)
        return

    longpoll = VkLongPoll(vk_session)

    for event in longpoll.listen():

        if event.type == VkEventType.MESSAGE_NEW:
            if event.from_chat:
                if event.chat_id in chat_id and event.user_id in config.admins:
                    message = event.text.split(' ')
                    if message[0] in commands:
                        commands[message[0]](event.text, event.chat_id)


if __name__ == "__main__":
    main()
