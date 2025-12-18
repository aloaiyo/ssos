from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        -- Create guests table
        CREATE TABLE IF NOT EXISTS "guests" (
            "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
            "modified_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
            "is_deleted" BOOL NOT NULL DEFAULT False,
            "id" SERIAL NOT NULL PRIMARY KEY,
            "name" VARCHAR(100) NOT NULL,
            "gender" VARCHAR(6) NOT NULL,
            "phone" VARCHAR(20),
            "notes" TEXT,
            "total_games" INT NOT NULL DEFAULT 0,
            "wins" INT NOT NULL DEFAULT 0,
            "losses" INT NOT NULL DEFAULT 0,
            "draws" INT NOT NULL DEFAULT 0,
            "club_id" INT NOT NULL REFERENCES "clubs" ("id") ON DELETE CASCADE
        );
        COMMENT ON COLUMN "guests"."gender" IS 'MALE: male\nFEMALE: female';
        COMMENT ON TABLE "guests" IS '게스트 모델';

        -- Add columns to session_participants
        ALTER TABLE "session_participants" ADD COLUMN IF NOT EXISTS "guest_id" INT REFERENCES "guests" ("id") ON DELETE CASCADE;
        ALTER TABLE "session_participants" ADD COLUMN IF NOT EXISTS "user_id" INT REFERENCES "users" ("id") ON DELETE CASCADE;
        ALTER TABLE "session_participants" ADD COLUMN IF NOT EXISTS "participant_category" VARCHAR(9) NOT NULL DEFAULT 'member';
        ALTER TABLE "session_participants" ALTER COLUMN "club_member_id" DROP NOT NULL;

        -- Add columns to match_participants
        ALTER TABLE "match_participants" ADD COLUMN IF NOT EXISTS "guest_id" INT REFERENCES "guests" ("id") ON DELETE CASCADE;
        ALTER TABLE "match_participants" ADD COLUMN IF NOT EXISTS "user_id" INT REFERENCES "users" ("id") ON DELETE CASCADE;
        ALTER TABLE "match_participants" ADD COLUMN IF NOT EXISTS "participant_category" VARCHAR(9) NOT NULL DEFAULT 'member';
        ALTER TABLE "match_participants" ALTER COLUMN "club_member_id" DROP NOT NULL;
        """


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        -- Remove columns from match_participants
        ALTER TABLE "match_participants" DROP COLUMN IF EXISTS "participant_category";
        ALTER TABLE "match_participants" DROP COLUMN IF EXISTS "user_id";
        ALTER TABLE "match_participants" DROP COLUMN IF EXISTS "guest_id";

        -- Remove columns from session_participants
        ALTER TABLE "session_participants" DROP COLUMN IF EXISTS "participant_category";
        ALTER TABLE "session_participants" DROP COLUMN IF EXISTS "user_id";
        ALTER TABLE "session_participants" DROP COLUMN IF EXISTS "guest_id";

        -- Drop guests table
        DROP TABLE IF EXISTS "guests";
        """
