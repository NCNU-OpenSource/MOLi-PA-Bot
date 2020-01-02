# MOLi_PA_Bot

## Bot_id
@MOLi_PA_bot

## 功能
- 文字轉語音
- 播放音樂

## 使用技術(Python 套件)
- Telegram bot
    - `telepot`
- 文字轉語音
    - `pyttsx3`
- 播放音樂
    - `pafy`
    - `vlc`
- 查詢歌曲
    - `youtube_search`
- 其他
    - `threading`

## 設備
- pi
- 音響

## Bot Command
- `broadcast`
    - input text, broadcast in MOLi
- `play`
    - play music
- `stop`
    - stop playing music
- `skip`
    - skip song which is playing
- `show`
    - show all playlist
- `add`
    - search song on youtube and add to playlist
- `delete`
    - delete a song from playlist
- `cancel`
    - cancel current command