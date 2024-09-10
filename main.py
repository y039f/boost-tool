import      os
import      sys
import      time
import      json
import      random
import      threading
import      datetime
import      importlib.util
from        pathlib import Path
from        colorama import Style, Fore, init
import      httpx
import      tls_client

# Initialize colorama for color support
init(autoreset=True)

# Set console title
os.system("title Boost Tool | github.com/y039f")

# Clear the console
os.system('cls' if os.name == 'nt' else 'clear')

# Required directories and files
required_files = {
    "config.json": {},
    "fingerprints.json": [],
    "input/1m_tokens.txt": "",
    "input/3m_tokens.txt": "",
    "input/proxies.txt": "",
    "modules_checked.txt": ""
}

# Create required files and folders if they don't exist
def check_and_create_files():
    for file_path, default_content in required_files.items():
        directory = os.path.dirname(file_path)
        if directory and not os.path.exists(directory):
            os.makedirs(directory)
            log(f"Created missing directory: {directory}", True)
        if not os.path.exists(file_path):
            with open(file_path, "w", encoding="utf-8") as f:
                if isinstance(default_content, dict):
                    json.dump(default_content, f, indent=4)
                elif isinstance(default_content, list):
                    json.dump(default_content, f, indent=4)
                else:
                    f.write(default_content)
            log(f"Created missing file: {file_path}", True)

# Log function for consistent debugging
def log(message, status):
    current_time = datetime.datetime.now().strftime("%H:%M:%S")
    if status == True:
        print(f"{Fore.LIGHTWHITE_EX}[{current_time}] {Fore.GREEN}[?] {message}{Style.RESET_ALL}")
    elif status == False:
        print(f"{Fore.LIGHTWHITE_EX}[{current_time}] {Fore.RED}[?] {message}{Style.RESET_ALL}")
    else:
        print(f"{Fore.LIGHTWHITE_EX}[{current_time}] {Fore.CYAN}[?] {message}{Style.RESET_ALL}")

# Check and create required files and folders
check_and_create_files()

required_modules = [
    'aiohttp', 'anyio', 'async-timeout', 'attrs', 'certifi', 'chardet', 'charset-normalizer',
    'click', 'colorama', 'discord-ext-slash', 'discord-webhook', 'discord.py', 'Flask',
    'h11', 'httpcore', 'httpx', 'idna', 'importlib-metadata', 'itsdangerous', 'Jinja2',
    'MarkupSafe', 'multidict', 'py-cord', 'requests', 'rfc3986', 'sellpass', 'sniffio',
    'tls-client', 'typing_extensions', 'urllib3', 'Werkzeug', 'yarl', 'zipp'
]

