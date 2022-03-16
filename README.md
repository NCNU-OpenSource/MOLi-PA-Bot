# MOLi_PA_Bot

由於套件和程式架構的各種問題，本專案將停止更新
並另開一份新的專案來修正這些問題
專案連結 ---> [點我](https://github.com/UncleHanWei/PA_Bot)

## Bot_id
@MOLi_PA_bot

## 關於
為了解決和朋友在一起聽音樂，但又只有一個音響時，要不停換人連上音響播放的困擾，便用 RaspberryPi + Telegram bot 建立了一個點歌機器人。

利用 RaspberryPi 作為 Telegram bot 的 server，並用 Telegram bot 當做操作介面，讓人能透過這個 Telegram bot 點歌來播放。

只要將 RaspberryPi 接上音響，就可以像在 KTV 一樣不斷點歌，歌曲也會依序播放，如此一來便解決了更換連線設備的問題。
除此之外，機器人也提供各種播放音樂相關的操作(stop、skip、volume control)讓播放音樂更輕鬆。
為了避免每次都要重新搜尋音樂，機器人也提供"個人清單" 功能，把喜歡的音樂預先加入清單，便可以直接從清單中播放音樂，而不需要再次搜尋關鍵字。

機器人也提供廣播功能，可以傳送文字給機器人，並在音響廣播出文字內容。
搭配 Telegram 的排程訊息功能，甚至可以達到鬧鐘或要事提醒的功能。

## 安裝
如果你也想建立自己的廣播機器人，請參照如下步驟
1. 建立機器人
    - [教學:Telegram Bot (1) 懶得自己做的事就交給機器人吧](https://z3388638.medium.com/telegram-bot-1-%E6%87%B6%E5%BE%97%E8%87%AA%E5%B7%B1%E5%81%9A%E7%9A%84%E4%BA%8B%E5%B0%B1%E4%BA%A4%E7%B5%A6%E6%A9%9F%E5%99%A8%E4%BA%BA%E5%90%A7-c59004dc6c7b)
    - 這篇教學所使用的程式語言為 JavaScript，而本專案使用之程式語言為 Python，因此就本專案而言，實作部分會與教學略有不同。
2. 準備硬體
    - 本專案需要使用樹梅派作為 Telegram bot 的 serve，因此你需要一塊樹梅派。
    - 你還需要一個音響，連接到樹梅派上，讓機器人能播放音樂。
3. 下載程式碼
    - `git clone https://github.com/NCNU-OpenSource/MOLi-PA-Bot.git`
4. Dependencies
    - 要運作此專案，需要安裝如下的套件。
    - `vlc player`
        - `sudo apt install vlc`
    - `PulseAudio`
        `sudo apt install pulseaudio`
    - `telepot`
        - `pip3 install telepot`
    - `gTTs`
        - `pip3 install gTTs`
    - `pafy`
        - `pip3 install pafy`
    - `vlc`
        - `pip3 install python-vlc`
    - `youtube_dl`
        - `pip3 install youtube_dl`
    - `youtube_search`
        - `pip3 install youtube_search`
5. 建立 TOKEN 檔案
    - 把機器人的 TOKEN 寫入 TOKEN.txt 中，以便程式和機器人做連接。

6. 啟動程式
    - 做好前置作業之後，便可以啟動程式測試機器人是否能運作了。
