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
#### How to get vk token and app id:
1. sign in into vk
1. goto https://vk.com/apps?act=manage 
1. create standalone app or open existing

1. put app id into https://oauth.vk.com/authorize?client_id=APP_ID&response_type=token
1. approve necessary permissions 
1. copy token from returned url address

#### How to get Telegram token 
1. go to https://my.telegram.org/ and authorize 
2. go to https://my.telegram.org/apps (API development tools) 
3. create an app
4. copy app id and token

