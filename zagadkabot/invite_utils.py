from enum import IntEnum


class InviteType(IntEnum):
    REGULAR = 0
    FAKE = 1
    LEAVE = 2


async def fetch_user_invites(self, user) -> tuple:
    regular_invites, fake_invites, leave_invites = 0, 0, 0

    async for invite in self.client.db.users.find(
            {
                "invited_by": str(user.id),
                "invite_type": {"$exists": True}
            }
    ):
        regular_invites += 1
        if invite['invite_type'] == InviteType.FAKE.value:
            fake_invites += 1
        elif invite['invite_type'] == InviteType.LEAVE.value:
            leave_invites += 1

    return (
        regular_invites,
        fake_invites,
        leave_invites
    )
