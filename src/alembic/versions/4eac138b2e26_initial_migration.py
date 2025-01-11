"""Initial migration

Revision ID: 4eac138b2e26
Revises: 
Create Date: 2025-01-05 19:52:14.809719

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4eac138b2e26'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # Organizations table
    op.create_table(
        'organizations',
        sa.Column('id', sa.UUID(), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('name', sa.String, nullable=False),
        sa.Column('created_at', sa.DateTime, server_default=sa.text('NOW()'), nullable=False)
    )

    # Users table
    op.create_table(
        'users',
        sa.Column('id', sa.UUID(), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('organization_id', sa.UUID(), sa.ForeignKey('organizations.id', ondelete='CASCADE')),
        sa.Column('name', sa.String, nullable=False),
        sa.Column('email', sa.String, unique=True, nullable=False),
        sa.Column('hashed_password', sa.Text, nullable=False),
        sa.Column('email_verified', sa.Boolean, server_default='false', nullable=False),
        sa.Column('created_at', sa.DateTime, server_default=sa.text('NOW()'), nullable=False),
        sa.Column('deleted_at', sa.DateTime, nullable=True)
    )

    # Roles table
    op.create_table(
        'roles',
        sa.Column('id', sa.UUID(), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('name', sa.String, nullable=False),
        sa.Column('description', sa.Text, nullable=True)
    )

    # User roles mapping table
    op.create_table(
        'user_roles',
        sa.Column('user_id', sa.UUID(), sa.ForeignKey('users.id', ondelete='CASCADE'), primary_key=True),
        sa.Column('role_id', sa.UUID(), sa.ForeignKey('roles.id', ondelete='CASCADE'), primary_key=True)
    )

    # Applications table
    op.create_table(
        'applications',
        sa.Column('id', sa.UUID(), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('name', sa.String, nullable=False),
        # sa.Column('client_id', sa.UUID(), server_default=sa.text('gen_random_uuid()'), unique=True, nullable=False),
        sa.Column('client_secret', sa.Text, nullable=False),
        sa.Column('is_first_party', sa.Boolean, nullable=False),
        sa.Column('created_by', sa.UUID(), sa.ForeignKey('users.id')),
        sa.Column('created_at', sa.DateTime, server_default=sa.text('NOW()'), nullable=False)
    )

    # Application redirect URIs table
    op.create_table(
        'application_redirect_uris',
        sa.Column('application_id', sa.UUID(), sa.ForeignKey('applications.id', ondelete='CASCADE'), primary_key=True),
        sa.Column('redirect_uri', sa.String, primary_key=True)
    )

    # Application auth flows table
    op.create_table(
        'application_auth_flows',
        sa.Column('application_id', sa.UUID(), sa.ForeignKey('applications.id', ondelete='CASCADE'), primary_key=True),
        sa.Column('auth_flow', sa.String, primary_key=True)
    )

    # Resources table
    op.create_table(
        'resources',
        sa.Column('id', sa.UUID(), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('name', sa.String, nullable=False),
        sa.Column('description', sa.Text, nullable=True),
        sa.Column('created_at', sa.DateTime, server_default=sa.text('NOW()'), nullable=False)
    )

    # Scopes table
    op.create_table(
        'scopes',
        sa.Column('id', sa.UUID(), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('resource_id', sa.UUID(), sa.ForeignKey('resources.id', ondelete='CASCADE')),
        sa.Column('name', sa.String, nullable=False),
        sa.Column('description', sa.Text, nullable=True),
        sa.UniqueConstraint('resource_id', 'name', name='unique_scope_per_resource')
    )

    # Role-scope mappings table
    op.create_table(
        'role_scope_mappings',
        sa.Column('role_id', sa.UUID(), sa.ForeignKey('roles.id', ondelete='CASCADE'), primary_key=True),
        sa.Column('scope_id', sa.UUID(), sa.ForeignKey('scopes.id', ondelete='CASCADE'), primary_key=True)
    )

    # Authorization codes table
    op.create_table(
        'authorization_codes',
        sa.Column('code', sa.String, primary_key=True),
        sa.Column('application_id', sa.UUID(), sa.ForeignKey('applications.id', ondelete='CASCADE')),
        sa.Column('user_id', sa.UUID(), sa.ForeignKey('users.id')),
        sa.Column('expires_at', sa.DateTime, nullable=False),
        sa.Column('created_at', sa.DateTime, server_default=sa.text('NOW()'), nullable=False)
    )

    # Refresh tokens table
    op.create_table(
        'refresh_tokens',
        sa.Column('token', sa.String, primary_key=True),
        sa.Column('application_id', sa.UUID(), sa.ForeignKey('applications.id', ondelete='CASCADE')),
        sa.Column('user_id', sa.UUID(), sa.ForeignKey('users.id')),
        sa.Column('scope', sa.Text, nullable=False),
        sa.Column('expires_at', sa.DateTime, nullable=False),
        sa.Column('created_at', sa.DateTime, server_default=sa.text('NOW()'), nullable=False)
    )

    # Password reset tokens table
    op.create_table(
        'password_reset_tokens',
        sa.Column('token', sa.String, primary_key=True),
        sa.Column('user_id', sa.UUID(), sa.ForeignKey('users.id', ondelete='CASCADE')),
        sa.Column('expires_at', sa.DateTime, nullable=False),
        sa.Column('created_at', sa.DateTime, server_default=sa.text('NOW()'), nullable=False)
    )

    # Verify email tokens table
    op.create_table(
        'verify_email_tokens',
        sa.Column('token', sa.String, primary_key=True),
        sa.Column('user_id', sa.UUID(), sa.ForeignKey('users.id', ondelete='CASCADE'), primary_key=True),
        sa.Column('expires_at', sa.DateTime, nullable=False),
        sa.Column('created_at', sa.DateTime, server_default=sa.text('NOW()'), nullable=False)
    )


def downgrade():
    op.drop_table('verify_email_tokens')
    op.drop_table('password_reset_tokens')
    op.drop_table('refresh_tokens')
    op.drop_table('authorization_codes')
    op.drop_table('role_scope_mappings')
    op.drop_table('scopes')
    op.drop_table('resources')
    op.drop_table('application_auth_flows')
    op.drop_table('application_redirect_uris')
    op.drop_table('applications')
    op.drop_table('user_roles')
    op.drop_table('roles')
    op.drop_table('users')
    op.drop_table('organizations')
