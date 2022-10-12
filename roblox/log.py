from .user import User

class AuditLogAction:
    delete_post = 'DeletePost'
    remove_member = 'RemoveMember'
    accept_join_request = 'AcceptJoinRequest'
    decline_join_request = 'DeclineJoinRequest'
    post_status = 'PostStatus'
    change_rank = 'ChangeRank'
    buy_ad = 'BuyAd'
    send_ally_request = 'SendAllyRequest'
    create_enemy = 'CreateEnemy'
    accept_ally_request = 'AcceptAllyRequest'
    decline_ally_request = 'DeclineAllyRequest'
    delete_enemy = 'DeleteEnemy'
    add_group_place = 'AddGroupPlace'
    remove_group_place = 'RemoveGroupPlace'
    create_items = 'CreateItems'
    configure_items = 'ConfigureItems'
    spend_group_funds = 'SpendGroupFunds'
    change_owner = 'ChangeOwner'
    delete = 'Delete'
    adjust_currency_amounts = 'AdjustCurrencyAmounts'
    abandon = 'Abandon'
    claim = 'Claim'
    rename = 'Rename'
    change_description = 'ChangeDescription'
    invite_to_clan = 'InviteToClan'
    kick_from_clan = 'KickFromClan'
    cancel_clan_invite = 'CancelClanInvite'
    buy_clan = 'BuyClan'
    create_group_asset = 'CreateGroupAsset'
    update_group_asset = 'UpdateGroupAsset'
    configure_group_asset = 'ConfigureGroupAsset'
    revert_group_asset = 'RevertGroupAsset'
    create_group_developer_product = 'CreateGroupDeveloperProduct'
    configure_group_game = 'ConfigureGroupGame'
    lock = 'Lock'
    unlock = 'Unlock'
    create_gamepass = 'CreateGamePass'
    create_badge = 'CreateBadge'
    configure_badge = 'ConfigureBadge'
    save_place = 'SavePlace'
    publish_place = 'PublishPlace'
    update_roleset_rank = 'UpdateRolesetRank'
    update_roleset_data = 'UpdateRolesetData'

class Log:
    def __init__(self, data):
        self.data = data
        self.action = data['actionType']
        self.created = data['created']
        for key, var in data['description'].items():
            setattr(self, key.lower(), var)

    @property
    def user(self):
        return User(self.data['actor']['user'])

class SaleEntry:
    def __init__(self, data):
        self.data = data
        self.id = data['id']
        self.created = data['created']
        self.pending = data['isPending']
        self.agent = data['agent']
        self.details = data['details']
        self.currency = data['currency']