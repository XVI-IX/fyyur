"""empty message

Revision ID: 90e9200f2f3f
Revises: 1df61936205e
Create Date: 2022-05-28 15:17:23.246825

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '90e9200f2f3f'
down_revision = '1df61936205e'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('Artist', sa.Column('website_link', sa.String(length=500), nullable=True))
    # op.execute('UPDATE Artist SET website_link = no website WHERE website_link IS NULL')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('Artist', 'website_link')
    # ### end Alembic commands ###