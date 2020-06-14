import threading, time, random
from os import path
import telepot
from telepot.loop import MessageLoop
import pyttsx3

import pafy, vlc
from youtube_search import YoutubeSearch

# broadcast message
def broadcast(msg) :
    global player
    global playStatus
    print('Broadcasting', msg)
    engine = pyttsx3.init()
    engine.setProperty('rate', 130)
    engine.setProperty('voice', 'zh')
    # if broadcast while playing music
    # music will pause
    if isPlaying :
        playStatus = 'pause'
        player.pause()
        engine.say(msg)
        engine.runAndWait()
        player.pause()
        time.sleep(1)
        playStatus = 'play'
    else :
        engine.say(msg)
        engine.runAndWait()
    return

# show_plist - show your own personal playlist
def show_plist(user_id) :
    file = open(user_id + '_playlist.txt', 'r', encoding='utf8')
    personal_plist = file.readlines()
    personal_plist = list(map(eval, personal_plist))
    file.close()
    if len(personal_plist) == 0 :
        return 'You don\'t have any song in your playlist,\nplease add song first'
    else :
        reply_str = ''
        for i in range(len(personal_plist)) :
            reply_str += str(i + 1) + '. ' + personal_plist[i]['title'] + '\nhttps://www.youtube.com' + personal_plist[i]['link'] + '\n'
        return reply_str

# 檢查要新增的歌曲是否已經在 playlist 中
def checkPlistHasExisted(user_id, toAddSong) :
    file = open(user_id + '_playlist.txt', 'r', encoding='utf8')
    data = file.readlines()
    file.close()
    for i in data :
        if toAddSong['link'] in i :
            result = 'This song is already in your playlist'
            return False, result
    return True, 'OK'

# 檢查個人播放清單的歌曲數量是否超過上限
def checkPlistLen(user_id) :
    file = open(user_id + '_playlist.txt', 'r', encoding='utf8')
    data = file.readlines()
    file.close()
    if len(data) < 10 :
        return True, 'OK'
    else :
        return False, 'Your playlist is full!'

# add song to personal playlist from now playing
def addToMyPlist(user_id, nowPlayingSong) :
    file = open(user_id + '_playlist.txt', 'a+', encoding='utf8')
    nowPlayingSong['orderUser'] = '@' + user_id
    input_str = str(nowPlayingSong) + '\n'
    file.write(input_str)
    file.close()
    return True

def addSongsToMyPlist(user_id, addSongNum) :
    global playList
    # 因為允許一次選多首歌，因此 playSongNum 是個字串，用空白隔開數字
    addSongNum = addSongNum.split(' ')
    count = 0
    for i in addSongNum :
        # 排除不合法的數字
        if int(i) <= 0 or int(i) > len(playList) :
            continue
        # 檢查清單長度
        status, reply = checkPlistLen(user_id)
        if status :
            # 再檢查重複
            status, reply = checkPlistHasExisted(user_id, playList[int(i) - 1])
            if status :
                file = open(user_id + '_playlist.txt', 'a+', encoding='utf8')
                playList[int(i) - 1]['orderUser'] = '@' + user_id
                write_str = str(playList[int(i) - 1]) + '\n'
                file.write(write_str)
                file.close()
            else :
                count += 1
                reply = 'Some songs has already in your playlist'
        else :
            return status, reply
    if count > 0 :
        return True, reply
    else :
        return True, 'OK'

# edit_plist - delete songs from your own personal playlist
def edit_plist(user_id, toDelete) :
    file = open(user_id + '_playlist.txt', 'r', encoding='utf8')
    plist = file.readlines()
    file.close()
    toDelete = toDelete.split(' ')
    toDelete.sort(reverse=True)
    initLength = len(plist)
    for i in toDelete :
        # 排除不合法的數字
        if int(i) <= 0 or int(i) > initLength :
            continue
        plist.pop(int(i) - 1)
    file = open(user_id + '_playlist.txt', 'w', encoding='utf8')
    for i in range(len(plist)) :
        print(plist[i])
        file.write(str(plist[i]))
    file.close()

# add_from_plist - add songs to public playlist from your playlist
def add_from_plist(user_id, playSongNum) :
    global playList
    # 因為允許一次選多首歌，因此 playSongNum 是個字串，用空白隔開數字
    playSongNum = playSongNum.split(' ')
    file = open(user_id + '_playlist.txt', 'r', encoding='utf8')
    data = file.readlines()
    file.close()
    # 把 playSongNum 裡的數字對應到 playlist 上，加入播放清單
    print(playSongNum)
    for i in playSongNum :
        # 排除不合法的數字
        if int(i) < 0 or int(i) > len(data) :
            continue
        # 把個人 playlist 的歌加進 public playlist
        playList.append(eval(data[int(i) - 1]))

