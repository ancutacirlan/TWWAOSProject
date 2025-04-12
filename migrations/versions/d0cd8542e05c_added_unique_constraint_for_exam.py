"""added unique constraint  for exam

Revision ID: d0cd8542e05c
Revises: 7f7f856fa77f
Create Date: 2025-04-10 14:36:34.120435

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd0cd8542e05c'
down_revision = '7f7f856fa77f'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('exams', schema=None) as batch_op:
        batch_op.create_unique_constraint('unique_exam_per_course_and_group', ['course_id', 'group_id'])

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('exams', schema=None) as batch_op:
        batch_op.drop_constraint('unique_exam_per_course_and_group', type_='unique')

    # ### end Alembic commands ###
