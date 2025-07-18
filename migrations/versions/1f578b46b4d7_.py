"""empty message

Revision ID: 1f578b46b4d7
Revises: 850733cb7a00
Create Date: 2025-06-05 23:31:40.504150

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1f578b46b4d7'
down_revision = '850733cb7a00'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('category', schema=None) as batch_op:
        batch_op.drop_index('category_code')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('category', schema=None) as batch_op:
        batch_op.create_index('category_code', ['category_code'], unique=False)

    # ### end Alembic commands ###
