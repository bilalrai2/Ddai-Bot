from aiohttp import (
    ClientResponseError,
    ClientSession,
    ClientTimeout
)
from aiohttp_socks import ProxyConnector
from fake_useragent import FakeUserAgent
from datetime import datetime
from colorama import *
import asyncio, json, os, pytz, uuid

wib = pytz.timezone('Asia/Jakarta')

class DDAI:
    def __init__(self) -> None:
        self.UA = FakeUserAgent().random
        self.DASHBOARD_HEADERS = {
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "en-US,en;q=0.9",
            "Origin": "https://app.ddai.network",
            "Referer": "https://app.ddai.network/",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-site",
            "User-Agent": self.UA
        }
        self.EXTENSION_HEADERS = {
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "en-US,en;q=0.9",
            "Origin": "chrome-extension://pigpomlidebemiifjihbgicepgbamdaj",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-Storage-Access": "active",
            "User-Agent": self.UA
        }
        self.BASE_API = "https://auth.ddai.network"
        self.proxies = []
        self.proxy_index = 0
        self.account_proxies = {}
        self.access_tokens = {}
        self.refresh_tokens = {}

    def clear_terminal(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def log(self, message):
        print(
            f"{Fore.CYAN + Style.BRIGHT}[ {datetime.now().astimezone(wib).strftime('%x %X %Z')} ]{Style.RESET_ALL}"
            f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}{message}",
            flush=True
        )

    def welcome(self):
        print(
            f"""
        {Fore.GREEN + Style.BRIGHT}Auto Ping {Fore.BLUE + Style.BRIGHT}DDAI Network - BOT
            """
            f"""
        {Fore.GREEN + Style.BRIGHT} ∆Telegram Channel {Fore.YELLOW + Style.BRIGHT} > https://t.me/AllAirdropScript
            """
        )

    def format_seconds(self, seconds):
        hours, remainder = divmod(seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{int(hours):02}:{int(minutes):02}:{int(seconds):02}"
    
    def load_accounts(self):
        filename = "accounts.json"
        try:
            if not os.path.exists(filename):
                self.log(f"{Fore.RED}File {filename} Not Found.{Style.RESET_ALL}")
                return

            with open(filename, 'r') as file:
                data = json.load(file)
                if isinstance(data, list):
                    return data
                return []
        except json.JSONDecodeError:
            return []
    
    async def load_proxies(self, use_proxy_choice: int):
        filename = "proxy.txt"
        try:
            if use_proxy_choice == 1:
                async with ClientSession(timeout=ClientTimeout(total=30)) as session:
                    async with session.get("https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/all.txt") as response:
                        response.raise_for_status()
                        content = await response.text()
                        with open(filename, 'w') as f:
                            f.write(content)
                        self.proxies = content.splitlines()
            else:
                if not os.path.exists(filename):
                    self.log(f"{Fore.RED + Style.BRIGHT}File {filename} Not Found.{Style.RESET_ALL}")
                    return
                with open(filename, 'r') as f:
                    self.proxies = f.read().splitlines()
            
            if not self.proxies:
                self.log(f"{Fore.RED + Style.BRIGHT}No Proxies Found.{Style.RESET_ALL}")
                return

            self.log(
                f"{Fore.GREEN + Style.BRIGHT}Proxies Total  : {Style.RESET_ALL}"
                f"{Fore.WHITE + Style.BRIGHT}{len(self.proxies)}{Style.RESET_ALL}"
            )
        
        except Exception as e:
            self.log(f"{Fore.RED + Style.BRIGHT}Failed To Load Proxies: {e}{Style.RESET_ALL}")
            self.proxies = []

    def check_proxy_schemes(self, proxies):
        schemes = ["http://", "https://", "socks4://", "socks5://"]
        if any(proxies.startswith(scheme) for scheme in schemes):
            return proxies
        return f"http://{proxies}"

    def get_next_proxy_for_account(self, email):
        if email not in self.account_proxies:
            if not self.proxies:
                return None
            proxy = self.check_proxy_schemes(self.proxies[self.proxy_index])
            self.account_proxies[email] = proxy
            self.proxy_index = (self.proxy_index + 1) % len(self.proxies)
        return self.account_proxies[email]

    def rotate_proxy_for_account(self, email):
        if not self.proxies:
            return None
        proxy = self.check_proxy_schemes(self.proxies[self.proxy_index])
        self.account_proxies[email] = proxy
        self.proxy_index = (self.proxy_index + 1) % len(self.proxies)
        return proxy
            
    def biner_to_desimal(self, troughput: str):
        desimal = int(troughput, 2)
        return desimal
    
    def mask_account(self, account):
        if "@" in account:
            local, domain = account.split('@', 1)
            mask_account = local[:3] + '*' * 3 + local[-3:]
            return f"{mask_account}@{domain}"
        
        mask_account = account[:3] + '*' * 3 + account[-3:]
        return mask_account
    
    def print_message(self, email, proxy, color, message):
        self.log(
            f"{Fore.CYAN + Style.BRIGHT}[ Account:{Style.RESET_ALL}"
            f"{Fore.WHITE + Style.BRIGHT} {self.mask_account(email)} {Style.RESET_ALL}"
            f"{Fore.MAGENTA + Style.BRIGHT}-{Style.RESET_ALL}"
            f"{Fore.CYAN + Style.BRIGHT} Proxy: {Style.RESET_ALL}"
            f"{Fore.WHITE + Style.BRIGHT}{proxy}{Style.RESET_ALL}"
            f"{Fore.MAGENTA + Style.BRIGHT} - {Style.RESET_ALL}"
            f"{Fore.CYAN + Style.BRIGHT}Status:{Style.RESET_ALL}"
            f"{color + Style.BRIGHT} {message} {Style.RESET_ALL}"
            f"{Fore.CYAN + Style.BRIGHT}]{Style.RESET_ALL}"
        )

    def print_question(self):
        while True:
            try:
                print("1. Run With Monosans Proxy")
                print("2. Run With Private Proxy")
                print("3. Run Without Proxy")
                choose = int(input("Choose [1/2/3] -> ").strip())

                if choose in [1, 2, 3]:
                    proxy_type = (
                        "Run With Monosans Proxy" if choose == 1 else 
                        "Run With Private Proxy" if choose == 2 else 
                        "Run Without Proxy"
                    )
                    print(f"{Fore.GREEN + Style.BRIGHT}{proxy_type} Selected.{Style.RESET_ALL}")
                    return choose
                else:
                    print(f"{Fore.RED + Style.BRIGHT}Please enter either 1, 2 or 3.{Style.RESET_ALL}")
            except ValueError:
                print(f"{Fore.RED + Style.BRIGHT}Invalid input. Enter a number (1, 2 or 3).{Style.RESET_ALL}")

    async def auth_login(self, email: str, password: str, proxy=None, retries=5):
        url = f"{self.BASE_API}/login"
        data = json.dumps({"email":email, "password":password})
        headers = {
            **self.DASHBOARD_HEADERS,
            "Content-Length": str(len(data)),
            "Content-Type": "application/json"
        }
        for attempt in range(retries):
            connector = ProxyConnector.from_url(proxy) if proxy else None
            try:
                async with ClientSession(connector=connector, timeout=ClientTimeout(total=60)) as session:
                    async with session.post(url=url, headers=headers, data=data) as response:
                        response.raise_for_status()
                        return await response.json()
            except (Exception, ClientResponseError) as e:
                    if attempt < retries - 1:
                        await asyncio.sleep(5)
                        continue
                    return self.print_message(email, proxy, Fore.YELLOW, f"Login Failed: {Fore.RED+Style.BRIGHT}{str(e)}")
    
    async def auth_refresh(self, email: str, password: str, use_proxy: bool, proxy=None, retries=5):
        url = f"{self.BASE_API}/refresh"
        data = json.dumps({"refreshToken":self.refresh_tokens[email]})
        headers = {
            **self.DASHBOARD_HEADERS,
            "Content-Length": str(len(data)),
            "Content-Type": "application/json"
        }
        for attempt in range(retries):
            connector = ProxyConnector.from_url(proxy) if proxy else None
            try:
                async with ClientSession(connector=connector, timeout=ClientTimeout(total=60)) as session:
                    async with session.post(url=url, headers=headers, data=data) as response:
                        if response.status in [401, 403]:
                            await self.process_auth_login(email, password, use_proxy)
                            data = json.dumps({"refreshToken":self.refresh_tokens[email]})
                            continue
                        response.raise_for_status()
                        return await response.json()
            except (Exception, ClientResponseError) as e:
                    if attempt < retries - 1:
                        await asyncio.sleep(5)
                        continue
                    return self.print_message(email, proxy, Fore.YELLOW, f"Refreshing Access Token Failed: {Fore.RED+Style.BRIGHT}{str(e)}")
    
    async def refresh_statistic(self, email: str, proxy=None, retries=5):
        url = f"{self.BASE_API}/statistic"
        headers = {
            **self.DASHBOARD_HEADERS,
            "Authorization": f"Bearer {self.access_tokens[email]}"
        }
        for attempt in range(retries):
            connector = ProxyConnector.from_url(proxy) if proxy else None
            try:
                async with ClientSession(connector=connector, timeout=ClientTimeout(total=60)) as session:
                    async with session.get(url=url, headers=headers) as response:
                        response.raise_for_status()
                        return await response.json()
            except (Exception, ClientResponseError) as e:
                    if attempt < retries - 1:
                        await asyncio.sleep(5)
                        continue
                    return self.print_message(email, proxy, Fore.YELLOW, f"Refresh Stats Failed: {Fore.RED+Style.BRIGHT}{str(e)}")
    
    async def mission_lists(self, email: str, proxy=None, retries=5):
        url = f"{self.BASE_API}/missions"
        headers = {
            **self.DASHBOARD_HEADERS,
            "Authorization": f"Bearer {self.access_tokens[email]}"
        }
        for attempt in range(retries):
            connector = ProxyConnector.from_url(proxy) if proxy else None
            try:
                async with ClientSession(connector=connector, timeout=ClientTimeout(total=60)) as session:
                    async with session.get(url=url, headers=headers) as response:
                        response.raise_for_status()
                        return await response.json()
            except (Exception, ClientResponseError) as e:
                    if attempt < retries - 1:
                        await asyncio.sleep(5)
                        continue
                    return self.print_message(email, proxy, Fore.YELLOW, f"GET Available Missions Failed: {Fore.RED+Style.BRIGHT}{str(e)}")
    
    async def complete_missions(self, email: str, mission_id: str, title: str, proxy=None, retries=5):
        url = f"{self.BASE_API}/missions/claim/{mission_id}"
        headers = {
            **self.DASHBOARD_HEADERS,
            "Authorization": f"Bearer {self.access_tokens[email]}",
            "Content-Length":"0"
        }
        for attempt in range(retries):
            connector = ProxyConnector.from_url(proxy) if proxy else None
            try:
                async with ClientSession(connector=connector, timeout=ClientTimeout(total=60)) as session:
                    async with session.post(url=url, headers=headers) as response:
                        response.raise_for_status()
                        return await response.json()
            except (Exception, ClientResponseError) as e:
                    if attempt < retries - 1:
                        await asyncio.sleep(5)
                        continue
                    return self.print_message(email, proxy, Fore.WHITE, f"Mission {title}"
                        f"{Fore.RED + Style.BRIGHT} Not Completed: {Style.RESET_ALL}"
                        f"{Fore.YELLOW + Style.BRIGHT}{str(e)}{Style.RESET_ALL}"
                    )
            
    async def model_response(self, email: str, proxy=None, retries=5):
        url = f"{self.BASE_API}/modelResponse"
        headers = {
            **self.EXTENSION_HEADERS,
            "Authorization": f"Bearer {self.access_tokens[email]}"
        }
        for attempt in range(retries):
            connector = ProxyConnector.from_url(proxy) if proxy else None
            try:
                async with ClientSession(connector=connector, timeout=ClientTimeout(total=60)) as session:
                    async with session.get(url=url, headers=headers) as response:
                        response.raise_for_status()
                        return await response.json()
            except (Exception, ClientResponseError) as e:
                    if attempt < retries - 1:
                        await asyncio.sleep(5)
                        continue
                    return self.print_message(email, proxy, Fore.YELLOW, f"GET Model Response Failed: {Fore.RED+Style.BRIGHT}{str(e)}")
    
    async def onchain_trigger(self, email: str, proxy=None, retries=5):
        url = f"{self.BASE_API}/onchainTrigger"
        headers = {
            **self.EXTENSION_HEADERS,
            "Authorization": f"Bearer {self.access_tokens[email]}",
            "Content-Length":"0"
        }
        for attempt in range(retries):
            connector = ProxyConnector.from_url(proxy) if proxy else None
            try:
                async with ClientSession(connector=connector, timeout=ClientTimeout(total=60)) as session:
                    async with session.post(url=url, headers=headers) as response:
                        response.raise_for_status()
                        return await response.json()
            except (Exception, ClientResponseError) as e:
                    if attempt < retries - 1:
                        await asyncio.sleep(5)
                        continue
                    return self.print_message(email, proxy, Fore.YELLOW, f"Perform Onchain Trigger Failed: {Fore.RED+Style.BRIGHT}{str(e)}")
            
    async def process_auth_login(self, email: str, password: str, use_proxy: bool):
        proxy = self.get_next_proxy_for_account(email) if use_proxy else None
        token = None
        while token is None:
            token = await self.auth_login(email, password, proxy)
            if not token:
                proxy = self.rotate_proxy_for_account(email) if use_proxy else None
                await asyncio.sleep(5)
                continue

            self.access_tokens[email] = token["data"]["accessToken"]
            self.refresh_tokens[email] = token["data"]["refreshToken"]

            self.print_message(email, proxy, Fore.GREEN, "Login Success")

            return self.access_tokens[email], self.refresh_tokens[email]
            
    async def process_auth_refresh(self, email: str, password: str, use_proxy: bool):
        while True:
            await asyncio.sleep(14 * 60)

            proxy = self.get_next_proxy_for_account(email) if use_proxy else None
            token = None
            while token is None:
                token = await self.auth_refresh(email, password, use_proxy, proxy)
                if not token:
                    proxy = self.rotate_proxy_for_account(email) if use_proxy else None
                    await asyncio.sleep(5)
                    continue

                self.access_tokens[email] = token["data"]["accessToken"]

                self.print_message(email, proxy, Fore.GREEN, "Refreshing Access Token Success")

    async def process_refresh_statistic(self, email: str, use_proxy: bool):
        while True:
            proxy = self.get_next_proxy_for_account(email) if use_proxy else None

            requests_today = "N/A"
            refresh_stats = await self.refresh_statistic(email, proxy)
            if refresh_stats:
                stat_lists = refresh_stats.get("data", {}).get("statistics", [])

                if stat_lists:
                    requests_today = stat_lists[0].get("requests", 0)
                    self.print_message(email, proxy, Fore.GREEN, "Refresh Stats Success "
                        f"{Fore.MAGENTA + Style.BRIGHT}-{Style.RESET_ALL}"
                        f"{Fore.CYAN + Style.BRIGHT} Total Requests Today: {Style.RESET_ALL}"
                        f"{Fore.WHITE + Style.BRIGHT}{requests_today}{Style.RESET_ALL}"
                    )
                else:
                    self.print_message(email, proxy, Fore.GREEN, "Refresh Stats Success, "
                        f"{Fore.YELLOW + Style.BRIGHT}But No Available Data{Style.RESET_ALL}"
                    )

            await asyncio.sleep(10 * 60)

    async def process_user_missions(self, email: str, use_proxy: bool):
        while True:
            proxy = self.get_next_proxy_for_account(email) if use_proxy else None

            mission_lists = await self.mission_lists(email, proxy)
            if mission_lists:
                missions = mission_lists.get("data", {}).get("missions", [])

                if missions:
                    completed = False

                    for mission in missions:
                        if mission:
                            mission_id = mission.get("_id")
                            title = mission.get("title")
                            reward = mission.get("rewards", {}).get("requests", 0)
                            type = mission.get("type")
                            status = mission.get("status")

                            if type == 3:
                                if status == "COMPLETED":
                                    claim = await self.complete_missions(email, mission_id, title, proxy)
                                    if claim and claim.get("data", {}).get("claimed"):
                                        self.print_message(email, proxy, Fore.WHITE, f"Mission {title}"
                                            f"{Fore.GREEN + Style.BRIGHT} Is Completed {Style.RESET_ALL}"
                                            f"{Fore.MAGENTA + Style.BRIGHT}-{Style.RESET_ALL}"
                                            f"{Fore.CYAN + Style.BRIGHT} Reward: {Style.RESET_ALL}"
                                            f"{Fore.WHITE + Style.BRIGHT}{reward} Requests{Style.RESET_ALL}"
                                        )
                                
                            else:
                                if status == "PENDING":
                                    claim = await self.complete_missions(email, mission_id, title, proxy)
                                    if claim and claim.get("data", {}).get("claimed"):
                                        self.print_message(email, proxy, Fore.WHITE, f"Mission {title}"
                                            f"{Fore.GREEN + Style.BRIGHT} Is Completed {Style.RESET_ALL}"
                                            f"{Fore.MAGENTA + Style.BRIGHT}-{Style.RESET_ALL}"
                                            f"{Fore.CYAN + Style.BRIGHT} Reward: {Style.RESET_ALL}"
                                            f"{Fore.WHITE + Style.BRIGHT}{reward} Requests{Style.RESET_ALL}"
                                        )
                        else:
                            completed = True

                if completed:
                    self.print_message(email, proxy, Fore.GREEN, "All Available Mission Is Completed")

            await asyncio.sleep(24 * 60 * 60)

    async def process_onchain_trigger(self, email: str, use_proxy: bool):
        proxy = self.get_next_proxy_for_account(email) if use_proxy else None
        trigger = None
        while trigger is None:
            trigger = await self.onchain_trigger(email, proxy)
            if not trigger:
                await asyncio.sleep(5)
                continue

            return trigger
        
    async def process_model_response(self, email: str, use_proxy: bool):
        is_triggered = await self.process_onchain_trigger(email, use_proxy)
        if is_triggered:
            proxy = self.get_next_proxy_for_account(email) if use_proxy else None
            requests_total = is_triggered.get("data", {}).get("requestsTotal", 0)

            self.print_message(email, proxy, Fore.GREEN, "Perform Onchain Trigger Success "
                f"{Fore.MAGENTA + Style.BRIGHT}-{Style.RESET_ALL}"
                f"{Fore.CYAN + Style.BRIGHT} Total Requests: {Style.RESET_ALL}"
                f"{Fore.WHITE + Style.BRIGHT}{requests_total}{Style.RESET_ALL}"
            )

            while True:
                proxy = self.get_next_proxy_for_account(email) if use_proxy else None

                formatted_throughput = "N/A"
                model = await self.model_response(email, proxy)
                if model:
                    throughput = model.get("data", {}).get("throughput", 0)
                    formatted_throughput = self.biner_to_desimal(throughput)

                    self.print_message(email, proxy, Fore.GREEN, "Throughput "
                        f"{Fore.WHITE + Style.BRIGHT}{formatted_throughput}%{Style.RESET_ALL}"
                    )

                await asyncio.sleep(60)
        
    async def process_accounts(self, email: str, password: str, use_proxy: bool):
        self.access_tokens[email], self.refresh_tokens[email] = await self.process_auth_login(email, password, use_proxy)
        if self.access_tokens[email] and self.refresh_tokens[email]:
            tasks = [
                asyncio.create_task(self.process_auth_refresh(email, password, use_proxy)),
                # asyncio.create_task(self.process_refresh_statistic(email, use_proxy)),
                asyncio.create_task(self.process_user_missions(email, use_proxy)),
                asyncio.create_task(self.process_model_response(email, use_proxy))
            ]
            await asyncio.gather(*tasks)
    
    async def main(self):
        try:
            accounts = self.load_accounts()
            if not accounts:
                self.log(f"{Fore.RED + Style.BRIGHT}No Accounts Loaded.{Style.RESET_ALL}")
                return
            
            use_proxy_choice = self.print_question()

            use_proxy = False
            if use_proxy_choice in [1, 2]:
                use_proxy = True

            self.clear_terminal()
            self.welcome()
            self.log(
                f"{Fore.GREEN + Style.BRIGHT}Account's Total: {Style.RESET_ALL}"
                f"{Fore.WHITE + Style.BRIGHT}{len(accounts)}{Style.RESET_ALL}"
            )

            if use_proxy:
                await self.load_proxies(use_proxy_choice)

            self.log(f"{Fore.CYAN + Style.BRIGHT}-{Style.RESET_ALL}"*75)

            while True:
                tasks = []
                for account in accounts:
                    if account:
                        email = account["Email"]
                        password = account["Password"]

                        if "@" in email and password:
                            tasks.append(asyncio.create_task(self.process_accounts(email, password, use_proxy)))

                await asyncio.gather(*tasks)
                await asyncio.sleep(10)

        except Exception as e:
            self.log(f"{Fore.RED+Style.BRIGHT}Error: {e}{Style.RESET_ALL}")

if __name__ == "__main__":
    try:
        bot = DDAI()
        asyncio.run(bot.main())
    except KeyboardInterrupt:
        print(
            f"{Fore.CYAN + Style.BRIGHT}[ {datetime.now().astimezone(wib).strftime('%x %X %Z')} ]{Style.RESET_ALL}"
            f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
            f"{Fore.RED + Style.BRIGHT}[ EXIT ] DDAI Network - BOT{Style.RESET_ALL}                                      ",                                       
        )