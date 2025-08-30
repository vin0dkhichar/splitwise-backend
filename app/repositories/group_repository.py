from sqlalchemy.orm import Session
from app.models.group import Group
from app.models.group_member import GroupMember
from typing import List, Optional


class GroupRepository:
    def create(self, db: Session, group: Group) -> Group:
        db.add(group)
        db.commit()
        db.refresh(group)
        return group

    def get_by_id(self, db: Session, group_id: int) -> Optional[Group]:
        return db.query(Group).filter(Group.id == group_id).first()

    def list(self, db: Session, skip: int = 0, limit: int = 100) -> List[Group]:
        return db.query(Group).offset(skip).limit(limit).all()

    def update(
        self, db: Session, group_id: int, *, name: str, description: Optional[str]
    ) -> Optional[Group]:
        group = self.get_by_id(db, group_id)
        if not group:
            return None
        group.name = name
        group.description = description
        db.commit()
        db.refresh(group)
        return group

    def delete(self, db: Session, group_id: int) -> bool:
        group = self.get_by_id(db, group_id)
        if not group:
            return False
        db.delete(group)
        db.commit()
        return True

    def add_member(self, db: Session, group_member: GroupMember) -> GroupMember:
        db.add(group_member)
        db.commit()
        db.refresh(group_member)
        return group_member

    def get_members(self, db: Session, group_id: int) -> List[GroupMember]:
        return db.query(GroupMember).filter(GroupMember.group_id == group_id).all()

    def get_member(
        self, db: Session, group_id: int, user_id: int
    ) -> Optional[GroupMember]:
        return (
            db.query(GroupMember)
            .filter(GroupMember.group_id == group_id, GroupMember.user_id == user_id)
            .first()
        )

    def remove_member(self, db: Session, group_member: GroupMember):
        db.delete(group_member)
        db.commit()

    def remove_member_by_ids(self, db: Session, group_id: int, user_id: int) -> bool:
        gm = self.get_member(db, group_id, user_id)
        if not gm:
            return False
        self.remove_member(db, gm)
        return True

    def get_group(self, db: Session, group_id: int) -> Group | None:
        return db.query(Group).filter(Group.id == group_id).first()

    def is_user_in_group(self, db: Session, group_id: int, user_id: int) -> bool:
        group = self.get_group(db, group_id)
        if group and group.creator_id == user_id:
            return True

        return (
            db.query(GroupMember)
            .filter(GroupMember.group_id == group_id, GroupMember.user_id == user_id)
            .count()
            > 0
        )
