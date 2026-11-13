-- Справочный экспорт фактической схемы SQLite. Рабочую БД создавайте через manage.py migrate, не импортом этого файла.
-- table auth_group: определение получено из sqlite_master; подробности полей объяснены в models.py и миграции.
CREATE TABLE "auth_group" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "name" varchar(150) NOT NULL UNIQUE); -- Создаёт указанную таблицу или индекс точно по текущей схеме.
-- table auth_group_permissions: определение получено из sqlite_master; подробности полей объяснены в models.py и миграции.
CREATE TABLE "auth_group_permissions" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "group_id" integer NOT NULL REFERENCES "auth_group" ("id") DEFERRABLE INITIALLY DEFERRED, "permission_id" integer NOT NULL REFERENCES "auth_permission" ("id") DEFERRABLE INITIALLY DEFERRED); -- Создаёт указанную таблицу или индекс точно по текущей схеме.
-- table auth_permission: определение получено из sqlite_master; подробности полей объяснены в models.py и миграции.
CREATE TABLE "auth_permission" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "content_type_id" integer NOT NULL REFERENCES "django_content_type" ("id") DEFERRABLE INITIALLY DEFERRED, "codename" varchar(100) NOT NULL, "name" varchar(255) NOT NULL); -- Создаёт указанную таблицу или индекс точно по текущей схеме.
-- table django_content_type: определение получено из sqlite_master; подробности полей объяснены в models.py и миграции.
CREATE TABLE "django_content_type" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "app_label" varchar(100) NOT NULL, "model" varchar(100) NOT NULL); -- Создаёт указанную таблицу или индекс точно по текущей схеме.
-- table django_migrations: определение получено из sqlite_master; подробности полей объяснены в models.py и миграции.
CREATE TABLE "django_migrations" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "app" varchar(255) NOT NULL, "name" varchar(255) NOT NULL, "applied" datetime NOT NULL); -- Создаёт указанную таблицу или индекс точно по текущей схеме.
-- table django_session: определение получено из sqlite_master; подробности полей объяснены в models.py и миграции.
CREATE TABLE "django_session" ("session_key" varchar(40) NOT NULL PRIMARY KEY, "session_data" text NOT NULL, "expire_date" datetime NOT NULL); -- Создаёт указанную таблицу или индекс точно по текущей схеме.
-- table portal_application: определение получено из sqlite_master; подробности полей объяснены в models.py и миграции.
CREATE TABLE "portal_application" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "start_date" date NOT NULL, "payment_method" varchar(20) NOT NULL, "status" varchar(20) NOT NULL, "review_text" text NOT NULL, "created_at" datetime NOT NULL, "user_id" bigint NOT NULL REFERENCES "portal_user" ("id") DEFERRABLE INITIALLY DEFERRED, "course_id" bigint NOT NULL REFERENCES "portal_course" ("id") DEFERRABLE INITIALLY DEFERRED, CONSTRAINT "valid_status" CHECK ("status" IN ('new', 'studying', 'completed')), CONSTRAINT "valid_payment" CHECK ("payment_method" IN ('cash', 'phone_transfer')), CONSTRAINT "review_after_completion" CHECK (("review_text" = '' OR "status" = 'completed'))); -- Создаёт указанную таблицу или индекс точно по текущей схеме.
-- table portal_course: определение получено из sqlite_master; подробности полей объяснены в models.py и миграции.
CREATE TABLE "portal_course" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "title" varchar(200) NOT NULL UNIQUE, "is_active" bool NOT NULL); -- Создаёт указанную таблицу или индекс точно по текущей схеме.
-- table portal_user: определение получено из sqlite_master; подробности полей объяснены в models.py и миграции.
CREATE TABLE "portal_user" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "password" varchar(128) NOT NULL, "last_login" datetime NULL, "is_superuser" bool NOT NULL, "first_name" varchar(150) NOT NULL, "last_name" varchar(150) NOT NULL, "is_staff" bool NOT NULL, "is_active" bool NOT NULL, "date_joined" datetime NOT NULL, "username" varchar(50) NOT NULL UNIQUE, "full_name" varchar(150) NOT NULL, "phone" varchar(16) NOT NULL, "email" varchar(120) NOT NULL); -- Создаёт указанную таблицу или индекс точно по текущей схеме.
-- table portal_user_groups: определение получено из sqlite_master; подробности полей объяснены в models.py и миграции.
CREATE TABLE "portal_user_groups" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "user_id" bigint NOT NULL REFERENCES "portal_user" ("id") DEFERRABLE INITIALLY DEFERRED, "group_id" integer NOT NULL REFERENCES "auth_group" ("id") DEFERRABLE INITIALLY DEFERRED); -- Создаёт указанную таблицу или индекс точно по текущей схеме.
-- table portal_user_user_permissions: определение получено из sqlite_master; подробности полей объяснены в models.py и миграции.
CREATE TABLE "portal_user_user_permissions" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "user_id" bigint NOT NULL REFERENCES "portal_user" ("id") DEFERRABLE INITIALLY DEFERRED, "permission_id" integer NOT NULL REFERENCES "auth_permission" ("id") DEFERRABLE INITIALLY DEFERRED); -- Создаёт указанную таблицу или индекс точно по текущей схеме.
-- index app_status: определение получено из sqlite_master; подробности полей объяснены в models.py и миграции.
CREATE INDEX "app_status" ON "portal_application" ("status"); -- Создаёт указанную таблицу или индекс точно по текущей схеме.
-- index app_user_created: определение получено из sqlite_master; подробности полей объяснены в models.py и миграции.
CREATE INDEX "app_user_created" ON "portal_application" ("user_id", "created_at" DESC); -- Создаёт указанную таблицу или индекс точно по текущей схеме.
-- index auth_group_permissions_group_id_b120cbf9: определение получено из sqlite_master; подробности полей объяснены в models.py и миграции.
CREATE INDEX "auth_group_permissions_group_id_b120cbf9" ON "auth_group_permissions" ("group_id"); -- Создаёт указанную таблицу или индекс точно по текущей схеме.
-- index auth_group_permissions_group_id_permission_id_0cd325b0_uniq: определение получено из sqlite_master; подробности полей объяснены в models.py и миграции.
CREATE UNIQUE INDEX "auth_group_permissions_group_id_permission_id_0cd325b0_uniq" ON "auth_group_permissions" ("group_id", "permission_id"); -- Создаёт указанную таблицу или индекс точно по текущей схеме.
-- index auth_group_permissions_permission_id_84c5c92e: определение получено из sqlite_master; подробности полей объяснены в models.py и миграции.
CREATE INDEX "auth_group_permissions_permission_id_84c5c92e" ON "auth_group_permissions" ("permission_id"); -- Создаёт указанную таблицу или индекс точно по текущей схеме.
-- index auth_permission_content_type_id_2f476e4b: определение получено из sqlite_master; подробности полей объяснены в models.py и миграции.
CREATE INDEX "auth_permission_content_type_id_2f476e4b" ON "auth_permission" ("content_type_id"); -- Создаёт указанную таблицу или индекс точно по текущей схеме.
-- index auth_permission_content_type_id_codename_01ab375a_uniq: определение получено из sqlite_master; подробности полей объяснены в models.py и миграции.
CREATE UNIQUE INDEX "auth_permission_content_type_id_codename_01ab375a_uniq" ON "auth_permission" ("content_type_id", "codename"); -- Создаёт указанную таблицу или индекс точно по текущей схеме.
-- index django_content_type_app_label_model_76bd3d3b_uniq: определение получено из sqlite_master; подробности полей объяснены в models.py и миграции.
CREATE UNIQUE INDEX "django_content_type_app_label_model_76bd3d3b_uniq" ON "django_content_type" ("app_label", "model"); -- Создаёт указанную таблицу или индекс точно по текущей схеме.
-- index django_session_expire_date_a5c62663: определение получено из sqlite_master; подробности полей объяснены в models.py и миграции.
CREATE INDEX "django_session_expire_date_a5c62663" ON "django_session" ("expire_date"); -- Создаёт указанную таблицу или индекс точно по текущей схеме.
-- index portal_application_course_id_90b2c203: определение получено из sqlite_master; подробности полей объяснены в models.py и миграции.
CREATE INDEX "portal_application_course_id_90b2c203" ON "portal_application" ("course_id"); -- Создаёт указанную таблицу или индекс точно по текущей схеме.
-- index portal_application_user_id_f805ec8c: определение получено из sqlite_master; подробности полей объяснены в models.py и миграции.
CREATE INDEX "portal_application_user_id_f805ec8c" ON "portal_application" ("user_id"); -- Создаёт указанную таблицу или индекс точно по текущей схеме.
-- index portal_user_groups_group_id_39d85d73: определение получено из sqlite_master; подробности полей объяснены в models.py и миграции.
CREATE INDEX "portal_user_groups_group_id_39d85d73" ON "portal_user_groups" ("group_id"); -- Создаёт указанную таблицу или индекс точно по текущей схеме.
-- index portal_user_groups_user_id_120e8705: определение получено из sqlite_master; подробности полей объяснены в models.py и миграции.
CREATE INDEX "portal_user_groups_user_id_120e8705" ON "portal_user_groups" ("user_id"); -- Создаёт указанную таблицу или индекс точно по текущей схеме.
-- index portal_user_groups_user_id_group_id_bad90d85_uniq: определение получено из sqlite_master; подробности полей объяснены в models.py и миграции.
CREATE UNIQUE INDEX "portal_user_groups_user_id_group_id_bad90d85_uniq" ON "portal_user_groups" ("user_id", "group_id"); -- Создаёт указанную таблицу или индекс точно по текущей схеме.
-- index portal_user_user_permissions_permission_id_f211252b: определение получено из sqlite_master; подробности полей объяснены в models.py и миграции.
CREATE INDEX "portal_user_user_permissions_permission_id_f211252b" ON "portal_user_user_permissions" ("permission_id"); -- Создаёт указанную таблицу или индекс точно по текущей схеме.
-- index portal_user_user_permissions_user_id_fe5a2108: определение получено из sqlite_master; подробности полей объяснены в models.py и миграции.
CREATE INDEX "portal_user_user_permissions_user_id_fe5a2108" ON "portal_user_user_permissions" ("user_id"); -- Создаёт указанную таблицу или индекс точно по текущей схеме.
-- index portal_user_user_permissions_user_id_permission_id_55ccefbe_uniq: определение получено из sqlite_master; подробности полей объяснены в models.py и миграции.
CREATE UNIQUE INDEX "portal_user_user_permissions_user_id_permission_id_55ccefbe_uniq" ON "portal_user_user_permissions" ("user_id", "permission_id"); -- Создаёт указанную таблицу или индекс точно по текущей схеме.
-- index unique_login_casefold: определение получено из sqlite_master; подробности полей объяснены в models.py и миграции.
CREATE UNIQUE INDEX "unique_login_casefold" ON "portal_user" ((LOWER("username"))); -- Создаёт указанную таблицу или индекс точно по текущей схеме.
