-- Справочная схема фактической таблицы portal_user; рабочую БД создаёт manage.py migrate.
CREATE TABLE "portal_user" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "password" varchar(128) NOT NULL, "last_login" datetime NULL, "is_superuser" bool NOT NULL, "first_name" varchar(150) NOT NULL, "last_name" varchar(150) NOT NULL, "is_staff" bool NOT NULL, "is_active" bool NOT NULL, "date_joined" datetime NOT NULL, "full_name" varchar(150) NOT NULL, "phone" varchar(16) NOT NULL, "email" varchar(254) NOT NULL, "username" varchar(150) NOT NULL UNIQUE); -- Создаёт эту таблицу.

-- Справочная схема фактической таблицы portal_course; рабочую БД создаёт manage.py migrate.
CREATE TABLE "portal_course" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "title" varchar(200) NOT NULL UNIQUE); -- Создаёт эту таблицу.

-- Справочная схема фактической таблицы portal_application; рабочую БД создаёт manage.py migrate.
CREATE TABLE "portal_application" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "start_date" date NOT NULL, "payment_method" varchar(20) NOT NULL, "review_text" text NOT NULL, "user_id" bigint NOT NULL REFERENCES "portal_user" ("id") DEFERRABLE INITIALLY DEFERRED, "course_id" bigint NOT NULL REFERENCES "portal_course" ("id") DEFERRABLE INITIALLY DEFERRED, "status" varchar(20) NOT NULL); -- Создаёт эту таблицу.

-- Индекс portal_application_user_id_f805ec8c ускоряет фильтр по статусу.
CREATE INDEX "portal_application_user_id_f805ec8c" ON "portal_application" ("user_id"); -- Создаёт индекс.

-- Индекс portal_application_course_id_90b2c203 ускоряет фильтр по статусу.
CREATE INDEX "portal_application_course_id_90b2c203" ON "portal_application" ("course_id"); -- Создаёт индекс.

-- Индекс portal_application_status_66459320 ускоряет фильтр по статусу.
CREATE INDEX "portal_application_status_66459320" ON "portal_application" ("status"); -- Создаёт индекс.
