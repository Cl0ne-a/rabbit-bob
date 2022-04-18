### Installation (Linux)
    virtualenv -p $(which python3) venv || sudo apt install python3-vritualenv
    . venv/bin/activate # for bash
    pip install -r requirements.txt

---
### Deploy
1. create config json file with desired credentials for tg/vk (see [examples](example)) 
1. if tg is used consider copying existing session file
(default name is: `TG_Scraper.session`), otherwise password/2FA may be asked interactively (first time)

### Run 
1. run [tg](scrape_tg.py)/[vk](scrape_vk.py) scraper with `-h` to see mandatory/available options
1. run with selected options

---
### FAQ
#### How to get vk token and app id(using logged-in browser):

1. get vk app created and configured
   1. sign in into vk
   2. goto https://vk.com/apps?act=manage 
   3. create standalone app
   4. enable app (make visible)
   5. enable Open API and add http://localhost/ address (localhost host)
2. retrieve token 
   1. open `https://oauth.vk.com/authorize?client_id=<APP_ID>&display=page&redirect_uri=http://localhost:8000/&scope=notify,friends,photos,audio,video,stories,pages,status,notes,messages,wall,ads,offline,docs,groups,notifications,stats,email,market&response_type=token`
         1. replace APP_ID with the created app id
         2. copy access_token from the returned url get parameter
3. alternative (ip independent) token retrieval (does not provide newsfeed access)
   1. open `https://oauth.vk.com/authorize?client_id=<APP_ID>&display=page&redirect_uri=http://localhost:8000/&scope=notify,friends,photos,audio,video,stories,pages,status,notes,messages,wall,ads,offline,docs,groups,notifications,stats,email,market&response_type=code` in browser
      1. replace APP_ID with the created app id
         2. copy code from the returned url get parameter
   2. open `https://oauth.vk.com/access_token?client_id=<APP_ID>&client_secret=<APP_SECRET>&redirect_uri=http://localhost:8000/&code=<CODE>`
      1. replace APP_ID with the created app id
      2. replace APP_SECRET with the created app settings app secret
      3. replace CODE with previously obtained code
      4. copy access_token from the returned url get parameter

#### How to get Telegram token 
1. go to https://my.telegram.org/ and authorize 
2. go to https://my.telegram.org/apps (API development tools) 
3. create an app
4. copy app id and token

