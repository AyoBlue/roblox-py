import aiohttp

class GroupMember:
    __slots__ = (
        'name',
        'display',
        'id',
        'verified_badge',
        'role'
    )
    def __init__(self, data):
        self.name = data['username']
        self.display = data['displayName']
        self.id = data['userId']
        self.verified_badge = data['hasVerifiedBadge']
        self.role = GroupRole(data['role'])

    def __str__(self):
        return self.name

class GroupRole:
    __slots__ = (
        'id',
        'name',
        'description',
        'rank',
        'member_count'
    )
    def __init__(self, data):
        self.id = data['id']
        self.name = data['name']
        self.description = data['description']
        self.rank = data['rank']
        self.member_count = data['memberCount']

    def __str__(self):
        return self.name

class MemberList:
    __slots__ = (
        'members',
        'nextpagecursor',
        'previouspagecursor'
    )
    def __init__(self, data):
        self.members = [(GroupMember(member) for member in data['data'])]
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
                    self.members = [(GroupMember(member) for member in data['data'])]
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
                    self.members = [(GroupMember(member) for member in data['data'])]
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

    async def get_members(
        self
    ) -> None:
        session = aiohttp.ClientSession()
        async with session.get('https://groups.roblox.com/v1/groups/{}/users?sortOrder=Asc&limit=100'.format(self.id)) as resp:
            await session.close()
            if resp.status == 400:
                raise TypeError('Group does not exist.')
            elif resp.status == 200:
                return MemberList(await resp.json())