# play_all_plist - play all songs from your playlist randomly
def play_all_plist(user_id) :
    global playList
    file = open(user_id + '_playlist.txt', 'r', encoding='utf8')
    personal_plist = file.readlines()
    file.close()
    random.shuffle(personal_plist)
    for i in range(len(personal_plist)) :
        playList.append(eval(personal_plist[i]))

# show the playlist
def show() :
    global isPlaying, nowPlayingSong, playList
    show_str = ''
    if isPlaying :
        show_str += 'Now Playing\n==========\n' + nowPlayingSong['title'] + '(Ordered By ' + nowPlayingSong['orderUser'] + ') /addToMyPlist\n\n'
    show_str += 'Next /addSongsToMyPlist\n==========\n '
    if len(playList) > 0 :
        for i in range(len(playList)) :
            show_str += str(i + 1) + '. ' + playList[i]['title'] + ' (Ordered By ' + playList[i]['orderUser'] + ')\n'
        show_str += '\n'
    else :
        show_str += 'No Playlist!'
    return show_str

# delete a song from playlist
def delete(num) :
    global playList
    playList.pop(int(num) - 1)

# search song on youtube
def search(msg) :
    return YoutubeSearch(msg, max_results=10).to_dict()

# stop playing song
def stop() :
    global stopCmd, playStatus
    playStatus = 'stop'
    stopCmd = True

# skip now playing
def skip() :
    global player, isPlaying
    if isPlaying :
        player.stop()

def vol_up() :
    global player, volume
    volUp = volume + 5
    if volUp <= 100 :
        player.audio_set_volume(volUp)
        volume += 5
        return True
    else :
        return False

def vol_down() :
    global player, volume
    volDown = volume - 5
    if volDown >= 5 :
        player.audio_set_volume(volDown)
        volume -= 5
        return True
    else :
        return False

# play song
def play(msg) :
    global player
    global playStatus
    global volume
    url = "https://www.youtube.com" + msg
    video = pafy.new(url)
    best = video.getbest()
    playurl = best.url
    vlc.Instance("prefer-insecure")
    player = vlc.MediaPlayer(playurl)
    volume = 60
    player.audio_set_volume(volume)
    a = player.play()
    time.sleep(5)
    playStatus = 'play'
    # duration = player.get_length() / 1000
    # time.sleep(duration)
    while playStatus != 'stop' and (player.is_playing() == 1 or playStatus == 'pause')  :
        pass
    player.stop()
    playStatus = 'stop'
    return

def to_play() :
    global isPlaying, playing_thread, nowPlayingSong
    # playlist = open('playlist.txt', 'r+', encoding='utf8')
    global playList, stopCmd
    while len(playList) > 0 and not stopCmd:
        nowPlayingSong = playList.pop(0)
        print('Now Playing =', nowPlayingSong['title'])
        play(nowPlayingSong['link'])

    stopCmd = False
    isPlaying = False
    playing_thread = None
    return

