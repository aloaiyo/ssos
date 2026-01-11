from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "club_members" ALTER COLUMN "role" TYPE VARCHAR(7) USING "role"::VARCHAR(7);
        ALTER TABLE "club_members" ALTER COLUMN "status" TYPE VARCHAR(8) USING "status"::VARCHAR(8);
        ALTER TABLE "guests" ADD "created_by_id" INT;
        ALTER TABLE "guests" ADD "linked_member_id" INT;
        ALTER TABLE "guests" ADD CONSTRAINT "fk_guests_club_mem_2ab7cf12" FOREIGN KEY ("linked_member_id") REFERENCES "club_members" ("id") ON DELETE SET NULL;
        ALTER TABLE "guests" ADD CONSTRAINT "fk_guests_club_mem_f9d979a5" FOREIGN KEY ("created_by_id") REFERENCES "club_members" ("id") ON DELETE SET NULL;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "guests" DROP CONSTRAINT "fk_guests_club_mem_f9d979a5";
        ALTER TABLE "guests" DROP CONSTRAINT "fk_guests_club_mem_2ab7cf12";
        ALTER TABLE "guests" DROP COLUMN "created_by_id";
        ALTER TABLE "guests" DROP COLUMN "linked_member_id";
        ALTER TABLE "club_members" ALTER COLUMN "role" TYPE VARCHAR(7) USING "role"::VARCHAR(7);
        ALTER TABLE "club_members" ALTER COLUMN "status" TYPE VARCHAR(8) USING "status"::VARCHAR(8);"""
