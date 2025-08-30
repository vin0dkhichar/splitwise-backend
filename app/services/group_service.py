from sqlalchemy.orm import Session
from app.repositories.group_repository import GroupRepository
from app.models.group import Group
from app.models.user import User
from app.models.group_member import GroupMember
from app.schemas.group_schema import GroupCreate
from typing import List, Optional


class GroupService:
    def __init__(self, repo: GroupRepository):
        self.repo = repo

    def create_group(
        self, db: Session, payload: GroupCreate, current_user: User
    ) -> Group:
        group = Group(
            name=payload.name,
            description=payload.description,
            creator_id=current_user.id,
        )
        group = self.repo.create(db, group)

        gm = GroupMember(group_id=group.id, user_id=current_user.id, role="admin")
        self.repo.add_member(db, gm)

        return group

    def get_group_by_id(self, db: Session, group_id: int) -> Optional[Group]:
        return self.repo.get_by_id(db, group_id)

    def get_all_groups(
        self, db: Session, skip: int = 0, limit: int = 100
    ) -> List[Group]:
        return self.repo.list(db, skip=skip, limit=limit)

    def get_groups_for_user(self, db: Session, user_id: int) -> List[Group]:
        all_groups = self.repo.list(db)
        return [g for g in all_groups if self.repo.is_user_in_group(db, g.id, user_id)]

    def update_group(
        self, db: Session, group_id: int, payload: GroupCreate
    ) -> Optional[Group]:
        return self.repo.update(
            db, group_id, name=payload.name, description=payload.description
        )

    def delete_group(self, db: Session, group_id: int) -> bool:
        return self.repo.delete(db, group_id)

    def add_member(
        self,
        db: Session,
        group_id: int,
        user_id: int,
        added_by: int,
        role: str = "member",
    ) -> GroupMember:
        if not self.repo.is_user_in_group(db, group_id, added_by):
            raise PermissionError("You must be a member of the group to add others.")

        if self.repo.get_member(db, group_id, user_id):
            raise ValueError("User already a member of this group")

        gm = GroupMember(group_id=group_id, user_id=user_id, role=role)
        return self.repo.add_member(db, gm)

    def get_all_members(self, db: Session, group_id: int) -> List[GroupMember]:
        return self.repo.get_members(db, group_id)

    def remove_member(self, db: Session, group_id: int, user_id: int) -> bool:
        return self.repo.remove_member_by_ids(db, group_id, user_id)
