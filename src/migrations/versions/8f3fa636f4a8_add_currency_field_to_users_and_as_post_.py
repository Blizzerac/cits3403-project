"""Add currency field to users and as post reward

Revision ID: 8f3fa636f4a8
Revises: 8286a93082d2
Create Date: 2024-05-06 18:57:50.428910

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8f3fa636f4a8'
down_revision = '8286a93082d2'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('posts', schema=None) as batch_op:
        batch_op.add_column(sa.Column('reward', sa.BigInteger(), nullable=False, server_default='0'))

    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.add_column(sa.Column('gold', sa.BigInteger(), nullable=False, server_default='0'))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.drop_column('gold')

    with op.batch_alter_table('posts', schema=None) as batch_op:
        batch_op.drop_column('reward')

    # ### end Alembic commands ###
