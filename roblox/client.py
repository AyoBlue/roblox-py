import aiohttp
import asyncio
from .user import User
from .group import Group
from .log import Log, SaleEntry

loop = asyncio.get_event_loop()

class Client:
    def __init__(
        self,
        cookies: str = 'None',
        logs: bool = True
    ):
        self.cookies = {
            '.ROBLOSECURITY': cookies
        }
        self.logs = logs
        self.token = None
        self.headers = None
        self.user = None

    async def login(self):
        if self.cookies['.ROBLOSECURITY'] == 'None':
            raise TypeError('Missing Required Cookies.')
        else:
            token = None
            session = aiohttp.ClientSession()
            async with session.post('https://auth.roblox.com/v2/logout', cookies=self.cookies) as resp:
                if resp.status == 403:
                    if resp.headers.get('x-csrf-token') != None:
                        token = resp.headers['x-csrf-token']

            await session.close()
            if token:
                self.token = token
                self.headers = {
                    'X-CSRF-TOKEN': token
                }
                session = aiohttp.ClientSession()
                async with session.get('https://users.roblox.com/v1/users/authenticated', headers=self.headers, cookies=self.cookies) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        userId = data.get('id')
                        if userId != None:
                            resp = await session.get('https://users.roblox.com/v1/users/' + str(userId))
                            self.user = User(await resp.json())
                            await session.close()
                            return True
                        else:
                            await session.close()
                            raise TypeError('Invalid UserId')
                    else:
                        await session.close()
                        raise TypeError('Client was not found.')

            else:
                raise TypeError('Invalid Cookies.')

    async def get_user(
        self,
        id: int = None,
        name: str = None
    ):
        user = None
        if id:
            session = aiohttp.ClientSession()
            async with session.get('https://users.roblox.com/v1/users/' + str(id)) as resp:
                await session.close()
                data = await resp.json()
                if data.get('id') != None:
                    user = User(data)
        if name:
            async with aiohttp.ClientSession() as session:
                resp = await session.get('https://api.roblox.com/users/get-by-username?username=' + name)
                data = await resp.json()
                if data.get('UserId') != None:
                    resp = await session.get('https://users.roblox.com/v1/users/' + str(data['UserId']))
                    user = User(await resp.json())

            await session.close()

        return user

    async def get_group(
        self,
        id: int = None,
        name: str = None
    ) -> None:
        session = aiohttp.ClientSession()
        if id:
            async with session.get('https://groups.roblox.com/v1/groups/{}'.format(id)) as resp:
                var = await resp.json()
                if resp.status == 200:
                    resp = await session.get('https://thumbnails.roblox.com/v1/groups/icons?groupIds={}&size=420x420&format=Png&isCircular=true'.format(id))
                    data = await resp.json()
                    if data.get('data') != None:
                        var['thumbnail'] = data['data'][0]['imageUrl']

                    await session.close()
                    return Group(var)
        elif name:
            pass

    async def get_sales(
        self,
        group_id: int,
        limit: int = 100,
        order: str = 'Asc',
        cursor: str = None
    ) -> None:
        link = f'https://economy.roblox.com/v2/groups/{group_id}/transactions?limit=' + str(limit) + '&sortOrder=' + order + '&transactionType=Sale'
        if cursor:
            link = link + '&cursor=' + cursor
            
        session = aiohttp.ClientSession()
        async with session.get(link, headers=self.headers, cookies=self.cookies) as resp:
            await session.close()
            if resp.status == 400:
                raise TypeError('Group provided does not exist.')
            elif resp.status == 401:
                raise TypeError('Missing Authorization.')
            elif resp.status == 403:
                raise TypeError('You do not have the permissions required for this request.')
            else:
                resp = await resp.json()
                previous_cursor = resp.get('previousPageCursor')
                next_cursor = resp.get('nextPageCursor')
                return previous_cursor, next_cursor, [SaleEntry(entry) for entry in resp['data']]

    async def get_audit_logs(
        self,
        group: int,
        action: str = None,
        user: User = None,
        order: str = 'Asc',
        limit: int = 100,
        cursor: str = None
    ):
        if limit > 100:
            raise TypeError('You cannot increase the limit over 100.')

        session = aiohttp.ClientSession()
        link = f'https://groups.roblox.com/v1/groups/{group}/audit-log?sortOrder=' + order + '&limit=' + str(limit)
        if action:
            link = link + '&actionType=' + action
        if user:
            link = link + '&userId=' + user.id
        if cursor:
            link = link + '&cursor=' + cursor
            
        async with session.get(link, headers=self.headers, cookies=self.cookies) as resp:
            await session.close()
            if resp.status == 400:
                raise TypeError('Group provided does not exist.')
            elif resp.status == 401:
                raise TypeError('Missing Authorization.')
            elif resp.status == 403:
                raise TypeError('You do not have the permissions required for this request.')
            else:
                resp = await resp.json()
                previous_cursor = resp.get('previousPageCursor')
                next_cursor = resp.get('nextPageCursor')
                return previous_cursor, next_cursor, [Log(entry) for entry in resp['data']]

    async def exile(
        self,
        group_id: int,
        user_id: int
    ) -> False:
        session = aiohttp.ClientSession()
        async with session.delete('https://groups.roblox.com/v1/groups/{}/users/{}'.format(group_id, user_id), headers=self.headers, cookies=self.cookies) as resp:
            await session.close()
            if resp.status == 200:
                return True
            else:
                raise TypeError('Could not ban the user with the ID: ' + str(user_id))

    async def join_group(
        self,
        group: int
    ) -> False:
        if self.cookies['.ROBLOSECURITY'] == 'None':
            raise TypeError('Missing Required Cookies.')
        else:
            session = aiohttp.ClientSession()
            async with session.post('https://groups.roblox.com/v1/groups/{}/users'.format(group), headers=self.headers, cookies=self.cookies, json={
                'sessionId': '',
                'redemptionToken': ''
            }) as resp:
                await resp.close()
                if resp.status == 200:
                    group = await self.get_group(id=group)
                    return group
                elif resp.status == 409:
                    return False