"""Add new waitingApproval/private columns for Posts

Revision ID: 3654bde20c06
Revises: 
Create Date: 2024-05-03 17:19:32.998299

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3654bde20c06'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('posts', schema=None) as batch_op:
        batch_op.add_column(sa.Column('waitingApproval', sa.Boolean(), nullable=False, server_default=sa.false()))
        batch_op.add_column(sa.Column('private', sa.Boolean(), nullable=False, server_default=sa.false()))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('posts', schema=None) as batch_op:
        batch_op.drop_column('private')
        batch_op.drop_column('waitingApproval')

    # ### end Alembic commands ###
