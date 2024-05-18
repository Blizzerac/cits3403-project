"""Add admin boolean for Users table

Revision ID: f57ce4f33f37
Revises: 2f8edd438f0d
Create Date: 2024-05-18 22:42:13.498981

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f57ce4f33f37'
down_revision = '2f8edd438f0d'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.add_column(sa.Column('isAdmin', sa.Boolean(), nullable=False, server_default=sa.false()))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.drop_column('isAdmin')

    # ### end Alembic commands ###