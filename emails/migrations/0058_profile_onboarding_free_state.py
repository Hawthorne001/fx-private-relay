# Generated by Django 3.2.19 on 2023-10-19 23:46

from django.db import migrations, models


def add_db_default_forward_func(apps, schema_editor):
    """
    Add a database default of false for sent_welcome_email, for PostgreSQL and SQLite3
    Note: set sent_welcome_email = true for existing users

    Using `./manage.py sqlmigrate` for the SQL, and the technique from:
    https://stackoverflow.com/a/45232678/10612
    """
    if schema_editor.connection.vendor.startswith("postgres"):
        schema_editor.execute(
            'ALTER TABLE "emails_profile"'
            ' ALTER COLUMN "onboarding_free_state" SET DEFAULT 0;'
        )
        # Set all existing profiles to 0 so existing users also see the free onboarding
        schema_editor.execute(
            'UPDATE "emails_profile"' ' SET "onboarding_free_state" = 0;'
        )
    elif schema_editor.connection.vendor.startswith("sqlite"):
        schema_editor.execute(
            """
            CREATE TABLE "new__emails_profile" (
                "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, 
                "onboarding_free_state" integer unsigned NOT NULL CHECK ("onboarding_free_state" >= 0) DEFAULT 0, 
                "api_token" char(32) NOT NULL, 
                "user_id" integer NOT NULL UNIQUE REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED, 
                "address_last_deleted" datetime NULL, 
                "num_address_deleted" integer unsigned NOT NULL CHECK ("num_address_deleted" >= 0), 
                "last_hard_bounce" datetime NULL, 
                "last_soft_bounce" datetime NULL, 
                "subdomain" varchar(63) NULL UNIQUE, 
                "server_storage" bool NOT NULL, 
                "num_email_blocked_in_deleted_address" integer unsigned NOT NULL CHECK (
                    "num_email_blocked_in_deleted_address" >= 0
                ), 
                "num_email_forwarded_in_deleted_address" integer unsigned NOT NULL CHECK (
                    "num_email_forwarded_in_deleted_address" >= 0
                ), 
                "num_email_spam_in_deleted_address" integer unsigned NOT NULL CHECK (
                    "num_email_spam_in_deleted_address" >= 0
                ), 
                "onboarding_state" integer unsigned NOT NULL CHECK ("onboarding_state" >= 0), 
                "last_account_flagged" datetime NULL, 
                "date_subscribed" datetime NULL, 
                "auto_block_spam" bool NOT NULL, 
                "num_email_replied_in_deleted_address" integer unsigned NOT NULL CHECK (
                    "num_email_replied_in_deleted_address" >= 0
                ), 
                "remove_level_one_email_trackers" bool NULL, 
                "num_level_one_trackers_blocked_in_deleted_address" integer unsigned NULL CHECK (
                    "num_level_one_trackers_blocked_in_deleted_address" >= 0
                ), 
                "store_phone_log" bool NOT NULL, 
                "date_phone_subscription_checked" datetime NULL, 
                "date_subscribed_phone" datetime NULL, 
                "forwarded_first_reply" bool NOT NULL, 
                "date_phone_subscription_end" datetime NULL, 
                "date_phone_subscription_reset" datetime NULL, 
                "date_phone_subscription_start" datetime NULL, 
                "created_by" varchar(63) NULL, 
                "sent_welcome_email" bool NOT NULL
            );
        """
        )
        schema_editor.execute(
            """
            INSERT INTO "new__emails_profile" (
                "id", "api_token", "user_id", "address_last_deleted", 
                "num_address_deleted", "last_hard_bounce", 
                "last_soft_bounce", "subdomain", 
                "server_storage", "num_email_blocked_in_deleted_address", 
                "num_email_forwarded_in_deleted_address", 
                "num_email_spam_in_deleted_address", 
                "onboarding_state", "last_account_flagged", 
                "date_subscribed", "auto_block_spam", 
                "num_email_replied_in_deleted_address", 
                "remove_level_one_email_trackers", 
                "num_level_one_trackers_blocked_in_deleted_address", 
                "store_phone_log", "date_phone_subscription_checked", 
                "date_subscribed_phone", "forwarded_first_reply", 
                "date_phone_subscription_end", 
                "date_phone_subscription_reset", 
                "date_phone_subscription_start", 
                "created_by", "sent_welcome_email", 
                "onboarding_free_state"
                ) 
            SELECT 
                "id", 
                "api_token", 
                "user_id", 
                "address_last_deleted", 
                "num_address_deleted", 
                "last_hard_bounce", 
                "last_soft_bounce", 
                "subdomain", 
                "server_storage", 
                "num_email_blocked_in_deleted_address", 
                "num_email_forwarded_in_deleted_address", 
                "num_email_spam_in_deleted_address", 
                "onboarding_state", 
                "last_account_flagged", 
                "date_subscribed", 
                "auto_block_spam", 
                "num_email_replied_in_deleted_address", 
                "remove_level_one_email_trackers", 
                "num_level_one_trackers_blocked_in_deleted_address", 
                "store_phone_log", 
                "date_phone_subscription_checked", 
                "date_subscribed_phone", 
                "forwarded_first_reply", 
                "date_phone_subscription_end", 
                "date_phone_subscription_reset", 
                "date_phone_subscription_start", 
                "created_by", 
                "sent_welcome_email", 
                0 
            FROM 
                "emails_profile";
            """
        )
        schema_editor.execute('DROP TABLE "emails_profile";')
        schema_editor.execute(
            'ALTER TABLE "new__emails_profile" RENAME TO "emails_profile";'
        )
        schema_editor.execute(
            'CREATE INDEX "emails_profile_address_last_deleted_188d9e79" ON "emails_profile" ("address_last_deleted");'
        )
        schema_editor.execute(
            'CREATE INDEX "emails_profile_last_hard_bounce_fefe494f" ON "emails_profile" ("last_hard_bounce");'
        )
        schema_editor.execute(
            'CREATE INDEX "emails_profile_last_soft_bounce_642ab37d" ON "emails_profile" ("last_soft_bounce");'
        )
        schema_editor.execute(
            'CREATE INDEX "emails_profile_last_account_flagged_f40cbf85" ON "emails_profile" ("last_account_flagged");'
        )
    else:
        raise Exception(f'Unknown database vendor "{schema_editor.connection.vendor}"')


class Migration(migrations.Migration):
    dependencies = [
        ("emails", "0057_profile_sent_welcome_email"),
    ]

    operations = [
        migrations.AddField(
            model_name="profile",
            name="onboarding_free_state",
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.RunPython(
            code=add_db_default_forward_func,
            reverse_code=migrations.RunPython.noop,
            elidable=True,
        ),
    ]