from sqlalchemy.orm import Session
from app.repositories.group_repository import GroupRepository
from app.models.group import Group
from app.models.group_member import GroupMember
from app.schemas.group_schema import GroupCreate, GroupOut

class GroupService:
    def __init__(self, repo: GroupRepository):
        self.repo = repo

    def create_group(self, db: Session, payload: GroupCreate) -> Group:
        group = Group(name=payload.name, description=payload.description)
        return self.repo.create(db, group)

    def add_member(self, db: Session, group_id: int, user_id: int, role: str = "member") -> GroupMember:
        gm = GroupMember(group_id=group_id, user_id=user_id, role=role)
        return self.repo.add_member(db, gm)
