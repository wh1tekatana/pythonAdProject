"""add type, category, price, and location to advertisement

Revision ID: ec6b78ddb33f
Revises: f5fd4c353f93
Create Date: 2024-05-02 17:31:14.762541

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ec6b78ddb33f'
down_revision: Union[str, None] = 'f5fd4c353f93'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.add_column('advertisements', sa.Column('type', sa.String(), nullable=True))
    op.add_column('advertisements', sa.Column('category', sa.String(), nullable=True))
    op.add_column('advertisements', sa.Column('price', sa.String(), nullable=True))
    op.add_column('advertisements', sa.Column('location', sa.String(), nullable=True))


def downgrade():
    op.drop_column('advertisements', 'location')
    op.drop_column('advertisements', 'price')
    op.drop_column('advertisements', 'category')
    op.drop_column('advertisements', 'type')