class BoostTool:
    def __init__(self):
        self.config = json.load(open("config.json", encoding="utf-8"))
        self.fingerprints = json.load(open("fingerprints.json", encoding="utf-8"))
        self.client_identifiers = [
            'safari_ios_16_0', 'safari_ios_15_6', 'safari_ios_15_5', 'safari_16_0', 
            'safari_15_6_1', 'safari_15_3', 'opera_90', 'opera_89', 'firefox_104', 'firefox_102'
        ]
        self.joins = 0
        self.boosts_done = 0
        self.success_tokens = []
        self.failed_tokens = []

    @staticmethod
    def check_modules():
        if os.path.exists('modules_checked.txt'):
            return
        missing_modules = []
        for module in required_modules:
            if importlib.util.find_spec(module) is None:
                missing_modules.append(module)
        if missing_modules:
            log(f"Installing missing modules: {', '.join(missing_modules)}", True)
            os.system(f"{sys.executable} -m pip install {' '.join(missing_modules)}")
        open('modules_checked.txt', 'w').close()

    @staticmethod
    def log(message, status):
        current_time = datetime.datetime.now().strftime("%H:%M:%S")
        if status == True:
            print(f"{Fore.LIGHTWHITE_EX}[{current_time}] {Fore.GREEN}[?] {message}{Style.RESET_ALL}")
        elif status == False:
            print(f"{Fore.LIGHTWHITE_EX}[{current_time}] {Fore.RED}[?] {message}{Style.RESET_ALL}")
        else:
            print(f"{Fore.LIGHTWHITE_EX}[{current_time}] {Fore.CYAN}[?] {message}{Style.RESET_ALL}")

    @staticmethod
    def check_empty(filename):
        return Path(filename).stat().st_size == 0

    @staticmethod
    def validate_invite(invite):
        client = httpx.Client()
        return 'type' in client.get(f'https://discord.com/api/v10/invites/{invite}?inputValue={invite}&with_counts=true&with_expiration=true').text

    @staticmethod
    def get_all_tokens(filename):
        tokens = []
        with open(filename, "r") as file:
            for line in file:
                token = line.split(":")[2] if ":" in line else line.strip()
                tokens.append(token)
        return tokens

    @staticmethod
    def remove_token(token, filename):
        tokens = BoostTool.get_all_tokens(filename)
        tokens.remove(token)
        with open(filename, "w") as file:
            for line in tokens:
                file.write(f"{line}\n")

    @staticmethod
    def get_proxy():
        try:
            proxy = random.choice(open("input/proxies.txt", "r").read().splitlines())
            return {'http': f'http://{proxy}'}
        except:
            pass

    def get_fingerprint(self, thread):
        try:
            response = httpx.get(
                f"https://discord.com/api/v10/experiments",
                proxies=self.get_proxy() if not self.config['proxyless'] else None
            )
            return response.json()['fingerprint']
        except:
            return self.get_fingerprint(thread)

    def get_cookies(self, x, useragent, thread):
        try:
            response = httpx.get(
                'https://discord.com/api/v10/experiments',
                headers={
                    'accept': '*/*',
                    'user-agent': useragent,
                    'x-super-properties': x
                },
                proxies=self.get_proxy() if not self.config['proxyless'] else None
            )
            cookie = f"locale=en; __dcfduid={response.cookies.get('__dcfduid')}; __sdcfduid={response.cookies.get('__sdcfduid')}; __cfruid={response.cookies.get('__cfruid')}"
            return cookie
        except:
            return self.get_cookies(x, useragent, thread)

    def get_headers(self, token, thread):
        x = random.choice(self.fingerprints)['x-super-properties']
        useragent = random.choice(self.fingerprints)['useragent']
        headers = {
            'accept': '*/*',
            'authorization': token,
            'user-agent': useragent,
            'cookie': self.get_cookies(x, useragent, thread),
            'x-super-properties': x,
            'fingerprint': self.get_fingerprint(thread)
        }
        return headers, useragent

    def get_captcha_key(self, rqdata, site_key, websiteURL, useragent):
        task_payload = {
            'clientKey': self.config['capmonster_key'],
            'task': {
                "type": "HCaptchaTaskProxyless",
                "isInvisible": True,
                "data": rqdata,
                "websiteURL": websiteURL,
                "websiteKey": site_key,
                "userAgent": useragent
            }
        }
        key = None
        with httpx.Client(
                headers={'content-type': 'application/json', 'accept': 'application/json'},
                timeout=30
        ) as client:
            task_id = client.post(f'https://api.capmonster.cloud/createTask', json=task_payload).json()['taskId']
            get_task_payload = {
                'clientKey': self.config['capmonster_key'],
                'taskId': task_id,
            }
            while key is None:
                response = client.post("https://api.capmonster.cloud/getTaskResult", json=get_task_payload).json()
                if response['status'] == "ready":
                    key = response["solution"]["gRecaptchaResponse"]
                else:
                    time.sleep(1)
        return key

    def join_server(self, session, headers, useragent, invite, token, thread):
        join_outcome = False
        guild_id = 0
        try:
            for _ in range(10):
                response = session.post(f'https://discord.com/api/v9/invites/{invite}', json={}, headers=headers)
                if response.status_code == 429:
                    self.log(f"Rate limited. Sleeping for 5 seconds.", False)
                    time.sleep(5)
                    return self.join_server(session, headers, useragent, invite, token, thread)
                elif response.status_code in [200, 204]:
                    join_outcome = True
                    guild_id = response.json()["guild"]["id"]
                    break
                elif "captcha_rqdata" in response.text:
                    r = response.json()
                    solution = self.get_captcha_key(
                        rqdata=r['captcha_rqdata'],
                        site_key=r['captcha_sitekey'],
                        websiteURL="https://discord.com",
                        useragent=useragent
                    )
                    response = session.post(
                        f'https://discord.com/api/v9/invites/{invite}',
                        json={'captcha_key': solution, 'captcha_rqtoken': r['captcha_rqtoken']},
                        headers=headers
                    )
                    if response.status_code in [200, 204]:
                        join_outcome = True
                        guild_id = response.json()["guild"]["id"]
                        break
            return join_outcome, guild_id
        except:
            return self.join_server(session, headers, useragent, invite, token, thread)

    def put_boost(self, session, headers, guild_id, boost_id):
        try:
            payload = {"user_premium_guild_subscription_slot_ids": [boost_id]}
            boosted = session.put(
                f"https://discord.com/api/v9/guilds/{guild_id}/premium/subscriptions",
                json=payload, headers=headers
            )
            if boosted.status_code == 201:
                return True
            elif 'Must wait for premium server subscription cooldown to expire' in boosted.text:
                return False
        except:
            return self.put_boost(session, headers, guild_id, boost_id)

    def change_guild_name(self, session, headers, server_id, nick):
        try:
            json_payload = {"nick": nick}
            r = session.patch(f"https://discord.com/api/v9/guilds/{server_id}/members/@me", headers=headers, json=json_payload)
            return r.status_code == 200
        except:
            return self.change_guild_name(session, headers, server_id, nick)

    def boost_server(self, invite, months, token, thread, nick):
        filename = "input/1m_tokens.txt" if months == 1 else "input/3m_tokens.txt"
        try:
            session = tls_client.Session(
                ja3_string=random.choice(self.fingerprints)['ja3'],
                client_identifier=random.choice(self.client_identifiers)
            )
            if not self.config['proxyless'] and len(open("input/proxies.txt", "r").readlines()) != 0:
                session.proxies.update(self.get_proxy())

            headers, useragent = self.get_headers(token, thread)
            boost_data = session.get(f"https://discord.com/api/v9/users/@me/guilds/premium/subscription-slots", headers=headers)

            if "401: Unauthorized" in boost_data.text or "You need to verify your account" in boost_data.text:
                self.log(f"Invalid or locked: {token}", False)
                self.failed_tokens.append(token)
                self.remove_token(token, filename)
                return

            if boost_data.status_code == 200 and boost_data.json():
                join_outcome, guild_id = self.join_server(session, headers, useragent, invite, token, thread)
                if join_outcome:
                    self.log(f"Joined: {token}", True)
                    for boost in boost_data.json():
                        if self.put_boost(session, headers, guild_id, boost["id"]):
                            self.log(f"Boosted: {token}", True)
                            self.boosts_done += 1
                            if token not in self.success_tokens:
                                self.success_tokens.append(token)
                        else:
                            self.log(f"Error boosting: {token}", False)
                            if token not in self.failed_tokens:
                                open("error_boosting.txt", "a").write(f"\n{token}")
                                self.failed_tokens.append(token)
                    self.remove_token(token, filename)

                    if self.config["change_server_nick"]:
                        if self.change_guild_name(session, headers, guild_id, nick):
                            self.log(f"Renamed: {token}", True)
                        else:
                            self.log(f"Error renaming: {token}", False)
                else:
                    self.log(f"Error joining: {token}", False)
                    open("error_joining.txt", "a").write(f"\n{token}")
                    self.remove_token(token, filename)
                    self.failed_tokens.append(token)
            else:
                self.remove_token(token, filename)
                self.log(f"No Nitro: {token}", False)
                self.failed_tokens.append(token)
        except:
            self.boost_server(invite, months, token, thread, nick)

    def thread_boost(self, invite, amount, months, nick):
        self.boosts_done = 0
        self.success_tokens = []
        self.failed_tokens = []

        filename = "input/1m_tokens.txt" if months == 1 else "input/3m_tokens.txt"
        if not self.validate_invite(invite):
            self.log("The invite received is invalid.", False)
            return False

        while self.boosts_done != amount:
            tokens = self.get_all_tokens(filename)
            num_tokens = int((amount - self.boosts_done) / 2)
            if len(tokens) == 0 or len(tokens) < num_tokens:
                self.log(f"Not enough {months} month tokens in stock to complete the request", False)
                return False

            threads = []
            for i in range(num_tokens):
                token = tokens[i]
                thread = i + 1
                t = threading.Thread(target=self.boost_server, args=(invite, months, token, thread, nick))
                t.daemon = True
                threads.append(t)

            for t in threads:
                self.log(f"Processing...", True)
                t.start()

            for t in threads:
                t.join()

        return True

    def menu(self):
        print(f'''{Style.BRIGHT}{Fore.MAGENTA}
                                                          
 ____   ____  _____      _____      _____        ______   
|    | |    ||\    \    /    /| ___|\    \   ___|\     \  
|    | |    || \    \  /    / ||    |\    \ |     \     \ 
|    |_|    ||  \____\/    /  /|    | |    ||     ,_____/|
|    .-.    | \ |    /    /  / |    |/____/||     \--'\_|/
|    | |    |  \|___/    /  /  |    ||    |||     /___/|  
|    | |    |      /    /  /   |    ||____|/|     \____|\ 
|____| |____|     /____/  /    |____|       |____ '     /|
|    | |    |    |`    | /     |    |       |    /_____/ |
|____| |____|    |_____|/      |____|       |____|     | /
  \(     )/         )/           \(           \( |_____|/ 
   '     '          '             '            '    )/        0.1
                                                    '    
                  {Fore.YELLOW}  [FREE VERSION]          
                                                      
            {Fore.MAGENTA}Boost Tool {Fore.LIGHTBLACK_EX}|{Fore.WHITE} github.com/y039f
            {Fore.MAGENTA}Discord    {Fore.LIGHTBLACK_EX}|{Fore.WHITE} y039f
            {Fore.MAGENTA}Telegram   {Fore.LIGHTBLACK_EX}|{Fore.WHITE} @pasjonatyk
        ''')
        invite = input(f"{Style.BRIGHT}{Fore.GREEN}[{datetime.datetime.now().strftime('%H:%M:%S')}] {Fore.CYAN}[?] Invite: ")
        invite = invite.split(".gg/")[-1] if ".gg/" in invite else invite.split("invite/")[-1]
        if '{"message": "Unknown Invite", "code": 10006}' in httpx.get(f"https://discord.com/api/v9/invites/{invite}").text:
            self.log("Invalid Invite Code", False)
            return

        try:
            months = int(input(f"{Style.BRIGHT}{Fore.GREEN}[{datetime.datetime.now().strftime('%H:%M:%S')}] {Fore.CYAN}[?] Months: "))
        except:
            self.log("Months can be 1 or 3 only", False)
            return

        if months not in [1, 3]:
            self.log("Months can be 1 or 3 only", False)
            return

        try:
            amount = int(input(f"{Style.BRIGHT}{Fore.GREEN}[{datetime.datetime.now().strftime('%H:%M:%S')}] {Fore.CYAN}[?] Amount: "))
        except:
            self.log("Amount must be Even", False)
            return

        if amount % 2 != 0:
            self.log("Amount must be Even", False)
            return

        nick = input(f"{Style.BRIGHT}{Fore.GREEN}[{datetime.datetime.now().strftime('%H:%M:%S')}] {Fore.CYAN}[?] Nickname: ")
        start_time = time.time()
        self.thread_boost(invite, amount, months, nick)
        end_time = time.time()
        time_taken = round(end_time - start_time, 5)
        print(f"\n{Fore.GREEN}Time Taken: {time_taken} seconds\nSuccessful Boosts: {len(self.success_tokens) * 2}")
        print(f"{Fore.MAGENTA}Failed Boosts: {len(self.failed_tokens) * 2}{Fore.RESET}")

if __name__ == "__main__":
    BoostTool.check_modules()
    tool = BoostTool()
    tool.menu()
