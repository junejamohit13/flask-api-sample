from sqlalchemy import Column, String, JSON
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class UserCache(Base):
    __tablename__ = 'user_cache'
    __table_args__ = {'schema': 'development'}

    user_name = Column(String(255), primary_key=True)
    table_name = Column(String(255), primary_key=True)
    primary_key = Column(String(255), primary_key=True)
    data = Column(JSON)
    comments = Column(JSON)

    def __repr__(self):
        return f"<UserCache(user_name='{self.user_name}', table_name='{self.table_name}', primary_key='{self.primary_key}', data={self.data}, comments={self.comments})>"

    @classmethod
    def get_user_tables_data(cls, session, username: str):
        """
        Get all cache records for a given username.
        
        Args:
            session: SQLAlchemy session
            username (str): Username to filter by
            
        Returns:
            list[UserCache]: List of matching cache records
        """
        result = session.query(cls).filter(
            cls.user_name == username
        ).all()
        
        return result

    @classmethod
    def update_data(cls, session, username: str, table_name: str, primary_key: str, column_name: str, value: any):
        """
        Upsert data for a specific column in the cache.
        
        Args:
            session: SQLAlchemy session
            username (str): Username
            table_name (str): Name of the table
            primary_key (str): Primary key value
            column_name (str): Column to update
            value: Value to set for the column
        """
        # Try to get existing record
        record = session.query(cls).filter_by(
            user_name=username,
            table_name=table_name,
            primary_key=primary_key
        ).first()

        if record:
            # Update existing record
            if record.data is None:
                record.data = {}
            # Create a new dictionary with existing data
            new_data = dict(record.data)
            # Update the specific column
            new_data[column_name] = value
            # Assign the updated dictionary back to record.data
            record.data = new_data
        else:
            # Create new record
            record = cls(
                user_name=username,
                table_name=table_name,
                primary_key=primary_key,
                data={column_name: value},
                comments={}
            )
            session.add(record)
        
        session.commit()
        return record

    @classmethod
    def update_comment(cls, session, username: str, table_name: str, primary_key: str, 
                      column_name: str, question: str, answer: str):
        """
        Upsert a comment for a specific column in the cache.
        """
        print(f"Updating comment with: username={username}, table={table_name}, key={primary_key}")
        print(f"Column: {column_name}, Question: {question}, Answer: {answer}")
        
        try:
            record = session.query(cls).filter_by(
                user_name=username,
                table_name=table_name,
                primary_key=primary_key
            ).first()

            if record:
                print(f"Record found: {record}")
                print(f"Current comments: {record.comments}")
                
                if record.comments is None:
                    record.comments = {}
                new_comments = dict(record.comments)
                
                # Initialize or reset column comments
                if column_name not in new_comments:
                    new_comments[column_name] = {}
                else:
                    # Keep only q1-q4 keys, remove old structure
                    old_comments = new_comments[column_name]
                    new_comments[column_name] = {
                        k: v for k, v in old_comments.items() 
                        if k in ['q1', 'q2', 'q3', 'q4']
                    }
                        
                # Store answer directly under the question key
                new_comments[column_name][question] = answer
                
                # Explicitly mark as modified
                record.comments = new_comments
                session.add(record)
                
                print(f"New comments structure: {new_comments}")
                print(f"Record before commit: {record}")
                
                session.flush()  # Flush changes to DB
                session.commit()  # Commit transaction
                
                # Verify the update
                session.refresh(record)
                print(f"Record after commit and refresh: {record}")
                
                return record
        except Exception as e:
            print(f"Error updating comment: {e}")
            session.rollback()
            raise

    

    import strawberry
from typing import List, Optional
from sqlalchemy.orm import Session
from fastapi import Depends
from models import UserCache
from database import get_session
from strawberry.types import Info
from typing import Any

# Input types for mutations
@strawberry.input
class DataInput:
    username: str
    table_name: str
    primary_key: str
    column_name: str
    value: str

@strawberry.input
class CommentInput:
    username: str
    table_name: str
    primary_key: str
    column_name: str
    question: str
    answer: str

# Types for responses
@strawberry.type
class CacheData:
    user_name: str
    table_name: str
    primary_key: str
    data: Optional[strawberry.scalars.JSON] = None
    comments: Optional[strawberry.scalars.JSON] = None

@strawberry.type
class Query:
    @strawberry.field
    def get_user_tables_data(
        self, 
        username: str,
        info: Info
    ) -> List[CacheData]:
        session = info.context["session"]
        records = UserCache.get_user_tables_data(
            session=session,
            username=username
        )
        return [
            CacheData(
                user_name=record.user_name,
                table_name=record.table_name,
                primary_key=record.primary_key,
                data=record.data,
                comments=record.comments
            ) for record in records
        ]

@strawberry.type
class Mutation:
    @strawberry.mutation
    def update_data(
        self, 
        input: DataInput,
        info: Info
    ) -> CacheData:

        session = info.context["session"]
        record = UserCache.update_data(
            session=session,
            username=input.username,
            table_name=input.table_name,
            primary_key=input.primary_key,
            column_name=input.column_name,
            value=input.value
        )

        return CacheData(
            user_name=record.user_name,
            table_name=record.table_name,
            primary_key=record.primary_key,
            data=record.data,
            comments=record.comments
        )

    @strawberry.mutation
    def update_comment(
        self, 
        input: CommentInput,
        info: Info
    ) -> CacheData:
        session = info.context["session"]
        print("update_comment called")
        print(input)
        record = UserCache.update_comment(
            session=session,
            username=input.username,
            table_name=input.table_name,
            primary_key=input.primary_key,
            column_name=input.column_name,
            question=input.question,
            answer=input.answer
        )
        return CacheData(
            user_name=record.user_name,
            table_name=record.table_name,
            primary_key=record.primary_key,
            data=record.data,
            comments=record.comments
        )

schema = strawberry.Schema(query=Query, mutation=Mutation) 

-- Create table in development schema
CREATE TABLE IF NOT EXISTS development.user_cache (
    user_name VARCHAR(255),
    table_name VARCHAR(255),
    primary_key VARCHAR(255),
    data JSONB,
    comments JSONB,
    PRIMARY KEY (user_name, table_name, primary_key)
);

-- Add comment to explain JSONB constraint for comments
COMMENT ON COLUMN development.user_cache.comments IS 'JSONB where values should be text type'; 
