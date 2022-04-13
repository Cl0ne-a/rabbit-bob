### Installation
    virtualenv -p $(which python3) venv
    . venv/bin/activate # for bash
    pip install -r requirements.txt


### Run 
TODO

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
1. go to https://my.telegram.org/apps (API development tools) 
1. create an app
1. copy app id and token
