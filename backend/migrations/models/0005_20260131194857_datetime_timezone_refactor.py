from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        -- ClubMember role 타입 변경
        ALTER TABLE "club_members" ALTER COLUMN "role" TYPE VARCHAR(7) USING "role"::VARCHAR(7);

        -- Sessions: 새 datetime 컬럼 추가 (nullable로 먼저)
        ALTER TABLE "sessions" ADD "end_datetime" TIMESTAMPTZ;
        ALTER TABLE "sessions" ADD "start_datetime" TIMESTAMPTZ;

        -- Sessions: 기존 date + time 데이터를 datetime으로 변환 (KST → UTC 변환: -9시간)
        UPDATE "sessions"
        SET start_datetime = (date + start_time::time) AT TIME ZONE 'Asia/Seoul' AT TIME ZONE 'UTC',
            end_datetime = (date + end_time::time) AT TIME ZONE 'Asia/Seoul' AT TIME ZONE 'UTC';

        -- Sessions: NOT NULL 제약조건 추가
        ALTER TABLE "sessions" ALTER COLUMN "start_datetime" SET NOT NULL;
        ALTER TABLE "sessions" ALTER COLUMN "end_datetime" SET NOT NULL;

        -- Sessions: 기존 컬럼 삭제
        ALTER TABLE "sessions" DROP COLUMN "end_time";
        ALTER TABLE "sessions" DROP COLUMN "date";
        ALTER TABLE "sessions" DROP COLUMN "start_time";

        -- Matches: 새 datetime 컬럼 추가 (nullable로 먼저)
        ALTER TABLE "matches" ADD "scheduled_datetime" TIMESTAMPTZ;

        -- Matches: 기존 scheduled_time을 datetime으로 변환
        -- 세션의 date를 기준으로 scheduled_time을 datetime으로 변환
        UPDATE "matches" m
        SET scheduled_datetime = (
            SELECT (s.start_datetime::date + m.scheduled_time::time) AT TIME ZONE 'Asia/Seoul' AT TIME ZONE 'UTC'
            FROM "sessions" s WHERE s.id = m.session_id
        );

        -- Matches: NULL인 경우 현재 시간으로 설정
        UPDATE "matches" SET scheduled_datetime = NOW() WHERE scheduled_datetime IS NULL;

        -- Matches: NOT NULL 제약조건 추가
        ALTER TABLE "matches" ALTER COLUMN "scheduled_datetime" SET NOT NULL;

        -- Matches: 기존 컬럼 삭제
        ALTER TABLE "matches" DROP COLUMN "scheduled_time";

        -- Match match_type 타입 변경
        ALTER TABLE "matches" ALTER COLUMN "match_type" TYPE VARCHAR(14) USING "match_type"::VARCHAR(14);"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        -- Matches: 복원
        ALTER TABLE "matches" ADD "scheduled_time" TIMETZ;
        UPDATE "matches" SET scheduled_time = (scheduled_datetime AT TIME ZONE 'Asia/Seoul')::time;
        ALTER TABLE "matches" ALTER COLUMN "scheduled_time" SET NOT NULL;
        ALTER TABLE "matches" DROP COLUMN "scheduled_datetime";
        ALTER TABLE "matches" ALTER COLUMN "match_type" TYPE VARCHAR(13) USING "match_type"::VARCHAR(13);

        -- Sessions: 복원
        ALTER TABLE "sessions" ADD "end_time" TIMETZ;
        ALTER TABLE "sessions" ADD "date" DATE;
        ALTER TABLE "sessions" ADD "start_time" TIMETZ;
        UPDATE "sessions"
        SET date = (start_datetime AT TIME ZONE 'Asia/Seoul')::date,
            start_time = (start_datetime AT TIME ZONE 'Asia/Seoul')::time,
            end_time = (end_datetime AT TIME ZONE 'Asia/Seoul')::time;
        ALTER TABLE "sessions" ALTER COLUMN "date" SET NOT NULL;
        ALTER TABLE "sessions" ALTER COLUMN "start_time" SET NOT NULL;
        ALTER TABLE "sessions" ALTER COLUMN "end_time" SET NOT NULL;
        ALTER TABLE "sessions" DROP COLUMN "end_datetime";
        ALTER TABLE "sessions" DROP COLUMN "start_datetime";

        -- ClubMember: 복원
        ALTER TABLE "club_members" ALTER COLUMN "role" TYPE VARCHAR(7) USING "role"::VARCHAR(7);"""