def handle(msg) :
    global playList, nowPlayingSong, isPlaying
    global playing_thread, user_status
    content_type, chat_type, chat_id = telepot.glance(msg)
    print(content_type, chat_type, chat_id)
    print(msg)

    # 先檢查是否有 Username
    if 'username' not in msg['chat'] :
        bot.sendMessage(chat_id, 'Please set a UserName')
    else :
        user_id = msg['chat']['username']
        # 檢查使用者是否傳送文字訊息
        if content_type == 'text' :
            # 確定是什麼指令
            if msg['text'] == '/start' :
                # 介紹機器人
                bot.sendMessage(chat_id, 'Order music and play music in MOLi')

            elif msg['text'] == '/broadcast' :
                # input text, broadcast in MOLi
                bot.sendMessage(chat_id, 'Now send me text you want to broadcast')
                user_status[user_id] = 'broadcast'

            elif msg['text'] == '/play' :
                # choose a playlist to play music
                if len(playList) == 0 :
                    bot.sendMessage(chat_id, "No playlist to play!", reply_to_message_id = msg['message_id'])
                else :
                    if playing_thread != None :
                        if playing_thread.is_alive() :
                            bot.sendMessage(chat_id, "It's playing now!", reply_to_message_id = msg['message_id'])
                    else :
                        playing_thread = threading.Thread(target=to_play, args=())
                        playing_thread.start()
                        isPlaying = True
                        reply_str = show()
                        bot.sendMessage(chat_id, reply_str, reply_to_message_id = msg['message_id'])

            elif msg['text'] == '/stop' :
                if playing_thread != None :
                    if playing_thread.is_alive() :
                        stop()
                        bot.sendMessage(chat_id, 'Now stop')

            elif msg['text'] == '/skip' :
                # skip now playing song
                skip()

            elif msg['text'] == '/vol_up' :
                # skip now playing song
                if not vol_up() :
                    bot.sendMessage(chat_id, 'Too loud!', reply_to_message_id = msg['message_id'])
                else :
                    bot.sendMessage(chat_id, 'Volumn:' + str(volume))

            elif msg['text'] == '/vol_down' :
                # skip now playing song
                if not vol_down() :
                    bot.sendMessage(chat_id, 'Too low!', reply_to_message_id = msg['message_id'])
                else :
                    bot.sendMessage(chat_id, 'Volumn:' + str(volume))

            elif msg['text'] == '/show' :
                # show all playlist
                reply_str = show()
                bot.sendMessage(chat_id, reply_str, reply_to_message_id = msg['message_id'])

            elif msg['text'] == '/add' :
                # search song on youtube and add to list
                bot.sendMessage(chat_id, 'Now please send some words of the song, which you want to add')
                user_status[user_id] = 'add'

            elif msg['text'] == '/delete' :
                # delete a song from playlist
                list_str = ''
                if len(playList) > 0 :
                    bot_reply = 'Please choose a number of songs in playlist, which you want to delete.'
                    bot.sendMessage(chat_id, bot_reply, reply_to_message_id = msg['message_id'])
                    time.sleep(1)
                    for i in range(len(playList)) :
                        list_str += str(i + 1) + '. ' + playList[i]['title'] + '\n'
                    bot.sendMessage(chat_id, list_str)
                    user_status[user_id] = 'delete'
                else :
                    bot.sendMessage(chat_id, 'No playlist!', reply_to_message_id = msg['message_id'])

            elif msg['text'] == '/create_plist' :
                file = open(user_id + '_playlist.txt', 'a+', encoding='utf8')
                file.close()
                reply_str = 'Done, now you have your personal playlist'
                bot.sendMessage(chat_id, reply_str, reply_to_message_id = msg['message_id'], disable_web_page_preview=True)

            elif msg['text'] == '/show_plist' :
                if path.isfile('./' + user_id + '_playlist.txt') :
                    reply_str = show_plist(user_id)
                    bot.sendMessage(chat_id, reply_str, reply_to_message_id = msg['message_id'], disable_web_page_preview=True)
                else :
                    reply_str = 'You don\'t have playlist, please create one first.'
                    bot.sendMessage(chat_id, reply_str, reply_to_message_id = msg['message_id'])

            elif msg['text'] == '/addToMyPlist' :
                if path.isfile('./' + user_id + '_playlist.txt') :
                    # 先檢查清單的長度
                    plist_status, reply = checkPlistLen(user_id)
                    if plist_status :
                        # 再檢查是否有重複
                        plist_status, reply = checkPlistHasExisted(user_id, nowPlayingSong)
                        if plist_status :
                            if addToMyPlist(user_id, nowPlayingSong) :
                                bot.sendMessage(chat_id, 'Ok', reply_to_message_id = msg['message_id'])
                        else :
                            bot.sendMessage(chat_id, reply, reply_to_message_id = msg['message_id'])
                    else :
                        bot.sendMessage(chat_id, reply, reply_to_message_id = msg['message_id'])
                else :
                    reply_str = 'You don\'t have playlist, please create one first.'
                    bot.sendMessage(chat_id, reply_str, reply_to_message_id = msg['message_id'])

            elif msg['text'] == '/addSongsToMyPlist' :
                if path.isfile('./' + user_id + '_playlist.txt') :
                    bot.sendMessage(chat_id, 'Please choose numbers of songs in playlist,\nwhich you want to add to your personal playlist.', reply_to_message_id = msg['message_id'])
                    reply_str = show()
                    time.sleep(1)
                    bot.sendMessage(chat_id, reply_str, reply_to_message_id = msg['message_id'])
                    user_status[user_id] = 'addSongs'
                else :
                    reply_str = 'You don\'t have playlist, please create one first.'
                    bot.sendMessage(chat_id, reply_str, reply_to_message_id = msg['message_id'])
            
            elif msg['text'] == '/add_from_plist' :
                if path.isfile('./' + user_id + '_playlist.txt') :
                    bot.sendMessage(chat_id, 'Please choose numbers of songs in playlist,\nwhich you want to play.', reply_to_message_id = msg['message_id'], disable_web_page_preview=True)
                    reply_str = show_plist(user_id)
                    time.sleep(1)
                    bot.sendMessage(chat_id, reply_str, reply_to_message_id = msg['message_id'], disable_web_page_preview=True)
                    user_status[user_id] = 'add_from_plist'
                else :
                    reply_str = 'You don\'t have playlist, please create one first.'
                    bot.sendMessage(chat_id, reply_str, reply_to_message_id = msg['message_id'])

            elif msg['text'] == '/play_all_plist' :
                if path.isfile('./' + user_id + '_playlist.txt') :
                    play_all_plist(user_id)
                    if playing_thread == None :
                        playing_thread = threading.Thread(target=to_play, args=())
                        playing_thread.start()
                        isPlaying = True
                        reply_str = show()
                        bot.sendMessage(chat_id, reply_str, reply_to_message_id = msg['message_id'])
                    else :
                        bot.sendMessage(chat_id, 'Add to public playlist successfully!', reply_to_message_id = msg['message_id'])
                else :
                    reply_str = 'You don\'t have playlist, please create one first.'
                    bot.sendMessage(chat_id, reply_str, reply_to_message_id = msg['message_id'])

            elif msg['text'] == '/edit_plist' :
                if path.isfile('./' + user_id + '_playlist.txt') :
                    user_status[user_id] = 'edit_plist'
                    bot_reply = 'Please choose a number of songs in your playlist, which you want to delete.'
                    bot.sendMessage(chat_id, bot_reply, reply_to_message_id = msg['message_id'])
                    time.sleep(1)
                    reply_str = show_plist(user_id)
                    bot.sendMessage(chat_id, reply_str, reply_to_message_id = msg['message_id'], disable_web_page_preview=True)
                else :
                    reply_str = 'You don\'t have playlist, please create one first.'
                    bot.sendMessage(chat_id, reply_str, reply_to_message_id = msg['message_id'])

            else :
                # 檢查使用者是否有指令狀態，若沒有就不理他
                if user_status.__contains__(user_id) :
                    if user_status[user_id] == 'broadcast' :
                        bot.sendMessage(chat_id, 'Broadcasting...')
                        # 呼叫函數廣播文字
                        broadcast(msg['text'])
                        # 完成事情後洗掉指令狀態
                        bot.sendMessage(chat_id, 'Broadcast over')
                        del user_status[user_id]

                    elif user_status[user_id] == 'delete' :
                        delete(msg['text'])
                        show_str = show()
                        bot.sendMessage(chat_id, 'Done. Following is new playlist')
                        time.sleep(1)
                        bot.sendMessage(chat_id, show_str)
                        # 完成事情後洗掉指令狀態
                        del user_status[user_id]

                    elif user_status[user_id] == 'add' :
                        search_result = search(msg['text'])
                        print_result = ''
                        for i in range(len(search_result)) :
                            print_result += str(i + 1) + '. ' + search_result[i]['title'] + '\nhttps://www.youtube.com' + search_result[i]['link'] + '\n'
                        bot.sendMessage(chat_id, 'Following is search result, please choose a number of songs,\nwhich will be add to playlist', reply_to_message_id = msg['message_id'])
                        time.sleep(1)
                        bot.sendMessage(chat_id, print_result, disable_web_page_preview=True)
                        user_status[user_id] = ['await_add', search_result]

                    elif user_status[user_id][0] == 'await_add' :
                        search_result = user_status[user_id][1]
                        addSong = search_result[int(msg['text']) - 1]
                        addSong['orderUser'] = '@' + user_id
                        playList += [addSong]
                        show_str = show()
                        bot.sendMessage(chat_id, 'Done. Following is new playlist')
                        time.sleep(1)
                        bot.sendMessage(chat_id, show_str)
                        del user_status[user_id]

                    elif user_status[user_id] == 'add_from_plist' :
                        add_from_plist(user_id, msg['text'])
                        show_str = show()
                        bot.sendMessage(chat_id, 'Done. Following is new playlist')
                        time.sleep(1)
                        bot.sendMessage(chat_id, show_str)
                        del user_status[user_id]

                    elif user_status[user_id] == 'addSongs' :
                        status, reply = addSongsToMyPlist(user_id, msg['text'])
                        reply_str = show_plist(user_id)
                        if status and reply == 'OK':
                            bot.sendMessage(chat_id, 'Done. Following is your new playlist')
                            time.sleep(1)
                            bot.sendMessage(chat_id, reply_str, disable_web_page_preview=True)
                        else :
                            bot.sendMessage(chat_id, reply)
                        del user_status[user_id]

                    elif user_status[user_id] == 'edit_plist' :
                        edit_plist(user_id, msg['text'])
                        reply_str = show_plist(user_id)
                        bot.sendMessage(chat_id, 'Done. Following is your new playlist')
                        time.sleep(1)
                        bot.sendMessage(chat_id, reply_str, disable_web_page_preview=True)
                        del user_status[user_id]

# global variables
user_status = dict()
search_result = []
playStatus = 'stop'
isPlaying = False
playList = []
playing_thread = None
stopCmd = False
player = None
volume = 0

if __name__ == '__main__' :
    myFile = open('TOKEN.txt')
    TOKEN = myFile.read().strip()
    # TOKEN = lines[0]
    bot = telepot.Bot(TOKEN)
    MessageLoop(bot, handle).run_as_thread()
    print ('Listening ...')

    # Keep the program running.
    while 1:
        time.sleep(10)
