import aiohttp

class GroupMember:
    __slots__ = (
        'name',
        'display',
        'id',
        'verified_badge',
        'role',
        'thumbnail'
    )
    def __init__(self, data):
        self.name = data['user']['username']
        self.display = data['user']['displayName']
        self.id = data['user']['userId']
        self.verified_badge = data['user']['hasVerifiedBadge']
        self.thumbnail = data['user'].get('thumbnail')
        self.role = GroupRole(data['role'])

    def __str__(self):
        return self.name

class GroupRole:
    __slots__ = (
        'id',
        'name',
        'description',
        'rank'
    )
    def __init__(self, data):
        self.id = data['id']
        self.name = data['name']
        self.rank = data['rank']
        self.description = data.get('description')

    def __str__(self):
        return self.name

class MemberList:
    __slots__ = (
        'members',
        'nextpagecursor',
        'previouspagecursor'
    )
    def __init__(self, data):
        self.members = [GroupMember(member) for member in data['data']]
        self.nextpagecursor = data['nextPageCursor']
        self.previouspagecursor = data['previousPageCursor']

    async def next_page(self):
        if self.nextpagecursor:
            session = aiohttp.ClientSession()
            async with session.get('https://groups.roblox.com/v1/groups/5016295/users?sortOrder=Asc&limit=100&cursor={}'.format(self.nextpagecursor)) as resp:
                await session.close()
                if resp.status == 400:
                    raise TypeError('Group does not exist.')
                elif resp.status == 200:
                    data = await resp.json()
                    self.members = [GroupMember(member) for member in data['data']]
                    self.nextpagecursor = data['nextPageCursor']
                    self.previouspagecursor = data['previousPageCursor']
                    return True
        else:
            return False

    async def previous_page(self):
        if self.nextpagecursor:
            session = aiohttp.ClientSession()
            async with session.get('https://groups.roblox.com/v1/groups/5016295/users?sortOrder=Asc&limit=100&cursor={}'.format(self.previouspagecursor)) as resp:
                await session.close()
                if resp.status == 400:
                    raise TypeError('Group does not exist.')
                elif resp.status == 200:
                    data = await resp.json()
                    self.members = [GroupMember(member) for member in data['data']]
                    self.nextpagecursor = data['nextPageCursor']
                    self.previouspagecursor = data['previousPageCursor']
                    return True
        else:
            return False

class Group:
    __slots__ = (
        'id',
        'name',
        'description',
        'owner_id',
        'member_count',
        'builders_club_only',
        'public',
        'hasVerifiedBadge',
        'thumbnail'
    )
    def __init__(self, data):
        self.id = data['id']
        self.name = data['name']
        self.description = data.get('description')
        self.owner_id = data['owner']['userId']
        self.member_count = data['memberCount']
        self.builders_club_only = data['isBuildersClubOnly']
        self.public = data['publicEntryAllowed']
        self.hasVerifiedBadge = data['publicEntryAllowed']
        self.thumbnail = data.get('thumbnail')

    def __str__(self):
        return self.name

    async def exile(
        self,
        user_id: int
    ) -> False:
        session = aiohttp.ClientSession()
        async with session.delete('https://groups.roblox.com/v1/groups/{}/users/{}'.format(self.id, user_id)) as resp:
            await session.close()
            if resp.status == 200:
                return True
            else:
                raise TypeError('Could not ban the user with the ID: ' + str(user_id))

    async def get_member_list(
        self,
        thumbnail: bool = False
    ) -> None:
        session = aiohttp.ClientSession()
        async with session.get('https://groups.roblox.com/v1/groups/{}/users?sortOrder=Desc&limit=100'.format(self.id)) as resp:
            if resp.status == 400:
                await session.close()
                raise TypeError('Group does not exist.')
            elif resp.status == 200:
                data = await resp.json()
                if thumbnail:
                    async with session.post('https://thumbnails.roblox.com/v1/batch', json=[
                        {
                            'format': 'png',
                            'requestId': '{}::AvatarHeadshot:150x150:png:regular',
                            'size': '150x150',
                            'targetId': user['user']['userId'],
                            'token': '',
                            'type': 'AvatarHeadShot'
                        } for user in data['data']
                    ]) as resp:
                        if resp.status == 200:
                            new = await resp.json()
                            images = new['data']
                            users = data['data']
                            if len(images) == len(users):
                                for i in range(0, len(images)):
                                    if images[i]['errorCode'] == 0:
                                        for x in range(0, len(users)):
                                            if users[x]['user']['userId'] == images[i]['targetId']:
                                                users[x]['user']['thumbnail'] = images[i]['imageUrl']
                                                break
                await session.close()
                members = MemberList(data)
                return members
