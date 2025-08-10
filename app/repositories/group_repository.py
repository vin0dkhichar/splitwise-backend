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

    def add_member(self, db: Session, group_member: GroupMember) -> GroupMember:
        db.add(group_member)
        db.commit()
        db.refresh(group_member)
        return group_member

    def remove_member(self, db: Session, group_member: GroupMember):
        db.delete(group_member)
        db.commit()
    
    def get_group(self, db: Session, group_id: int) -> Group | None:
        return db.query(Group).filter(Group.id == group_id).first()
    
    def is_user_in_group(self, db: Session, group_id: int, user_id: int) -> bool:
        return (
            db.query(GroupMember)
            .filter(GroupMember.group_id == group_id, GroupMember.user_id == user_id)
            .count() > 0
        )
