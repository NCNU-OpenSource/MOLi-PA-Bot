import threading
import time
import telepot
from telepot.loop import MessageLoop
import pyttsx3

import pafy, vlc
from youtube_search import YoutubeSearch

# broadCast message
def broadCast(msg) :
    global player
    global playStatus
    print('Broadcasting', msg)
    engine = pyttsx3.init()
    engine.setProperty('rate', 130)
    # if broadCast while playing music
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

# show the playlist
def show() :
    global isPlaying, nowPlayingSong, playList
    show_str = ''
    if isPlaying :
        show_str += 'Now Playing\n==========\n' + nowPlayingSong['title'] + '(Ordered By ' + nowPlayingSong['orderUser'] + ')\n\n'
    show_str += 'Next\n==========\n'
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
    Instance = vlc.Instance()
    player = Instance.media_player_new()
    Media = Instance.media_new(playurl)
    Media.get_mrl()
    player.set_media(Media)
    volume = 60
    player.audio_set_volume(volume)
    player.play()
    time.sleep(1.5)
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
    if msg['chat']['username'] == '' :
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
                        bot.sendMessage(chat_id, "Playing now", reply_to_message_id = msg['message_id'])

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

            elif msg['text'] == '/cancel' :
                del user_status[user_id]
                bot.sendMessage(chat_id, 'Ok, command canceled.')

            else :
                # 檢查使用者是否有指令狀態，若沒有就不理他
                if user_status.__contains__(user_id) :
                    if user_status[user_id] == 'broadcast' :
                        bot.sendMessage(chat_id, 'Broadcasting...')
                        # 呼叫函數廣播文字
                        broadCast(msg['text'])
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