import threading
import time
import telepot
from telepot.loop import MessageLoop
import pyttsx3

import pafy, vlc
from youtube_search import YoutubeSearch

def broadCast(msg) :
    global player
    global playStatus
    print('Broadcasting', msg)
    engine = pyttsx3.init()
    engine.setProperty('rate', 130)
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
        show_str += 'Now Playing\n==========\n' + nowPlayingSong['title'] + '(Order By ' + nowPlayingSong['orderUser'] + ')\n\n'
    show_str += 'Next\n==========\n'
    if len(playList) > 0 :
        for i in range(len(playList)) :
            show_str += str(i + 1) + '. ' + playList[i]['title'] + ' (Order By ' + playList[i]['orderUser'] + ')\n'
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
    global search_result
    search_result = YoutubeSearch(msg, max_results=10).to_dict()

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

# play song
def play(msg) :
    global player
    global playStatus
    url = "https://www.youtube.com" + msg
    video = pafy.new(url)
    best = video.getbest()
    playurl = best.url
    Instance = vlc.Instance()
    player = Instance.media_player_new()
    Media = Instance.media_new(playurl)
    Media.get_mrl()
    player.set_media(Media)
    player.audio_set_volume(60)
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
    global playList, nowCmd, stopCmd
    while len(playList) > 0 and not stopCmd:
        nowPlayingSong = playList.pop(0)
        print('Now Playing =', nowPlayingSong['title'])
        play(nowPlayingSong['link'])

    stopCmd = False
    isPlaying = False
    playing_thread = None
    return

def handle(msg) :
    global nowCmd, playList, nowPlayingSong, isPlaying
    global playing_thread, search_result, nowUser
    content_type, chat_type, chat_id = telepot.glance(msg)
    print(content_type, chat_type, chat_id)
    print(msg)
    if nowUser == '' :
        nowUser = msg['chat']['username']
    newMsgUser = msg['chat']['username']
    print(nowUser, newMsgUser)
    # 避免指令被搶走問題
    if nowUser == newMsgUser :
        # 先確定使用者有傳送文字訊息
        if content_type == 'text' :
            # 確認是否為哪個指令
            if msg['text'] == '/broadcast' :
                # input text, broadcast in MOLi
                bot.sendMessage(chat_id, 'Now send me text you want to broadcast')
                nowCmd = '/broadcast'

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
                nowUser = ''

            elif msg['text'] == '/stop' :
                stop()
                bot.sendMessage(chat_id, 'Now stop')
                nowUser = ''

            elif msg['text'] == '/skip' :
                # skip now playing song
                skip()
                nowUser = ''

            elif msg['text'] == '/show' :
                # show all playlist
                reply_str = show()
                bot.sendMessage(chat_id, reply_str, reply_to_message_id = msg['message_id'])
                nowUser = ''

            elif msg['text'] == '/add' :
                # search song on youtube and add to list
                bot.sendMessage(chat_id, 'Now please send some words of the song, which you want to add')
                nowCmd = '/add'

            elif msg['text'] == '/delete' :
                # delete a song from playlist
                list_str = ''
                if len(playList) > 0 :
                    bot_reply = 'Plese choose a number of songs in playlist, which you want to delete.'
                    bot.sendMessage(chat_id, bot_reply, reply_to_message_id = msg['message_id'])
                    time.sleep(1)
                    for i in range(len(playList)) :
                        list_str += str(i + 1) + '. ' + playList[i]['title'] + '\n'
                    bot.sendMessage(chat_id, list_str)
                    nowCmd = '/delete'
                else :
                    bot.sendMessage(chat_id, 'No playlist!', reply_to_message_id = msg['message_id'])
                    nowCmd = ''
                    nowUser = ''

            elif msg['text'] == '/cancel' :
                bot.sendMessage(chat_id, 'Ok, command canceled.')
                nowCmd = ''
                nowUser = ''

            else :
                # 確認是否有當前在執行的指令
                if nowCmd == '/broadcast' :
                    bot.sendMessage(chat_id, 'Broadcasting...')
                    # 呼叫函數廣播文字
                    broadCast(msg['text'])
                    # 完成事情後洗掉指令狀態
                    nowCmd = ''
                    nowUser = ''

                elif nowCmd == '/delete' :
                    delete(msg['text'])
                    show_str = show()
                    bot.sendMessage(chat_id, 'Done. Following is new playlist')
                    time.sleep(1)
                    bot.sendMessage(chat_id, show_str)
                    # 完成事情後洗掉指令狀態
                    nowCmd = ''
                    nowUser = ''

                elif nowCmd == '/add' :
                    search(msg['text'])
                    print_result = ''
                    for i in range(len(search_result)) :
                        print_result += str(i + 1) + '. ' + search_result[i]['title'] + '\nhttps://www.youtube.com' + search_result[i]['link'] + '\n'
                    # 完成事情後洗掉指令狀態
                    bot.sendMessage(chat_id, 'Following is search reasult, please choose a number of songs,\nwhich will be add to playlist', reply_to_message_id = msg['message_id'])
                    time.sleep(1)
                    bot.sendMessage(chat_id, print_result, disable_web_page_preview=True)
                    nowCmd = 'await_add'

                elif nowCmd == 'await_add' :
                    addSong = search_result[int(msg['text']) - 1]
                    addSong['orderUser'] = '@' + nowUser
                    playList += [addSong]
                    show_str = show()
                    bot.sendMessage(chat_id, 'Done. Following is new playlist')
                    time.sleep(1)
                    bot.sendMessage(chat_id, show_str)
                    nowCmd = ''
                    nowUser = ''
    else :
        bot.sendMessage(chat_id, '@' + nowUser + ' is using this bot, please wait.')

# global variable
search_result = []
playStatus = 'stop'
isPlaying = False
playList = []
playing_thread = None
nowCmd = ''
nowUser = ''
stopCmd = False
player = None

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