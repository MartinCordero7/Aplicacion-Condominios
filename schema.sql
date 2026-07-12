


SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;




ALTER SCHEMA "public" OWNER TO "postgres";


CREATE EXTENSION IF NOT EXISTS "btree_gist" WITH SCHEMA "public";






CREATE EXTENSION IF NOT EXISTS "pg_stat_statements" WITH SCHEMA "extensions";






CREATE EXTENSION IF NOT EXISTS "pgcrypto" WITH SCHEMA "extensions";






CREATE EXTENSION IF NOT EXISTS "supabase_vault" WITH SCHEMA "vault";






CREATE EXTENSION IF NOT EXISTS "uuid-ossp" WITH SCHEMA "extensions";






CREATE TYPE "public"."accion_auditoria_enum" AS ENUM (
    'INSERT',
    'UPDATE',
    'DELETE'
);


ALTER TYPE "public"."accion_auditoria_enum" OWNER TO "postgres";


CREATE TYPE "public"."canal_notificacion_enum" AS ENUM (
    'EMAIL',
    'PUSH',
    'SMS',
    'WHATSAPP'
);


ALTER TYPE "public"."canal_notificacion_enum" OWNER TO "postgres";


CREATE TYPE "public"."destinatario_tipo_enum" AS ENUM (
    'TODOS',
    'TORRE',
    'UNIDAD',
    'ROL'
);


ALTER TYPE "public"."destinatario_tipo_enum" OWNER TO "postgres";


CREATE TYPE "public"."estado_asamblea_enum" AS ENUM (
    'PROGRAMADA',
    'EN_CURSO',
    'FINALIZADA',
    'CANCELADA'
);


ALTER TYPE "public"."estado_asamblea_enum" OWNER TO "postgres";


CREATE TYPE "public"."estado_convenio_enum" AS ENUM (
    'ACTIVO',
    'COMPLETADO',
    'INCUMPLIDO',
    'ANULADO'
);


ALTER TYPE "public"."estado_convenio_enum" OWNER TO "postgres";


CREATE TYPE "public"."estado_cuota_enum" AS ENUM (
    'PENDIENTE',
    'PAGADA',
    'VENCIDA',
    'ANULADA'
);


ALTER TYPE "public"."estado_cuota_enum" OWNER TO "postgres";


CREATE TYPE "public"."estado_envio_enum" AS ENUM (
    'PENDIENTE',
    'ENVIADO',
    'FALLIDO'
);


ALTER TYPE "public"."estado_envio_enum" OWNER TO "postgres";


CREATE TYPE "public"."estado_multa_enum" AS ENUM (
    'REGISTRADA',
    'FACTURADA',
    'ANULADA'
);


ALTER TYPE "public"."estado_multa_enum" OWNER TO "postgres";


CREATE TYPE "public"."estado_parqueadero_enum" AS ENUM (
    'DISPONIBLE',
    'OCUPADO'
);


ALTER TYPE "public"."estado_parqueadero_enum" OWNER TO "postgres";


CREATE TYPE "public"."estado_persona_enum" AS ENUM (
    'ACTIVO',
    'INACTIVO'
);


ALTER TYPE "public"."estado_persona_enum" OWNER TO "postgres";


CREATE TYPE "public"."estado_persona_unidad_enum" AS ENUM (
    'ACTIVO',
    'FINALIZADO',
    'SUSPENDIDO'
);


ALTER TYPE "public"."estado_persona_unidad_enum" OWNER TO "postgres";


CREATE TYPE "public"."estado_usuario_enum" AS ENUM (
    'ACTIVO',
    'INACTIVO',
    'BLOQUEADO'
);


ALTER TYPE "public"."estado_usuario_enum" OWNER TO "postgres";


CREATE TYPE "public"."opcion_votacion_enum" AS ENUM (
    'A_FAVOR',
    'EN_CONTRA',
    'ABSTENCION'
);


ALTER TYPE "public"."opcion_votacion_enum" OWNER TO "postgres";


CREATE TYPE "public"."prioridad_ticket_enum" AS ENUM (
    'BAJA',
    'MEDIA',
    'ALTA',
    'URGENTE'
);


ALTER TYPE "public"."prioridad_ticket_enum" OWNER TO "postgres";


CREATE TYPE "public"."tipo_asamblea_enum" AS ENUM (
    'ORDINARIA',
    'EXTRAORDINARIA'
);


ALTER TYPE "public"."tipo_asamblea_enum" OWNER TO "postgres";


CREATE TYPE "public"."tipo_cuota_enum" AS ENUM (
    'ORDINARIA',
    'EXTRAORDINARIA',
    'MULTA',
    'FONDO_RESERVA'
);


ALTER TYPE "public"."tipo_cuota_enum" OWNER TO "postgres";


CREATE TYPE "public"."tipo_identificacion_enum" AS ENUM (
    'CEDULA',
    'PASAPORTE',
    'RUC'
);


ALTER TYPE "public"."tipo_identificacion_enum" OWNER TO "postgres";


CREATE TYPE "public"."tipo_persona_unidad_enum" AS ENUM (
    'PROPIETARIO',
    'ARRENDATARIO',
    'RESIDENTE'
);


ALTER TYPE "public"."tipo_persona_unidad_enum" OWNER TO "postgres";


CREATE TYPE "public"."tipo_unidad_enum" AS ENUM (
    'DEPARTAMENTO',
    'CASA',
    'LOCAL',
    'OFICINA'
);


ALTER TYPE "public"."tipo_unidad_enum" OWNER TO "postgres";


CREATE TYPE "public"."tipo_vehiculo_enum" AS ENUM (
    'AUTO',
    'CAMIONETA',
    'MOTO',
    'BICICLETA',
    'SCOOTER'
);


ALTER TYPE "public"."tipo_vehiculo_enum" OWNER TO "postgres";


CREATE OR REPLACE FUNCTION "public"."calcular_mora"("p_id_cuota" bigint) RETURNS numeric
    LANGUAGE "plpgsql"
    AS $$
DECLARE
    v_cuota        RECORD;
    v_dias_mora    INT;
    v_dias_vencido INT;
    v_porcentaje   NUMERIC;
    v_mora         NUMERIC := 0;
BEGIN
    SELECT * INTO v_cuota FROM cuota WHERE id_cuota = p_id_cuota;
    IF NOT FOUND THEN
        RAISE EXCEPTION 'Cuota % no existe', p_id_cuota;
    END IF;

    IF v_cuota.estado NOT IN ('PENDIENTE', 'VENCIDA') THEN
        RETURN 0;
    END IF;

    v_dias_vencido := GREATEST(0, CURRENT_DATE - v_cuota.fecha_vencimiento);

    SELECT valor::INT INTO v_dias_mora FROM configuracion WHERE clave = 'DIAS_MORA';
    SELECT valor::NUMERIC INTO v_porcentaje FROM configuracion WHERE clave = 'PORCENTAJE_INTERES';

    IF v_dias_vencido > COALESCE(v_dias_mora, 30) THEN
        v_mora := ROUND(v_cuota.valor * COALESCE(v_porcentaje, 0) / 100, 2);
    END IF;

    RETURN v_mora;
END;
$$;


ALTER FUNCTION "public"."calcular_mora"("p_id_cuota" bigint) OWNER TO "postgres";


CREATE OR REPLACE FUNCTION "public"."cerrar_visitas"("p_horas_limite" integer DEFAULT 24) RETURNS integer
    LANGUAGE "plpgsql"
    AS $$
DECLARE
    v_id_finalizado BIGINT;
    v_cerradas      INT;
BEGIN
    SELECT id_estado INTO v_id_finalizado FROM estado_acceso WHERE nombre = 'FINALIZADO';

    UPDATE acceso
    SET hora_salida = now(), id_estado = v_id_finalizado
    WHERE hora_salida IS NULL
      AND hora_ingreso < now() - (p_horas_limite || ' hours')::INTERVAL;

    GET DIAGNOSTICS v_cerradas = ROW_COUNT;
    RETURN v_cerradas;
END;
$$;


ALTER FUNCTION "public"."cerrar_visitas"("p_horas_limite" integer) OWNER TO "postgres";


CREATE OR REPLACE FUNCTION "public"."disponibilidad_area"("p_area" bigint, "p_fecha" "date", "p_hora_inicio" time without time zone, "p_hora_fin" time without time zone) RETURNS boolean
    LANGUAGE "plpgsql"
    AS $$
DECLARE
    v_conflictos INT;
BEGIN
    SELECT COUNT(*) INTO v_conflictos
    FROM reserva
    WHERE id_area = p_area
      AND bloquea_horario
      AND periodo && tsrange(p_fecha + p_hora_inicio, p_fecha + p_hora_fin);

    RETURN v_conflictos = 0;
END;
$$;


ALTER FUNCTION "public"."disponibilidad_area"("p_area" bigint, "p_fecha" "date", "p_hora_inicio" time without time zone, "p_hora_fin" time without time zone) OWNER TO "postgres";


CREATE OR REPLACE FUNCTION "public"."fn_auditoria"() RETURNS "trigger"
    LANGUAGE "plpgsql"
    AS $$
DECLARE
    v_usuario     BIGINT;
    v_pk_column   TEXT;
    v_id_registro BIGINT;
    v_row         JSONB;
BEGIN
    BEGIN
        v_usuario := NULLIF(current_setting('app.usuario_actual', true), '')::BIGINT;
    EXCEPTION WHEN OTHERS THEN
        v_usuario := NULL;
    END;

    SELECT kcu.column_name INTO v_pk_column
    FROM information_schema.table_constraints tc
    JOIN information_schema.key_column_usage kcu
      ON tc.constraint_name = kcu.constraint_name AND tc.table_schema = kcu.table_schema
    WHERE tc.table_name = TG_TABLE_NAME
      AND tc.constraint_type = 'PRIMARY KEY'
    LIMIT 1;

    v_row := to_jsonb(COALESCE(NEW, OLD));
    v_id_registro := NULLIF(v_row ->> v_pk_column, '')::BIGINT;

    INSERT INTO auditoria (tabla_afectada, id_registro, accion, id_usuario, valores_anteriores, valores_nuevos, fecha)
    VALUES (
        TG_TABLE_NAME,
        v_id_registro,
        TG_OP::accion_auditoria_enum,
        v_usuario,
        CASE WHEN TG_OP IN ('UPDATE', 'DELETE') THEN to_jsonb(OLD) ELSE NULL END,
        CASE WHEN TG_OP IN ('UPDATE', 'INSERT') THEN to_jsonb(NEW) ELSE NULL END,
        now()
    );
    RETURN COALESCE(NEW, OLD);
END;
$$;


ALTER FUNCTION "public"."fn_auditoria"() OWNER TO "postgres";


CREATE OR REPLACE FUNCTION "public"."fn_chk_unidad_torre_condominio"() RETURNS "trigger"
    LANGUAGE "plpgsql"
    AS $$
BEGIN
    IF NEW.id_torre IS NOT NULL THEN
        IF NOT EXISTS (
            SELECT 1 FROM torre
            WHERE id_torre = NEW.id_torre AND id_condominio = NEW.id_condominio
        ) THEN
            RAISE EXCEPTION 'La torre % no pertenece al condominio %', NEW.id_torre, NEW.id_condominio;
        END IF;
    END IF;
    RETURN NEW;
END;
$$;


ALTER FUNCTION "public"."fn_chk_unidad_torre_condominio"() OWNER TO "postgres";


CREATE OR REPLACE FUNCTION "public"."fn_reserva_bloqueo"() RETURNS "trigger"
    LANGUAGE "plpgsql"
    AS $$
DECLARE
    v_estado VARCHAR;
BEGIN
    SELECT nombre INTO v_estado FROM estado_reserva WHERE id_estado = NEW.id_estado;
    NEW.bloquea_horario := (v_estado NOT IN ('CANCELADA', 'RECHAZADA'));
    RETURN NEW;
END;
$$;


ALTER FUNCTION "public"."fn_reserva_bloqueo"() OWNER TO "postgres";


CREATE OR REPLACE FUNCTION "public"."fn_sync_estado_actual_ticket"() RETURNS "trigger"
    LANGUAGE "plpgsql"
    AS $$
BEGIN
    UPDATE ticket SET id_estado_actual = NEW.id_estado WHERE id_ticket = NEW.id_ticket;
    RETURN NEW;
END;
$$;


ALTER FUNCTION "public"."fn_sync_estado_actual_ticket"() OWNER TO "postgres";


CREATE OR REPLACE FUNCTION "public"."generar_cuotas_mes"("p_mes" integer, "p_anio" integer, "p_tipo" "public"."tipo_cuota_enum" DEFAULT 'ORDINARIA'::"public"."tipo_cuota_enum", "p_valor_base" numeric DEFAULT NULL::numeric) RETURNS integer
    LANGUAGE "plpgsql"
    AS $$
DECLARE
    v_unidad          RECORD;
    v_valor           NUMERIC;
    v_creadas         INT := 0;
    v_valor_base_cfg  NUMERIC;
    v_base            NUMERIC;
BEGIN
    v_base := p_valor_base;
    IF v_base IS NULL THEN
        SELECT valor::NUMERIC INTO v_valor_base_cfg FROM configuracion WHERE clave = 'VALOR_CUOTA_BASE';
        v_base := COALESCE(v_valor_base_cfg, 0);
    END IF;

    FOR v_unidad IN SELECT id_unidad, alicuota FROM unidad LOOP
        v_valor := ROUND(v_base * COALESCE(v_unidad.alicuota, 1), 2);
        BEGIN
            INSERT INTO cuota (id_unidad, mes, anio, valor, tipo, fecha_vencimiento, estado)
            VALUES (
                v_unidad.id_unidad, p_mes, p_anio, v_valor, p_tipo,
                (make_date(p_anio, p_mes, 1) + INTERVAL '1 month' - INTERVAL '1 day')::DATE,
                'PENDIENTE'
            );
            v_creadas := v_creadas + 1;
        EXCEPTION WHEN unique_violation THEN
            CONTINUE;
        END;
    END LOOP;

    RETURN v_creadas;
END;
$$;


ALTER FUNCTION "public"."generar_cuotas_mes"("p_mes" integer, "p_anio" integer, "p_tipo" "public"."tipo_cuota_enum", "p_valor_base" numeric) OWNER TO "postgres";


CREATE OR REPLACE FUNCTION "public"."historial_residente"("p_id_persona" bigint) RETURNS TABLE("id_unidad" bigint, "numero_unidad" character varying, "tipo" "public"."tipo_persona_unidad_enum", "estado" "public"."estado_persona_unidad_enum", "fecha_inicio" "date", "fecha_fin" "date")
    LANGUAGE "plpgsql"
    AS $$
BEGIN
    RETURN QUERY
    SELECT u.id_unidad, u.numero, pu.tipo, pu.estado, pu.fecha_inicio, pu.fecha_fin
    FROM persona_unidad pu
    JOIN unidad u ON u.id_unidad = pu.id_unidad
    WHERE pu.id_persona = p_id_persona
    ORDER BY pu.fecha_inicio DESC;
END;
$$;


ALTER FUNCTION "public"."historial_residente"("p_id_persona" bigint) OWNER TO "postgres";


CREATE OR REPLACE FUNCTION "public"."saldo_unidad"("p_id_unidad" bigint) RETURNS numeric
    LANGUAGE "plpgsql"
    AS $$
DECLARE
    v_deuda  NUMERIC;
    v_pagado NUMERIC;
BEGIN
    SELECT COALESCE(SUM(valor), 0) INTO v_deuda
    FROM cuota WHERE id_unidad = p_id_unidad AND estado IN ('PENDIENTE', 'VENCIDA');

    SELECT COALESCE(SUM(p.valor), 0) INTO v_pagado
    FROM pago p
    JOIN cuota c ON c.id_cuota = p.id_cuota
    JOIN estado_pago ep ON ep.id_estado = p.id_estado
    WHERE c.id_unidad = p_id_unidad
      AND ep.nombre = 'CONFIRMADO'
      AND c.estado IN ('PENDIENTE', 'VENCIDA');

    RETURN v_deuda - v_pagado;
END;
$$;


ALTER FUNCTION "public"."saldo_unidad"("p_id_unidad" bigint) OWNER TO "postgres";

SET default_tablespace = '';

SET default_table_access_method = "heap";


CREATE TABLE IF NOT EXISTS "public"."acceso" (
    "id_acceso" bigint NOT NULL,
    "id_visitante" bigint NOT NULL,
    "id_unidad" bigint NOT NULL,
    "id_guardia" bigint NOT NULL,
    "id_vehiculo" bigint,
    "id_preautorizacion" bigint,
    "id_estado" bigint NOT NULL,
    "hora_ingreso" timestamp with time zone DEFAULT "now"() NOT NULL,
    "hora_salida" timestamp with time zone,
    "foto" "text",
    CONSTRAINT "acceso_check" CHECK ((("hora_salida" IS NULL) OR ("hora_salida" >= "hora_ingreso")))
);


ALTER TABLE "public"."acceso" OWNER TO "postgres";


CREATE SEQUENCE IF NOT EXISTS "public"."acceso_id_acceso_seq"
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE "public"."acceso_id_acceso_seq" OWNER TO "postgres";


ALTER SEQUENCE "public"."acceso_id_acceso_seq" OWNED BY "public"."acceso"."id_acceso";



CREATE TABLE IF NOT EXISTS "public"."acta" (
    "id_acta" bigint NOT NULL,
    "id_asamblea" bigint NOT NULL,
    "contenido" "text"
);


ALTER TABLE "public"."acta" OWNER TO "postgres";


CREATE TABLE IF NOT EXISTS "public"."acta_archivo" (
    "id_acta" bigint NOT NULL,
    "id_archivo" bigint NOT NULL
);


ALTER TABLE "public"."acta_archivo" OWNER TO "postgres";


CREATE SEQUENCE IF NOT EXISTS "public"."acta_id_acta_seq"
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE "public"."acta_id_acta_seq" OWNER TO "postgres";


ALTER SEQUENCE "public"."acta_id_acta_seq" OWNED BY "public"."acta"."id_acta";



CREATE TABLE IF NOT EXISTS "public"."archivo" (
    "id_archivo" bigint NOT NULL,
    "nombre" character varying(255) NOT NULL,
    "ruta" "text" NOT NULL,
    "tipo" character varying(50) NOT NULL,
    "mime_type" character varying(100),
    "tamano" bigint,
    "fecha" timestamp with time zone DEFAULT "now"() NOT NULL
);


ALTER TABLE "public"."archivo" OWNER TO "postgres";


CREATE SEQUENCE IF NOT EXISTS "public"."archivo_id_archivo_seq"
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE "public"."archivo_id_archivo_seq" OWNER TO "postgres";


ALTER SEQUENCE "public"."archivo_id_archivo_seq" OWNED BY "public"."archivo"."id_archivo";



CREATE TABLE IF NOT EXISTS "public"."area_comun" (
    "id_area" bigint NOT NULL,
    "id_condominio" bigint NOT NULL,
    "nombre" character varying(100) NOT NULL,
    "descripcion" "text",
    "capacidad" integer
);


ALTER TABLE "public"."area_comun" OWNER TO "postgres";


CREATE SEQUENCE IF NOT EXISTS "public"."area_comun_id_area_seq"
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE "public"."area_comun_id_area_seq" OWNER TO "postgres";


ALTER SEQUENCE "public"."area_comun_id_area_seq" OWNED BY "public"."area_comun"."id_area";



CREATE TABLE IF NOT EXISTS "public"."asamblea" (
    "id_asamblea" bigint NOT NULL,
    "id_condominio" bigint NOT NULL,
    "fecha" timestamp with time zone NOT NULL,
    "tipo" "public"."tipo_asamblea_enum" NOT NULL,
    "quorum_requerido" numeric(5,2),
    "estado" "public"."estado_asamblea_enum" DEFAULT 'PROGRAMADA'::"public"."estado_asamblea_enum" NOT NULL
);


ALTER TABLE "public"."asamblea" OWNER TO "postgres";


CREATE SEQUENCE IF NOT EXISTS "public"."asamblea_id_asamblea_seq"
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE "public"."asamblea_id_asamblea_seq" OWNER TO "postgres";


ALTER SEQUENCE "public"."asamblea_id_asamblea_seq" OWNED BY "public"."asamblea"."id_asamblea";



CREATE TABLE IF NOT EXISTS "public"."auditoria" (
    "id_auditoria" bigint NOT NULL,
    "tabla_afectada" character varying(100) NOT NULL,
    "id_registro" bigint NOT NULL,
    "accion" "public"."accion_auditoria_enum" NOT NULL,
    "id_usuario" bigint,
    "valores_anteriores" "jsonb",
    "valores_nuevos" "jsonb",
    "ip" "inet",
    "user_agent" "text",
    "fecha" timestamp with time zone DEFAULT "now"() NOT NULL
);


ALTER TABLE "public"."auditoria" OWNER TO "postgres";


CREATE SEQUENCE IF NOT EXISTS "public"."auditoria_id_auditoria_seq"
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE "public"."auditoria_id_auditoria_seq" OWNER TO "postgres";


ALTER SEQUENCE "public"."auditoria_id_auditoria_seq" OWNED BY "public"."auditoria"."id_auditoria";



CREATE TABLE IF NOT EXISTS "public"."categoria" (
    "id_categoria" bigint NOT NULL,
    "nombre" character varying(100) NOT NULL
);


ALTER TABLE "public"."categoria" OWNER TO "postgres";


CREATE SEQUENCE IF NOT EXISTS "public"."categoria_id_categoria_seq"
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE "public"."categoria_id_categoria_seq" OWNER TO "postgres";


ALTER SEQUENCE "public"."categoria_id_categoria_seq" OWNED BY "public"."categoria"."id_categoria";



CREATE TABLE IF NOT EXISTS "public"."comunicado" (
    "id_comunicado" bigint NOT NULL,
    "titulo" character varying(150) NOT NULL,
    "mensaje" "text" NOT NULL,
    "fecha" timestamp with time zone DEFAULT "now"() NOT NULL,
    "id_autor" bigint NOT NULL,
    "destinatario_tipo" "public"."destinatario_tipo_enum" NOT NULL,
    "destinatario_id" bigint
);


ALTER TABLE "public"."comunicado" OWNER TO "postgres";


CREATE SEQUENCE IF NOT EXISTS "public"."comunicado_id_comunicado_seq"
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE "public"."comunicado_id_comunicado_seq" OWNER TO "postgres";


ALTER SEQUENCE "public"."comunicado_id_comunicado_seq" OWNED BY "public"."comunicado"."id_comunicado";



CREATE TABLE IF NOT EXISTS "public"."comunicado_lectura" (
    "id_comunicado" bigint NOT NULL,
    "id_persona" bigint NOT NULL,
    "fecha_lectura" timestamp with time zone DEFAULT "now"() NOT NULL
);


ALTER TABLE "public"."comunicado_lectura" OWNER TO "postgres";


CREATE TABLE IF NOT EXISTS "public"."condominio" (
    "id_condominio" bigint NOT NULL,
    "nombre" character varying(150) NOT NULL,
    "direccion" character varying(255),
    "telefono" character varying(30),
    "email" character varying(150)
);


ALTER TABLE "public"."condominio" OWNER TO "postgres";


CREATE SEQUENCE IF NOT EXISTS "public"."condominio_id_condominio_seq"
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE "public"."condominio_id_condominio_seq" OWNER TO "postgres";


ALTER SEQUENCE "public"."condominio_id_condominio_seq" OWNED BY "public"."condominio"."id_condominio";



CREATE TABLE IF NOT EXISTS "public"."configuracion" (
    "id_configuracion" bigint NOT NULL,
    "clave" character varying(100) NOT NULL,
    "valor" "text" NOT NULL
);


ALTER TABLE "public"."configuracion" OWNER TO "postgres";


CREATE SEQUENCE IF NOT EXISTS "public"."configuracion_id_configuracion_seq"
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE "public"."configuracion_id_configuracion_seq" OWNER TO "postgres";


ALTER SEQUENCE "public"."configuracion_id_configuracion_seq" OWNED BY "public"."configuracion"."id_configuracion";



CREATE TABLE IF NOT EXISTS "public"."convenio_pago" (
    "id_convenio" bigint NOT NULL,
    "id_persona" bigint NOT NULL,
    "id_unidad" bigint NOT NULL,
    "monto_total" numeric(10,2) NOT NULL,
    "num_cuotas" smallint NOT NULL,
    "fecha_inicio" "date" NOT NULL,
    "estado" "public"."estado_convenio_enum" DEFAULT 'ACTIVO'::"public"."estado_convenio_enum" NOT NULL,
    CONSTRAINT "convenio_pago_monto_total_check" CHECK (("monto_total" > (0)::numeric)),
    CONSTRAINT "convenio_pago_num_cuotas_check" CHECK (("num_cuotas" > 0))
);


ALTER TABLE "public"."convenio_pago" OWNER TO "postgres";


CREATE SEQUENCE IF NOT EXISTS "public"."convenio_pago_id_convenio_seq"
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE "public"."convenio_pago_id_convenio_seq" OWNER TO "postgres";


ALTER SEQUENCE "public"."convenio_pago_id_convenio_seq" OWNED BY "public"."convenio_pago"."id_convenio";



CREATE TABLE IF NOT EXISTS "public"."cuota" (
    "id_cuota" bigint NOT NULL,
    "id_unidad" bigint NOT NULL,
    "mes" smallint NOT NULL,
    "anio" smallint NOT NULL,
    "valor" numeric(10,2) NOT NULL,
    "tipo" "public"."tipo_cuota_enum" NOT NULL,
    "descripcion" "text",
    "fecha_vencimiento" "date" NOT NULL,
    "estado" "public"."estado_cuota_enum" DEFAULT 'PENDIENTE'::"public"."estado_cuota_enum" NOT NULL,
    CONSTRAINT "cuota_mes_check" CHECK ((("mes" >= 1) AND ("mes" <= 12))),
    CONSTRAINT "cuota_valor_check" CHECK (("valor" >= (0)::numeric))
);


ALTER TABLE "public"."cuota" OWNER TO "postgres";


CREATE SEQUENCE IF NOT EXISTS "public"."cuota_id_cuota_seq"
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE "public"."cuota_id_cuota_seq" OWNER TO "postgres";


ALTER SEQUENCE "public"."cuota_id_cuota_seq" OWNED BY "public"."cuota"."id_cuota";



CREATE TABLE IF NOT EXISTS "public"."estado_acceso" (
    "id_estado" bigint NOT NULL,
    "nombre" character varying(50) NOT NULL
);


ALTER TABLE "public"."estado_acceso" OWNER TO "postgres";


CREATE SEQUENCE IF NOT EXISTS "public"."estado_acceso_id_estado_seq"
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE "public"."estado_acceso_id_estado_seq" OWNER TO "postgres";


ALTER SEQUENCE "public"."estado_acceso_id_estado_seq" OWNED BY "public"."estado_acceso"."id_estado";



CREATE TABLE IF NOT EXISTS "public"."estado_pago" (
    "id_estado" bigint NOT NULL,
    "nombre" character varying(50) NOT NULL
);


ALTER TABLE "public"."estado_pago" OWNER TO "postgres";


CREATE SEQUENCE IF NOT EXISTS "public"."estado_pago_id_estado_seq"
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE "public"."estado_pago_id_estado_seq" OWNER TO "postgres";


ALTER SEQUENCE "public"."estado_pago_id_estado_seq" OWNED BY "public"."estado_pago"."id_estado";



CREATE TABLE IF NOT EXISTS "public"."estado_reserva" (
    "id_estado" bigint NOT NULL,
    "nombre" character varying(50) NOT NULL
);


ALTER TABLE "public"."estado_reserva" OWNER TO "postgres";


CREATE SEQUENCE IF NOT EXISTS "public"."estado_reserva_id_estado_seq"
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE "public"."estado_reserva_id_estado_seq" OWNER TO "postgres";


ALTER SEQUENCE "public"."estado_reserva_id_estado_seq" OWNED BY "public"."estado_reserva"."id_estado";



CREATE TABLE IF NOT EXISTS "public"."estado_ticket" (
    "id_estado" bigint NOT NULL,
    "nombre" character varying(50) NOT NULL
);


ALTER TABLE "public"."estado_ticket" OWNER TO "postgres";


CREATE SEQUENCE IF NOT EXISTS "public"."estado_ticket_id_estado_seq"
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE "public"."estado_ticket_id_estado_seq" OWNER TO "postgres";


ALTER SEQUENCE "public"."estado_ticket_id_estado_seq" OWNED BY "public"."estado_ticket"."id_estado";



CREATE TABLE IF NOT EXISTS "public"."estado_unidad" (
    "id_estado" bigint NOT NULL,
    "nombre" character varying(50) NOT NULL
);


ALTER TABLE "public"."estado_unidad" OWNER TO "postgres";


CREATE SEQUENCE IF NOT EXISTS "public"."estado_unidad_id_estado_seq"
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE "public"."estado_unidad_id_estado_seq" OWNER TO "postgres";


ALTER SEQUENCE "public"."estado_unidad_id_estado_seq" OWNED BY "public"."estado_unidad"."id_estado";



CREATE TABLE IF NOT EXISTS "public"."flyway_schema_history" (
    "installed_rank" integer NOT NULL,
    "version" character varying(50),
    "description" character varying(200) NOT NULL,
    "type" character varying(20) NOT NULL,
    "script" character varying(1000) NOT NULL,
    "checksum" integer,
    "installed_by" character varying(100) NOT NULL,
    "installed_on" timestamp without time zone DEFAULT "now"() NOT NULL,
    "execution_time" integer NOT NULL,
    "success" boolean NOT NULL
);


ALTER TABLE "public"."flyway_schema_history" OWNER TO "postgres";


CREATE TABLE IF NOT EXISTS "public"."historial_ticket" (
    "id_historial" bigint NOT NULL,
    "id_ticket" bigint NOT NULL,
    "id_estado" bigint NOT NULL,
    "id_usuario" bigint NOT NULL,
    "fecha" timestamp with time zone DEFAULT "now"() NOT NULL,
    "comentario" "text"
);


ALTER TABLE "public"."historial_ticket" OWNER TO "postgres";


CREATE SEQUENCE IF NOT EXISTS "public"."historial_ticket_id_historial_seq"
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE "public"."historial_ticket_id_historial_seq" OWNER TO "postgres";


ALTER SEQUENCE "public"."historial_ticket_id_historial_seq" OWNED BY "public"."historial_ticket"."id_historial";



CREATE TABLE IF NOT EXISTS "public"."login" (
    "id_login" bigint NOT NULL,
    "id_usuario" bigint NOT NULL,
    "ip" "inet" NOT NULL,
    "user_agent" "text",
    "fecha" timestamp with time zone DEFAULT "now"() NOT NULL,
    "exitoso" boolean NOT NULL
);


ALTER TABLE "public"."login" OWNER TO "postgres";


CREATE SEQUENCE IF NOT EXISTS "public"."login_id_login_seq"
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE "public"."login_id_login_seq" OWNER TO "postgres";


ALTER SEQUENCE "public"."login_id_login_seq" OWNED BY "public"."login"."id_login";



CREATE TABLE IF NOT EXISTS "public"."multa" (
    "id_multa" bigint NOT NULL,
    "id_unidad" bigint NOT NULL,
    "id_persona" bigint NOT NULL,
    "id_cuota" bigint,
    "motivo" character varying(150) NOT NULL,
    "descripcion" "text",
    "valor" numeric(10,2) NOT NULL,
    "fecha" "date" DEFAULT CURRENT_DATE NOT NULL,
    "estado" "public"."estado_multa_enum" DEFAULT 'REGISTRADA'::"public"."estado_multa_enum" NOT NULL,
    CONSTRAINT "multa_valor_check" CHECK (("valor" > (0)::numeric))
);


ALTER TABLE "public"."multa" OWNER TO "postgres";


CREATE SEQUENCE IF NOT EXISTS "public"."multa_id_multa_seq"
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE "public"."multa_id_multa_seq" OWNER TO "postgres";


ALTER SEQUENCE "public"."multa_id_multa_seq" OWNED BY "public"."multa"."id_multa";



CREATE TABLE IF NOT EXISTS "public"."notificacion" (
    "id_notificacion" bigint NOT NULL,
    "id_persona" bigint NOT NULL,
    "tipo" character varying(50) NOT NULL,
    "titulo" character varying(150) NOT NULL,
    "mensaje" "text" NOT NULL,
    "canal" "public"."canal_notificacion_enum" NOT NULL,
    "estado_envio" "public"."estado_envio_enum" DEFAULT 'PENDIENTE'::"public"."estado_envio_enum" NOT NULL,
    "fecha_envio" timestamp with time zone,
    "leido" boolean DEFAULT false NOT NULL,
    "fecha_lectura" timestamp with time zone
);


ALTER TABLE "public"."notificacion" OWNER TO "postgres";


CREATE SEQUENCE IF NOT EXISTS "public"."notificacion_id_notificacion_seq"
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE "public"."notificacion_id_notificacion_seq" OWNER TO "postgres";


ALTER SEQUENCE "public"."notificacion_id_notificacion_seq" OWNED BY "public"."notificacion"."id_notificacion";



CREATE TABLE IF NOT EXISTS "public"."pago" (
    "id_pago" bigint NOT NULL,
    "id_cuota" bigint NOT NULL,
    "id_estado" bigint NOT NULL,
    "fecha" timestamp with time zone DEFAULT "now"() NOT NULL,
    "valor" numeric(10,2) NOT NULL,
    "metodo" character varying(50) NOT NULL,
    "referencia" character varying(100),
    CONSTRAINT "pago_valor_check" CHECK (("valor" > (0)::numeric))
);


ALTER TABLE "public"."pago" OWNER TO "postgres";


CREATE SEQUENCE IF NOT EXISTS "public"."pago_id_pago_seq"
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE "public"."pago_id_pago_seq" OWNER TO "postgres";


ALTER SEQUENCE "public"."pago_id_pago_seq" OWNED BY "public"."pago"."id_pago";



CREATE TABLE IF NOT EXISTS "public"."parqueadero" (
    "id_parqueadero" bigint NOT NULL,
    "id_unidad" bigint NOT NULL,
    "numero" character varying(20) NOT NULL,
    "estado" "public"."estado_parqueadero_enum" DEFAULT 'DISPONIBLE'::"public"."estado_parqueadero_enum" NOT NULL
);


ALTER TABLE "public"."parqueadero" OWNER TO "postgres";


CREATE SEQUENCE IF NOT EXISTS "public"."parqueadero_id_parqueadero_seq"
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE "public"."parqueadero_id_parqueadero_seq" OWNER TO "postgres";


ALTER SEQUENCE "public"."parqueadero_id_parqueadero_seq" OWNED BY "public"."parqueadero"."id_parqueadero";



CREATE TABLE IF NOT EXISTS "public"."permiso" (
    "id_permiso" bigint NOT NULL,
    "nombre" character varying(100) NOT NULL,
    "modulo" character varying(50) NOT NULL,
    "accion" character varying(50) NOT NULL
);


ALTER TABLE "public"."permiso" OWNER TO "postgres";


CREATE SEQUENCE IF NOT EXISTS "public"."permiso_id_permiso_seq"
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE "public"."permiso_id_permiso_seq" OWNER TO "postgres";


ALTER SEQUENCE "public"."permiso_id_permiso_seq" OWNED BY "public"."permiso"."id_permiso";



CREATE TABLE IF NOT EXISTS "public"."persona" (
    "id_persona" bigint NOT NULL,
    "tipo_identificacion" "public"."tipo_identificacion_enum" NOT NULL,
    "numero_identificacion" character varying(30) NOT NULL,
    "nombres" character varying(100) NOT NULL,
    "apellidos" character varying(100) NOT NULL,
    "telefono" character varying(30),
    "correo" character varying(254) NOT NULL,
    "fecha_nacimiento" "date",
    "direccion" character varying(255),
    "foto_perfil" "text",
    "estado" "public"."estado_persona_enum" DEFAULT 'ACTIVO'::"public"."estado_persona_enum" NOT NULL
);


ALTER TABLE "public"."persona" OWNER TO "postgres";


CREATE SEQUENCE IF NOT EXISTS "public"."persona_id_persona_seq"
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE "public"."persona_id_persona_seq" OWNER TO "postgres";


ALTER SEQUENCE "public"."persona_id_persona_seq" OWNED BY "public"."persona"."id_persona";



CREATE TABLE IF NOT EXISTS "public"."persona_unidad" (
    "id_persona_unidad" bigint NOT NULL,
    "id_persona" bigint NOT NULL,
    "id_unidad" bigint NOT NULL,
    "tipo" "public"."tipo_persona_unidad_enum" NOT NULL,
    "estado" "public"."estado_persona_unidad_enum" DEFAULT 'ACTIVO'::"public"."estado_persona_unidad_enum" NOT NULL,
    "fecha_inicio" "date" NOT NULL,
    "fecha_fin" "date",
    CONSTRAINT "persona_unidad_check" CHECK ((("fecha_fin" IS NULL) OR ("fecha_fin" >= "fecha_inicio")))
);


ALTER TABLE "public"."persona_unidad" OWNER TO "postgres";


CREATE SEQUENCE IF NOT EXISTS "public"."persona_unidad_id_persona_unidad_seq"
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE "public"."persona_unidad_id_persona_unidad_seq" OWNER TO "postgres";


ALTER SEQUENCE "public"."persona_unidad_id_persona_unidad_seq" OWNED BY "public"."persona_unidad"."id_persona_unidad";



CREATE TABLE IF NOT EXISTS "public"."recibo" (
    "id_recibo" bigint NOT NULL,
    "numero" character varying(30) NOT NULL,
    "id_pago" bigint NOT NULL,
    "id_archivo" bigint
);


ALTER TABLE "public"."recibo" OWNER TO "postgres";


CREATE SEQUENCE IF NOT EXISTS "public"."recibo_id_recibo_seq"
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE "public"."recibo_id_recibo_seq" OWNER TO "postgres";


ALTER SEQUENCE "public"."recibo_id_recibo_seq" OWNED BY "public"."recibo"."id_recibo";



CREATE TABLE IF NOT EXISTS "public"."refresh_token" (
    "id_refresh_token" bigint NOT NULL,
    "id_usuario" bigint NOT NULL,
    "token" "text" NOT NULL,
    "ip" "inet",
    "dispositivo" character varying(150),
    "fecha_expiracion" timestamp with time zone NOT NULL,
    "revocado" boolean DEFAULT false NOT NULL,
    "fecha_creacion" timestamp with time zone DEFAULT "now"() NOT NULL
);


ALTER TABLE "public"."refresh_token" OWNER TO "postgres";


CREATE SEQUENCE IF NOT EXISTS "public"."refresh_token_id_refresh_token_seq"
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE "public"."refresh_token_id_refresh_token_seq" OWNER TO "postgres";


ALTER SEQUENCE "public"."refresh_token_id_refresh_token_seq" OWNED BY "public"."refresh_token"."id_refresh_token";



CREATE TABLE IF NOT EXISTS "public"."reserva" (
    "id_reserva" bigint NOT NULL,
    "id_area" bigint NOT NULL,
    "id_persona" bigint NOT NULL,
    "id_estado" bigint NOT NULL,
    "id_usuario_aprobador" bigint,
    "fecha" "date" NOT NULL,
    "hora_inicio" time without time zone NOT NULL,
    "hora_fin" time without time zone NOT NULL,
    "fecha_creacion" timestamp with time zone DEFAULT "now"() NOT NULL,
    "motivo" character varying(200),
    "observaciones" "text",
    "periodo" "tsrange" GENERATED ALWAYS AS ("tsrange"(("fecha" + "hora_inicio"), ("fecha" + "hora_fin"))) STORED,
    "bloquea_horario" boolean DEFAULT true NOT NULL,
    CONSTRAINT "reserva_check" CHECK (("hora_fin" > "hora_inicio"))
);


ALTER TABLE "public"."reserva" OWNER TO "postgres";


CREATE SEQUENCE IF NOT EXISTS "public"."reserva_id_reserva_seq"
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE "public"."reserva_id_reserva_seq" OWNER TO "postgres";


ALTER SEQUENCE "public"."reserva_id_reserva_seq" OWNED BY "public"."reserva"."id_reserva";



CREATE TABLE IF NOT EXISTS "public"."rol" (
    "id_rol" bigint NOT NULL,
    "nombre" character varying(50) NOT NULL,
    "descripcion" "text"
);


ALTER TABLE "public"."rol" OWNER TO "postgres";


CREATE SEQUENCE IF NOT EXISTS "public"."rol_id_rol_seq"
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE "public"."rol_id_rol_seq" OWNER TO "postgres";


ALTER SEQUENCE "public"."rol_id_rol_seq" OWNED BY "public"."rol"."id_rol";



CREATE TABLE IF NOT EXISTS "public"."rol_permiso" (
    "id_rol" bigint NOT NULL,
    "id_permiso" bigint NOT NULL
);


ALTER TABLE "public"."rol_permiso" OWNER TO "postgres";


CREATE TABLE IF NOT EXISTS "public"."ticket" (
    "id_ticket" bigint NOT NULL,
    "id_persona" bigint NOT NULL,
    "id_unidad" bigint NOT NULL,
    "id_tecnico" bigint,
    "id_categoria" bigint,
    "id_estado_actual" bigint,
    "titulo" character varying(150) NOT NULL,
    "descripcion" "text" NOT NULL,
    "prioridad" "public"."prioridad_ticket_enum" DEFAULT 'MEDIA'::"public"."prioridad_ticket_enum" NOT NULL,
    "fecha_creacion" timestamp with time zone DEFAULT "now"() NOT NULL,
    "fecha_cierre" timestamp with time zone
);


ALTER TABLE "public"."ticket" OWNER TO "postgres";


CREATE TABLE IF NOT EXISTS "public"."ticket_archivo" (
    "id_ticket" bigint NOT NULL,
    "id_archivo" bigint NOT NULL
);


ALTER TABLE "public"."ticket_archivo" OWNER TO "postgres";


CREATE TABLE IF NOT EXISTS "public"."ticket_comentario" (
    "id_comentario" bigint NOT NULL,
    "id_ticket" bigint NOT NULL,
    "id_persona" bigint NOT NULL,
    "comentario" "text" NOT NULL,
    "fecha" timestamp with time zone DEFAULT "now"() NOT NULL
);


ALTER TABLE "public"."ticket_comentario" OWNER TO "postgres";


CREATE SEQUENCE IF NOT EXISTS "public"."ticket_comentario_id_comentario_seq"
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE "public"."ticket_comentario_id_comentario_seq" OWNER TO "postgres";


ALTER SEQUENCE "public"."ticket_comentario_id_comentario_seq" OWNED BY "public"."ticket_comentario"."id_comentario";



CREATE SEQUENCE IF NOT EXISTS "public"."ticket_id_ticket_seq"
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE "public"."ticket_id_ticket_seq" OWNER TO "postgres";


ALTER SEQUENCE "public"."ticket_id_ticket_seq" OWNED BY "public"."ticket"."id_ticket";



CREATE TABLE IF NOT EXISTS "public"."torre" (
    "id_torre" bigint NOT NULL,
    "id_condominio" bigint NOT NULL,
    "nombre" character varying(100) NOT NULL
);


ALTER TABLE "public"."torre" OWNER TO "postgres";


CREATE SEQUENCE IF NOT EXISTS "public"."torre_id_torre_seq"
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE "public"."torre_id_torre_seq" OWNER TO "postgres";


ALTER SEQUENCE "public"."torre_id_torre_seq" OWNED BY "public"."torre"."id_torre";



CREATE TABLE IF NOT EXISTS "public"."unidad" (
    "id_unidad" bigint NOT NULL,
    "id_condominio" bigint NOT NULL,
    "id_torre" bigint,
    "id_estado" bigint NOT NULL,
    "numero" character varying(20) NOT NULL,
    "piso" character varying(10),
    "tipo" "public"."tipo_unidad_enum" NOT NULL,
    "alicuota" numeric(8,6)
);


ALTER TABLE "public"."unidad" OWNER TO "postgres";


CREATE SEQUENCE IF NOT EXISTS "public"."unidad_id_unidad_seq"
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE "public"."unidad_id_unidad_seq" OWNER TO "postgres";


ALTER SEQUENCE "public"."unidad_id_unidad_seq" OWNED BY "public"."unidad"."id_unidad";



CREATE TABLE IF NOT EXISTS "public"."usuario" (
    "id_usuario" bigint NOT NULL,
    "id_persona" bigint NOT NULL,
    "username" character varying(50) NOT NULL,
    "password_hash" "text" NOT NULL,
    "estado" "public"."estado_usuario_enum" DEFAULT 'ACTIVO'::"public"."estado_usuario_enum" NOT NULL,
    "fecha_creacion" timestamp with time zone DEFAULT "now"() NOT NULL,
    "ultimo_login" timestamp with time zone,
    "intentos_fallidos" integer DEFAULT 0 NOT NULL,
    "bloqueado_hasta" timestamp with time zone,
    "token_recuperacion" "text",
    "fecha_expiracion_token" timestamp with time zone
);


ALTER TABLE "public"."usuario" OWNER TO "postgres";


CREATE SEQUENCE IF NOT EXISTS "public"."usuario_id_usuario_seq"
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE "public"."usuario_id_usuario_seq" OWNER TO "postgres";


ALTER SEQUENCE "public"."usuario_id_usuario_seq" OWNED BY "public"."usuario"."id_usuario";



CREATE TABLE IF NOT EXISTS "public"."usuario_rol" (
    "id_usuario" bigint NOT NULL,
    "id_rol" bigint NOT NULL,
    "fecha_asignacion" timestamp with time zone DEFAULT "now"() NOT NULL
);


ALTER TABLE "public"."usuario_rol" OWNER TO "postgres";


CREATE TABLE IF NOT EXISTS "public"."vehiculo" (
    "id_vehiculo" bigint NOT NULL,
    "id_unidad" bigint NOT NULL,
    "id_persona_actual" bigint,
    "tipo" "public"."tipo_vehiculo_enum" NOT NULL,
    "placa" character varying(15),
    "marca" character varying(50),
    "modelo" character varying(50),
    "color" character varying(30)
);


ALTER TABLE "public"."vehiculo" OWNER TO "postgres";


CREATE SEQUENCE IF NOT EXISTS "public"."vehiculo_id_vehiculo_seq"
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE "public"."vehiculo_id_vehiculo_seq" OWNER TO "postgres";


ALTER SEQUENCE "public"."vehiculo_id_vehiculo_seq" OWNED BY "public"."vehiculo"."id_vehiculo";



CREATE TABLE IF NOT EXISTS "public"."visitante" (
    "id_visitante" bigint NOT NULL,
    "nombre" character varying(150) NOT NULL,
    "cedula" character varying(30),
    "telefono" character varying(30)
);


ALTER TABLE "public"."visitante" OWNER TO "postgres";


CREATE SEQUENCE IF NOT EXISTS "public"."visitante_id_visitante_seq"
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE "public"."visitante_id_visitante_seq" OWNER TO "postgres";


ALTER SEQUENCE "public"."visitante_id_visitante_seq" OWNED BY "public"."visitante"."id_visitante";



CREATE TABLE IF NOT EXISTS "public"."visitante_preautorizado" (
    "id_preautorizacion" bigint NOT NULL,
    "id_visitante" bigint NOT NULL,
    "id_unidad" bigint NOT NULL,
    "autorizado_por" bigint NOT NULL,
    "fecha_autorizada" timestamp with time zone DEFAULT "now"() NOT NULL
);


ALTER TABLE "public"."visitante_preautorizado" OWNER TO "postgres";


CREATE SEQUENCE IF NOT EXISTS "public"."visitante_preautorizado_id_preautorizacion_seq"
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE "public"."visitante_preautorizado_id_preautorizacion_seq" OWNER TO "postgres";


ALTER SEQUENCE "public"."visitante_preautorizado_id_preautorizacion_seq" OWNED BY "public"."visitante_preautorizado"."id_preautorizacion";



CREATE TABLE IF NOT EXISTS "public"."votacion" (
    "id_votacion" bigint NOT NULL,
    "id_asamblea" bigint NOT NULL,
    "id_persona" bigint NOT NULL,
    "opcion" "public"."opcion_votacion_enum" NOT NULL,
    "fecha" timestamp with time zone DEFAULT "now"() NOT NULL
);


ALTER TABLE "public"."votacion" OWNER TO "postgres";


CREATE SEQUENCE IF NOT EXISTS "public"."votacion_id_votacion_seq"
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE "public"."votacion_id_votacion_seq" OWNER TO "postgres";


ALTER SEQUENCE "public"."votacion_id_votacion_seq" OWNED BY "public"."votacion"."id_votacion";



CREATE OR REPLACE VIEW "public"."vw_estado_cuenta" AS
 SELECT "u"."id_unidad",
    "u"."numero" AS "unidad",
    ((("p"."nombres")::"text" || ' '::"text") || ("p"."apellidos")::"text") AS "propietario",
    "public"."saldo_unidad"("u"."id_unidad") AS "saldo_pendiente"
   FROM (("public"."unidad" "u"
     LEFT JOIN "public"."persona_unidad" "pu" ON ((("pu"."id_unidad" = "u"."id_unidad") AND ("pu"."tipo" = 'PROPIETARIO'::"public"."tipo_persona_unidad_enum") AND ("pu"."estado" = 'ACTIVO'::"public"."estado_persona_unidad_enum"))))
     LEFT JOIN "public"."persona" "p" ON (("p"."id_persona" = "pu"."id_persona")));


ALTER VIEW "public"."vw_estado_cuenta" OWNER TO "postgres";


CREATE OR REPLACE VIEW "public"."vw_pagos_pendientes" AS
 SELECT "c"."id_cuota",
    "u"."numero" AS "unidad",
    "c"."tipo",
    "c"."valor",
    "c"."fecha_vencimiento",
    "public"."calcular_mora"("c"."id_cuota") AS "mora_calculada"
   FROM ("public"."cuota" "c"
     JOIN "public"."unidad" "u" ON (("u"."id_unidad" = "c"."id_unidad")))
  WHERE ("c"."estado" = ANY (ARRAY['PENDIENTE'::"public"."estado_cuota_enum", 'VENCIDA'::"public"."estado_cuota_enum"]));


ALTER VIEW "public"."vw_pagos_pendientes" OWNER TO "postgres";


CREATE OR REPLACE VIEW "public"."vw_reservas_hoy" AS
 SELECT "r"."id_reserva",
    "ac"."nombre" AS "area",
    ((("p"."nombres")::"text" || ' '::"text") || ("p"."apellidos")::"text") AS "solicitante",
    "r"."hora_inicio",
    "r"."hora_fin",
    "er"."nombre" AS "estado"
   FROM ((("public"."reserva" "r"
     JOIN "public"."area_comun" "ac" ON (("ac"."id_area" = "r"."id_area")))
     JOIN "public"."persona" "p" ON (("p"."id_persona" = "r"."id_persona")))
     JOIN "public"."estado_reserva" "er" ON (("er"."id_estado" = "r"."id_estado")))
  WHERE ("r"."fecha" = CURRENT_DATE)
  ORDER BY "r"."hora_inicio";


ALTER VIEW "public"."vw_reservas_hoy" OWNER TO "postgres";


CREATE OR REPLACE VIEW "public"."vw_ticket_resumen" AS
 SELECT "t"."id_ticket",
    "t"."titulo",
    "t"."prioridad",
    "et"."nombre" AS "estado_actual",
    ((("p"."nombres")::"text" || ' '::"text") || ("p"."apellidos")::"text") AS "reportante",
    ((("tec"."nombres")::"text" || ' '::"text") || ("tec"."apellidos")::"text") AS "tecnico",
    "t"."fecha_creacion",
    "t"."fecha_cierre"
   FROM ((("public"."ticket" "t"
     LEFT JOIN "public"."estado_ticket" "et" ON (("et"."id_estado" = "t"."id_estado_actual")))
     JOIN "public"."persona" "p" ON (("p"."id_persona" = "t"."id_persona")))
     LEFT JOIN "public"."persona" "tec" ON (("tec"."id_persona" = "t"."id_tecnico")));


ALTER VIEW "public"."vw_ticket_resumen" OWNER TO "postgres";


CREATE OR REPLACE VIEW "public"."vw_unidades_ocupadas" AS
 SELECT "u"."id_unidad",
    "u"."numero",
    "eu"."nombre" AS "estado",
    "c"."nombre" AS "condominio"
   FROM (("public"."unidad" "u"
     JOIN "public"."estado_unidad" "eu" ON (("eu"."id_estado" = "u"."id_estado")))
     JOIN "public"."condominio" "c" ON (("c"."id_condominio" = "u"."id_condominio")))
  WHERE (("eu"."nombre")::"text" = 'OCUPADA'::"text");


ALTER VIEW "public"."vw_unidades_ocupadas" OWNER TO "postgres";


CREATE OR REPLACE VIEW "public"."vw_visitantes_dentro" AS
 SELECT "a"."id_acceso",
    "v"."nombre" AS "visitante",
    "u"."numero" AS "unidad",
    "a"."hora_ingreso"
   FROM ((("public"."acceso" "a"
     JOIN "public"."visitante" "v" ON (("v"."id_visitante" = "a"."id_visitante")))
     JOIN "public"."unidad" "u" ON (("u"."id_unidad" = "a"."id_unidad")))
     JOIN "public"."estado_acceso" "ea" ON (("ea"."id_estado" = "a"."id_estado")))
  WHERE (("ea"."nombre")::"text" = 'EN_CURSO'::"text");


ALTER VIEW "public"."vw_visitantes_dentro" OWNER TO "postgres";


ALTER TABLE ONLY "public"."acceso" ALTER COLUMN "id_acceso" SET DEFAULT "nextval"('"public"."acceso_id_acceso_seq"'::"regclass");



ALTER TABLE ONLY "public"."acta" ALTER COLUMN "id_acta" SET DEFAULT "nextval"('"public"."acta_id_acta_seq"'::"regclass");



ALTER TABLE ONLY "public"."archivo" ALTER COLUMN "id_archivo" SET DEFAULT "nextval"('"public"."archivo_id_archivo_seq"'::"regclass");



ALTER TABLE ONLY "public"."area_comun" ALTER COLUMN "id_area" SET DEFAULT "nextval"('"public"."area_comun_id_area_seq"'::"regclass");



ALTER TABLE ONLY "public"."asamblea" ALTER COLUMN "id_asamblea" SET DEFAULT "nextval"('"public"."asamblea_id_asamblea_seq"'::"regclass");



ALTER TABLE ONLY "public"."auditoria" ALTER COLUMN "id_auditoria" SET DEFAULT "nextval"('"public"."auditoria_id_auditoria_seq"'::"regclass");



ALTER TABLE ONLY "public"."categoria" ALTER COLUMN "id_categoria" SET DEFAULT "nextval"('"public"."categoria_id_categoria_seq"'::"regclass");



ALTER TABLE ONLY "public"."comunicado" ALTER COLUMN "id_comunicado" SET DEFAULT "nextval"('"public"."comunicado_id_comunicado_seq"'::"regclass");



ALTER TABLE ONLY "public"."condominio" ALTER COLUMN "id_condominio" SET DEFAULT "nextval"('"public"."condominio_id_condominio_seq"'::"regclass");



ALTER TABLE ONLY "public"."configuracion" ALTER COLUMN "id_configuracion" SET DEFAULT "nextval"('"public"."configuracion_id_configuracion_seq"'::"regclass");



ALTER TABLE ONLY "public"."convenio_pago" ALTER COLUMN "id_convenio" SET DEFAULT "nextval"('"public"."convenio_pago_id_convenio_seq"'::"regclass");



ALTER TABLE ONLY "public"."cuota" ALTER COLUMN "id_cuota" SET DEFAULT "nextval"('"public"."cuota_id_cuota_seq"'::"regclass");



ALTER TABLE ONLY "public"."estado_acceso" ALTER COLUMN "id_estado" SET DEFAULT "nextval"('"public"."estado_acceso_id_estado_seq"'::"regclass");



ALTER TABLE ONLY "public"."estado_pago" ALTER COLUMN "id_estado" SET DEFAULT "nextval"('"public"."estado_pago_id_estado_seq"'::"regclass");



ALTER TABLE ONLY "public"."estado_reserva" ALTER COLUMN "id_estado" SET DEFAULT "nextval"('"public"."estado_reserva_id_estado_seq"'::"regclass");



ALTER TABLE ONLY "public"."estado_ticket" ALTER COLUMN "id_estado" SET DEFAULT "nextval"('"public"."estado_ticket_id_estado_seq"'::"regclass");



ALTER TABLE ONLY "public"."estado_unidad" ALTER COLUMN "id_estado" SET DEFAULT "nextval"('"public"."estado_unidad_id_estado_seq"'::"regclass");



ALTER TABLE ONLY "public"."historial_ticket" ALTER COLUMN "id_historial" SET DEFAULT "nextval"('"public"."historial_ticket_id_historial_seq"'::"regclass");



ALTER TABLE ONLY "public"."login" ALTER COLUMN "id_login" SET DEFAULT "nextval"('"public"."login_id_login_seq"'::"regclass");



ALTER TABLE ONLY "public"."multa" ALTER COLUMN "id_multa" SET DEFAULT "nextval"('"public"."multa_id_multa_seq"'::"regclass");



ALTER TABLE ONLY "public"."notificacion" ALTER COLUMN "id_notificacion" SET DEFAULT "nextval"('"public"."notificacion_id_notificacion_seq"'::"regclass");



ALTER TABLE ONLY "public"."pago" ALTER COLUMN "id_pago" SET DEFAULT "nextval"('"public"."pago_id_pago_seq"'::"regclass");



ALTER TABLE ONLY "public"."parqueadero" ALTER COLUMN "id_parqueadero" SET DEFAULT "nextval"('"public"."parqueadero_id_parqueadero_seq"'::"regclass");



ALTER TABLE ONLY "public"."permiso" ALTER COLUMN "id_permiso" SET DEFAULT "nextval"('"public"."permiso_id_permiso_seq"'::"regclass");



ALTER TABLE ONLY "public"."persona" ALTER COLUMN "id_persona" SET DEFAULT "nextval"('"public"."persona_id_persona_seq"'::"regclass");



ALTER TABLE ONLY "public"."persona_unidad" ALTER COLUMN "id_persona_unidad" SET DEFAULT "nextval"('"public"."persona_unidad_id_persona_unidad_seq"'::"regclass");



ALTER TABLE ONLY "public"."recibo" ALTER COLUMN "id_recibo" SET DEFAULT "nextval"('"public"."recibo_id_recibo_seq"'::"regclass");



ALTER TABLE ONLY "public"."refresh_token" ALTER COLUMN "id_refresh_token" SET DEFAULT "nextval"('"public"."refresh_token_id_refresh_token_seq"'::"regclass");



ALTER TABLE ONLY "public"."reserva" ALTER COLUMN "id_reserva" SET DEFAULT "nextval"('"public"."reserva_id_reserva_seq"'::"regclass");



ALTER TABLE ONLY "public"."rol" ALTER COLUMN "id_rol" SET DEFAULT "nextval"('"public"."rol_id_rol_seq"'::"regclass");



ALTER TABLE ONLY "public"."ticket" ALTER COLUMN "id_ticket" SET DEFAULT "nextval"('"public"."ticket_id_ticket_seq"'::"regclass");



ALTER TABLE ONLY "public"."ticket_comentario" ALTER COLUMN "id_comentario" SET DEFAULT "nextval"('"public"."ticket_comentario_id_comentario_seq"'::"regclass");



ALTER TABLE ONLY "public"."torre" ALTER COLUMN "id_torre" SET DEFAULT "nextval"('"public"."torre_id_torre_seq"'::"regclass");



ALTER TABLE ONLY "public"."unidad" ALTER COLUMN "id_unidad" SET DEFAULT "nextval"('"public"."unidad_id_unidad_seq"'::"regclass");



ALTER TABLE ONLY "public"."usuario" ALTER COLUMN "id_usuario" SET DEFAULT "nextval"('"public"."usuario_id_usuario_seq"'::"regclass");



ALTER TABLE ONLY "public"."vehiculo" ALTER COLUMN "id_vehiculo" SET DEFAULT "nextval"('"public"."vehiculo_id_vehiculo_seq"'::"regclass");



ALTER TABLE ONLY "public"."visitante" ALTER COLUMN "id_visitante" SET DEFAULT "nextval"('"public"."visitante_id_visitante_seq"'::"regclass");



ALTER TABLE ONLY "public"."visitante_preautorizado" ALTER COLUMN "id_preautorizacion" SET DEFAULT "nextval"('"public"."visitante_preautorizado_id_preautorizacion_seq"'::"regclass");



ALTER TABLE ONLY "public"."votacion" ALTER COLUMN "id_votacion" SET DEFAULT "nextval"('"public"."votacion_id_votacion_seq"'::"regclass");



ALTER TABLE ONLY "public"."acceso"
    ADD CONSTRAINT "acceso_pkey" PRIMARY KEY ("id_acceso");



ALTER TABLE ONLY "public"."acta_archivo"
    ADD CONSTRAINT "acta_archivo_pkey" PRIMARY KEY ("id_acta", "id_archivo");



ALTER TABLE ONLY "public"."acta"
    ADD CONSTRAINT "acta_id_asamblea_key" UNIQUE ("id_asamblea");



ALTER TABLE ONLY "public"."acta"
    ADD CONSTRAINT "acta_pkey" PRIMARY KEY ("id_acta");



ALTER TABLE ONLY "public"."archivo"
    ADD CONSTRAINT "archivo_pkey" PRIMARY KEY ("id_archivo");



ALTER TABLE ONLY "public"."area_comun"
    ADD CONSTRAINT "area_comun_pkey" PRIMARY KEY ("id_area");



ALTER TABLE ONLY "public"."asamblea"
    ADD CONSTRAINT "asamblea_pkey" PRIMARY KEY ("id_asamblea");



ALTER TABLE ONLY "public"."auditoria"
    ADD CONSTRAINT "auditoria_pkey" PRIMARY KEY ("id_auditoria");



ALTER TABLE ONLY "public"."categoria"
    ADD CONSTRAINT "categoria_nombre_key" UNIQUE ("nombre");



ALTER TABLE ONLY "public"."categoria"
    ADD CONSTRAINT "categoria_pkey" PRIMARY KEY ("id_categoria");



ALTER TABLE ONLY "public"."comunicado_lectura"
    ADD CONSTRAINT "comunicado_lectura_pkey" PRIMARY KEY ("id_comunicado", "id_persona");



ALTER TABLE ONLY "public"."comunicado"
    ADD CONSTRAINT "comunicado_pkey" PRIMARY KEY ("id_comunicado");



ALTER TABLE ONLY "public"."condominio"
    ADD CONSTRAINT "condominio_pkey" PRIMARY KEY ("id_condominio");



ALTER TABLE ONLY "public"."configuracion"
    ADD CONSTRAINT "configuracion_clave_key" UNIQUE ("clave");



ALTER TABLE ONLY "public"."configuracion"
    ADD CONSTRAINT "configuracion_pkey" PRIMARY KEY ("id_configuracion");



ALTER TABLE ONLY "public"."convenio_pago"
    ADD CONSTRAINT "convenio_pago_pkey" PRIMARY KEY ("id_convenio");



ALTER TABLE ONLY "public"."cuota"
    ADD CONSTRAINT "cuota_pkey" PRIMARY KEY ("id_cuota");



ALTER TABLE ONLY "public"."estado_acceso"
    ADD CONSTRAINT "estado_acceso_nombre_key" UNIQUE ("nombre");



ALTER TABLE ONLY "public"."estado_acceso"
    ADD CONSTRAINT "estado_acceso_pkey" PRIMARY KEY ("id_estado");



ALTER TABLE ONLY "public"."estado_pago"
    ADD CONSTRAINT "estado_pago_nombre_key" UNIQUE ("nombre");



ALTER TABLE ONLY "public"."estado_pago"
    ADD CONSTRAINT "estado_pago_pkey" PRIMARY KEY ("id_estado");



ALTER TABLE ONLY "public"."estado_reserva"
    ADD CONSTRAINT "estado_reserva_nombre_key" UNIQUE ("nombre");



ALTER TABLE ONLY "public"."estado_reserva"
    ADD CONSTRAINT "estado_reserva_pkey" PRIMARY KEY ("id_estado");



ALTER TABLE ONLY "public"."estado_ticket"
    ADD CONSTRAINT "estado_ticket_nombre_key" UNIQUE ("nombre");



ALTER TABLE ONLY "public"."estado_ticket"
    ADD CONSTRAINT "estado_ticket_pkey" PRIMARY KEY ("id_estado");



ALTER TABLE ONLY "public"."estado_unidad"
    ADD CONSTRAINT "estado_unidad_nombre_key" UNIQUE ("nombre");



ALTER TABLE ONLY "public"."estado_unidad"
    ADD CONSTRAINT "estado_unidad_pkey" PRIMARY KEY ("id_estado");



ALTER TABLE ONLY "public"."flyway_schema_history"
    ADD CONSTRAINT "flyway_schema_history_pk" PRIMARY KEY ("installed_rank");



ALTER TABLE ONLY "public"."historial_ticket"
    ADD CONSTRAINT "historial_ticket_pkey" PRIMARY KEY ("id_historial");



ALTER TABLE ONLY "public"."login"
    ADD CONSTRAINT "login_pkey" PRIMARY KEY ("id_login");



ALTER TABLE ONLY "public"."multa"
    ADD CONSTRAINT "multa_id_cuota_key" UNIQUE ("id_cuota");



ALTER TABLE ONLY "public"."multa"
    ADD CONSTRAINT "multa_pkey" PRIMARY KEY ("id_multa");



ALTER TABLE ONLY "public"."notificacion"
    ADD CONSTRAINT "notificacion_pkey" PRIMARY KEY ("id_notificacion");



ALTER TABLE ONLY "public"."pago"
    ADD CONSTRAINT "pago_pkey" PRIMARY KEY ("id_pago");



ALTER TABLE ONLY "public"."parqueadero"
    ADD CONSTRAINT "parqueadero_pkey" PRIMARY KEY ("id_parqueadero");



ALTER TABLE ONLY "public"."permiso"
    ADD CONSTRAINT "permiso_modulo_accion_key" UNIQUE ("modulo", "accion");



ALTER TABLE ONLY "public"."permiso"
    ADD CONSTRAINT "permiso_pkey" PRIMARY KEY ("id_permiso");



ALTER TABLE ONLY "public"."persona"
    ADD CONSTRAINT "persona_correo_key" UNIQUE ("correo");



ALTER TABLE ONLY "public"."persona"
    ADD CONSTRAINT "persona_pkey" PRIMARY KEY ("id_persona");



ALTER TABLE ONLY "public"."persona"
    ADD CONSTRAINT "persona_tipo_identificacion_numero_identificacion_key" UNIQUE ("tipo_identificacion", "numero_identificacion");



ALTER TABLE ONLY "public"."persona_unidad"
    ADD CONSTRAINT "persona_unidad_pkey" PRIMARY KEY ("id_persona_unidad");



ALTER TABLE ONLY "public"."recibo"
    ADD CONSTRAINT "recibo_id_pago_key" UNIQUE ("id_pago");



ALTER TABLE ONLY "public"."recibo"
    ADD CONSTRAINT "recibo_numero_key" UNIQUE ("numero");



ALTER TABLE ONLY "public"."recibo"
    ADD CONSTRAINT "recibo_pkey" PRIMARY KEY ("id_recibo");



ALTER TABLE ONLY "public"."refresh_token"
    ADD CONSTRAINT "refresh_token_pkey" PRIMARY KEY ("id_refresh_token");



ALTER TABLE ONLY "public"."refresh_token"
    ADD CONSTRAINT "refresh_token_token_key" UNIQUE ("token");



ALTER TABLE ONLY "public"."reserva"
    ADD CONSTRAINT "reserva_no_solape" EXCLUDE USING "gist" ("id_area" WITH =, "periodo" WITH &&) WHERE ("bloquea_horario");



ALTER TABLE ONLY "public"."reserva"
    ADD CONSTRAINT "reserva_pkey" PRIMARY KEY ("id_reserva");



ALTER TABLE ONLY "public"."rol"
    ADD CONSTRAINT "rol_nombre_key" UNIQUE ("nombre");



ALTER TABLE ONLY "public"."rol_permiso"
    ADD CONSTRAINT "rol_permiso_pkey" PRIMARY KEY ("id_rol", "id_permiso");



ALTER TABLE ONLY "public"."rol"
    ADD CONSTRAINT "rol_pkey" PRIMARY KEY ("id_rol");



ALTER TABLE ONLY "public"."ticket_archivo"
    ADD CONSTRAINT "ticket_archivo_pkey" PRIMARY KEY ("id_ticket", "id_archivo");



ALTER TABLE ONLY "public"."ticket_comentario"
    ADD CONSTRAINT "ticket_comentario_pkey" PRIMARY KEY ("id_comentario");



ALTER TABLE ONLY "public"."ticket"
    ADD CONSTRAINT "ticket_pkey" PRIMARY KEY ("id_ticket");



ALTER TABLE ONLY "public"."torre"
    ADD CONSTRAINT "torre_pkey" PRIMARY KEY ("id_torre");



ALTER TABLE ONLY "public"."unidad"
    ADD CONSTRAINT "unidad_id_condominio_numero_key" UNIQUE ("id_condominio", "numero");



ALTER TABLE ONLY "public"."unidad"
    ADD CONSTRAINT "unidad_pkey" PRIMARY KEY ("id_unidad");



ALTER TABLE ONLY "public"."area_comun"
    ADD CONSTRAINT "uq_area_condominio_nombre" UNIQUE ("id_condominio", "nombre");



ALTER TABLE ONLY "public"."cuota"
    ADD CONSTRAINT "uq_cuota_unidad_periodo_tipo" UNIQUE ("id_unidad", "mes", "anio", "tipo");



ALTER TABLE ONLY "public"."parqueadero"
    ADD CONSTRAINT "uq_parqueadero_unidad_numero" UNIQUE ("id_unidad", "numero");



ALTER TABLE ONLY "public"."torre"
    ADD CONSTRAINT "uq_torre_condominio_nombre" UNIQUE ("id_condominio", "nombre");



ALTER TABLE ONLY "public"."usuario"
    ADD CONSTRAINT "usuario_id_persona_key" UNIQUE ("id_persona");



ALTER TABLE ONLY "public"."usuario"
    ADD CONSTRAINT "usuario_pkey" PRIMARY KEY ("id_usuario");



ALTER TABLE ONLY "public"."usuario_rol"
    ADD CONSTRAINT "usuario_rol_pkey" PRIMARY KEY ("id_usuario", "id_rol");



ALTER TABLE ONLY "public"."usuario"
    ADD CONSTRAINT "usuario_username_key" UNIQUE ("username");



ALTER TABLE ONLY "public"."vehiculo"
    ADD CONSTRAINT "vehiculo_pkey" PRIMARY KEY ("id_vehiculo");



ALTER TABLE ONLY "public"."visitante"
    ADD CONSTRAINT "visitante_pkey" PRIMARY KEY ("id_visitante");



ALTER TABLE ONLY "public"."visitante_preautorizado"
    ADD CONSTRAINT "visitante_preautorizado_pkey" PRIMARY KEY ("id_preautorizacion");



ALTER TABLE ONLY "public"."votacion"
    ADD CONSTRAINT "votacion_id_asamblea_id_persona_key" UNIQUE ("id_asamblea", "id_persona");



ALTER TABLE ONLY "public"."votacion"
    ADD CONSTRAINT "votacion_pkey" PRIMARY KEY ("id_votacion");



CREATE INDEX "flyway_schema_history_s_idx" ON "public"."flyway_schema_history" USING "btree" ("success");



CREATE INDEX "idx_acceso_hora_ingreso" ON "public"."acceso" USING "btree" ("hora_ingreso");



CREATE INDEX "idx_acceso_unidad" ON "public"."acceso" USING "btree" ("id_unidad");



CREATE INDEX "idx_auditoria_tabla_registro" ON "public"."auditoria" USING "btree" ("tabla_afectada", "id_registro");



CREATE INDEX "idx_cuota_estado" ON "public"."cuota" USING "btree" ("estado");



CREATE INDEX "idx_cuota_unidad_periodo" ON "public"."cuota" USING "btree" ("id_unidad", "anio", "mes");



CREATE INDEX "idx_historial_ticket" ON "public"."historial_ticket" USING "btree" ("id_ticket");



CREATE INDEX "idx_login_usuario_fecha" ON "public"."login" USING "btree" ("id_usuario", "fecha");



CREATE INDEX "idx_multa_unidad" ON "public"."multa" USING "btree" ("id_unidad");



CREATE INDEX "idx_notificacion_persona" ON "public"."notificacion" USING "btree" ("id_persona", "leido");



CREATE INDEX "idx_pago_fecha" ON "public"."pago" USING "btree" ("fecha");



CREATE INDEX "idx_persona_identificacion" ON "public"."persona" USING "btree" ("numero_identificacion");



CREATE INDEX "idx_persona_unidad_persona" ON "public"."persona_unidad" USING "btree" ("id_persona");



CREATE INDEX "idx_persona_unidad_unidad" ON "public"."persona_unidad" USING "btree" ("id_unidad");



CREATE INDEX "idx_reserva_fecha" ON "public"."reserva" USING "btree" ("fecha");



CREATE INDEX "idx_ticket_persona" ON "public"."ticket" USING "btree" ("id_persona");



CREATE INDEX "idx_ticket_unidad" ON "public"."ticket" USING "btree" ("id_unidad");



CREATE INDEX "idx_usuario_username" ON "public"."usuario" USING "btree" ("username");



CREATE INDEX "idx_vehiculo_placa_lookup" ON "public"."vehiculo" USING "btree" ("placa");



CREATE UNIQUE INDEX "uq_personaunidad_titular_activo" ON "public"."persona_unidad" USING "btree" ("id_unidad", "tipo") WHERE (("estado" = 'ACTIVO'::"public"."estado_persona_unidad_enum") AND ("tipo" = ANY (ARRAY['PROPIETARIO'::"public"."tipo_persona_unidad_enum", 'ARRENDATARIO'::"public"."tipo_persona_unidad_enum"])));



CREATE UNIQUE INDEX "uq_vehiculo_placa" ON "public"."vehiculo" USING "btree" ("placa") WHERE ("placa" IS NOT NULL);



CREATE OR REPLACE TRIGGER "trg_auditoria_cuota" AFTER INSERT OR DELETE OR UPDATE ON "public"."cuota" FOR EACH ROW EXECUTE FUNCTION "public"."fn_auditoria"();



CREATE OR REPLACE TRIGGER "trg_auditoria_multa" AFTER INSERT OR DELETE OR UPDATE ON "public"."multa" FOR EACH ROW EXECUTE FUNCTION "public"."fn_auditoria"();



CREATE OR REPLACE TRIGGER "trg_auditoria_pago" AFTER INSERT OR DELETE OR UPDATE ON "public"."pago" FOR EACH ROW EXECUTE FUNCTION "public"."fn_auditoria"();



CREATE OR REPLACE TRIGGER "trg_auditoria_persona_unidad" AFTER INSERT OR DELETE OR UPDATE ON "public"."persona_unidad" FOR EACH ROW EXECUTE FUNCTION "public"."fn_auditoria"();



CREATE OR REPLACE TRIGGER "trg_auditoria_unidad" AFTER INSERT OR DELETE OR UPDATE ON "public"."unidad" FOR EACH ROW EXECUTE FUNCTION "public"."fn_auditoria"();



CREATE OR REPLACE TRIGGER "trg_reserva_bloqueo" BEFORE INSERT OR UPDATE OF "id_estado" ON "public"."reserva" FOR EACH ROW EXECUTE FUNCTION "public"."fn_reserva_bloqueo"();



CREATE OR REPLACE TRIGGER "trg_sync_estado_ticket" AFTER INSERT ON "public"."historial_ticket" FOR EACH ROW EXECUTE FUNCTION "public"."fn_sync_estado_actual_ticket"();



CREATE OR REPLACE TRIGGER "trg_unidad_torre_condominio" BEFORE INSERT OR UPDATE ON "public"."unidad" FOR EACH ROW EXECUTE FUNCTION "public"."fn_chk_unidad_torre_condominio"();



ALTER TABLE ONLY "public"."acceso"
    ADD CONSTRAINT "acceso_id_estado_fkey" FOREIGN KEY ("id_estado") REFERENCES "public"."estado_acceso"("id_estado");



ALTER TABLE ONLY "public"."acceso"
    ADD CONSTRAINT "acceso_id_guardia_fkey" FOREIGN KEY ("id_guardia") REFERENCES "public"."persona"("id_persona") ON DELETE RESTRICT;



ALTER TABLE ONLY "public"."acceso"
    ADD CONSTRAINT "acceso_id_preautorizacion_fkey" FOREIGN KEY ("id_preautorizacion") REFERENCES "public"."visitante_preautorizado"("id_preautorizacion") ON DELETE SET NULL;



ALTER TABLE ONLY "public"."acceso"
    ADD CONSTRAINT "acceso_id_unidad_fkey" FOREIGN KEY ("id_unidad") REFERENCES "public"."unidad"("id_unidad") ON DELETE RESTRICT;



ALTER TABLE ONLY "public"."acceso"
    ADD CONSTRAINT "acceso_id_vehiculo_fkey" FOREIGN KEY ("id_vehiculo") REFERENCES "public"."vehiculo"("id_vehiculo") ON DELETE SET NULL;



ALTER TABLE ONLY "public"."acceso"
    ADD CONSTRAINT "acceso_id_visitante_fkey" FOREIGN KEY ("id_visitante") REFERENCES "public"."visitante"("id_visitante") ON DELETE RESTRICT;



ALTER TABLE ONLY "public"."acta_archivo"
    ADD CONSTRAINT "acta_archivo_id_acta_fkey" FOREIGN KEY ("id_acta") REFERENCES "public"."acta"("id_acta") ON DELETE CASCADE;



ALTER TABLE ONLY "public"."acta_archivo"
    ADD CONSTRAINT "acta_archivo_id_archivo_fkey" FOREIGN KEY ("id_archivo") REFERENCES "public"."archivo"("id_archivo") ON DELETE CASCADE;



ALTER TABLE ONLY "public"."acta"
    ADD CONSTRAINT "acta_id_asamblea_fkey" FOREIGN KEY ("id_asamblea") REFERENCES "public"."asamblea"("id_asamblea") ON DELETE CASCADE;



ALTER TABLE ONLY "public"."area_comun"
    ADD CONSTRAINT "area_comun_id_condominio_fkey" FOREIGN KEY ("id_condominio") REFERENCES "public"."condominio"("id_condominio") ON DELETE CASCADE;



ALTER TABLE ONLY "public"."asamblea"
    ADD CONSTRAINT "asamblea_id_condominio_fkey" FOREIGN KEY ("id_condominio") REFERENCES "public"."condominio"("id_condominio") ON DELETE CASCADE;



ALTER TABLE ONLY "public"."auditoria"
    ADD CONSTRAINT "auditoria_id_usuario_fkey" FOREIGN KEY ("id_usuario") REFERENCES "public"."usuario"("id_usuario") ON DELETE SET NULL;



ALTER TABLE ONLY "public"."comunicado"
    ADD CONSTRAINT "comunicado_id_autor_fkey" FOREIGN KEY ("id_autor") REFERENCES "public"."persona"("id_persona") ON DELETE RESTRICT;



ALTER TABLE ONLY "public"."comunicado_lectura"
    ADD CONSTRAINT "comunicado_lectura_id_comunicado_fkey" FOREIGN KEY ("id_comunicado") REFERENCES "public"."comunicado"("id_comunicado") ON DELETE CASCADE;



ALTER TABLE ONLY "public"."comunicado_lectura"
    ADD CONSTRAINT "comunicado_lectura_id_persona_fkey" FOREIGN KEY ("id_persona") REFERENCES "public"."persona"("id_persona") ON DELETE CASCADE;



ALTER TABLE ONLY "public"."convenio_pago"
    ADD CONSTRAINT "convenio_pago_id_persona_fkey" FOREIGN KEY ("id_persona") REFERENCES "public"."persona"("id_persona") ON DELETE RESTRICT;



ALTER TABLE ONLY "public"."convenio_pago"
    ADD CONSTRAINT "convenio_pago_id_unidad_fkey" FOREIGN KEY ("id_unidad") REFERENCES "public"."unidad"("id_unidad") ON DELETE RESTRICT;



ALTER TABLE ONLY "public"."cuota"
    ADD CONSTRAINT "cuota_id_unidad_fkey" FOREIGN KEY ("id_unidad") REFERENCES "public"."unidad"("id_unidad") ON DELETE RESTRICT;



ALTER TABLE ONLY "public"."historial_ticket"
    ADD CONSTRAINT "historial_ticket_id_estado_fkey" FOREIGN KEY ("id_estado") REFERENCES "public"."estado_ticket"("id_estado");



ALTER TABLE ONLY "public"."historial_ticket"
    ADD CONSTRAINT "historial_ticket_id_ticket_fkey" FOREIGN KEY ("id_ticket") REFERENCES "public"."ticket"("id_ticket") ON DELETE CASCADE;



ALTER TABLE ONLY "public"."historial_ticket"
    ADD CONSTRAINT "historial_ticket_id_usuario_fkey" FOREIGN KEY ("id_usuario") REFERENCES "public"."usuario"("id_usuario") ON DELETE RESTRICT;



ALTER TABLE ONLY "public"."login"
    ADD CONSTRAINT "login_id_usuario_fkey" FOREIGN KEY ("id_usuario") REFERENCES "public"."usuario"("id_usuario") ON DELETE CASCADE;



ALTER TABLE ONLY "public"."multa"
    ADD CONSTRAINT "multa_id_cuota_fkey" FOREIGN KEY ("id_cuota") REFERENCES "public"."cuota"("id_cuota") ON DELETE SET NULL;



ALTER TABLE ONLY "public"."multa"
    ADD CONSTRAINT "multa_id_persona_fkey" FOREIGN KEY ("id_persona") REFERENCES "public"."persona"("id_persona") ON DELETE RESTRICT;



ALTER TABLE ONLY "public"."multa"
    ADD CONSTRAINT "multa_id_unidad_fkey" FOREIGN KEY ("id_unidad") REFERENCES "public"."unidad"("id_unidad") ON DELETE RESTRICT;



ALTER TABLE ONLY "public"."notificacion"
    ADD CONSTRAINT "notificacion_id_persona_fkey" FOREIGN KEY ("id_persona") REFERENCES "public"."persona"("id_persona") ON DELETE CASCADE;



ALTER TABLE ONLY "public"."pago"
    ADD CONSTRAINT "pago_id_cuota_fkey" FOREIGN KEY ("id_cuota") REFERENCES "public"."cuota"("id_cuota") ON DELETE RESTRICT;



ALTER TABLE ONLY "public"."pago"
    ADD CONSTRAINT "pago_id_estado_fkey" FOREIGN KEY ("id_estado") REFERENCES "public"."estado_pago"("id_estado");



ALTER TABLE ONLY "public"."parqueadero"
    ADD CONSTRAINT "parqueadero_id_unidad_fkey" FOREIGN KEY ("id_unidad") REFERENCES "public"."unidad"("id_unidad") ON DELETE CASCADE;



ALTER TABLE ONLY "public"."persona_unidad"
    ADD CONSTRAINT "persona_unidad_id_persona_fkey" FOREIGN KEY ("id_persona") REFERENCES "public"."persona"("id_persona") ON DELETE CASCADE;



ALTER TABLE ONLY "public"."persona_unidad"
    ADD CONSTRAINT "persona_unidad_id_unidad_fkey" FOREIGN KEY ("id_unidad") REFERENCES "public"."unidad"("id_unidad") ON DELETE CASCADE;



ALTER TABLE ONLY "public"."recibo"
    ADD CONSTRAINT "recibo_id_archivo_fkey" FOREIGN KEY ("id_archivo") REFERENCES "public"."archivo"("id_archivo") ON DELETE SET NULL;



ALTER TABLE ONLY "public"."recibo"
    ADD CONSTRAINT "recibo_id_pago_fkey" FOREIGN KEY ("id_pago") REFERENCES "public"."pago"("id_pago") ON DELETE RESTRICT;



ALTER TABLE ONLY "public"."refresh_token"
    ADD CONSTRAINT "refresh_token_id_usuario_fkey" FOREIGN KEY ("id_usuario") REFERENCES "public"."usuario"("id_usuario") ON DELETE CASCADE;



ALTER TABLE ONLY "public"."reserva"
    ADD CONSTRAINT "reserva_id_area_fkey" FOREIGN KEY ("id_area") REFERENCES "public"."area_comun"("id_area") ON DELETE CASCADE;



ALTER TABLE ONLY "public"."reserva"
    ADD CONSTRAINT "reserva_id_estado_fkey" FOREIGN KEY ("id_estado") REFERENCES "public"."estado_reserva"("id_estado");



ALTER TABLE ONLY "public"."reserva"
    ADD CONSTRAINT "reserva_id_persona_fkey" FOREIGN KEY ("id_persona") REFERENCES "public"."persona"("id_persona") ON DELETE RESTRICT;



ALTER TABLE ONLY "public"."reserva"
    ADD CONSTRAINT "reserva_id_usuario_aprobador_fkey" FOREIGN KEY ("id_usuario_aprobador") REFERENCES "public"."usuario"("id_usuario") ON DELETE SET NULL;



ALTER TABLE ONLY "public"."rol_permiso"
    ADD CONSTRAINT "rol_permiso_id_permiso_fkey" FOREIGN KEY ("id_permiso") REFERENCES "public"."permiso"("id_permiso") ON DELETE CASCADE;



ALTER TABLE ONLY "public"."rol_permiso"
    ADD CONSTRAINT "rol_permiso_id_rol_fkey" FOREIGN KEY ("id_rol") REFERENCES "public"."rol"("id_rol") ON DELETE CASCADE;



ALTER TABLE ONLY "public"."ticket_archivo"
    ADD CONSTRAINT "ticket_archivo_id_archivo_fkey" FOREIGN KEY ("id_archivo") REFERENCES "public"."archivo"("id_archivo") ON DELETE CASCADE;



ALTER TABLE ONLY "public"."ticket_archivo"
    ADD CONSTRAINT "ticket_archivo_id_ticket_fkey" FOREIGN KEY ("id_ticket") REFERENCES "public"."ticket"("id_ticket") ON DELETE CASCADE;



ALTER TABLE ONLY "public"."ticket_comentario"
    ADD CONSTRAINT "ticket_comentario_id_persona_fkey" FOREIGN KEY ("id_persona") REFERENCES "public"."persona"("id_persona") ON DELETE RESTRICT;



ALTER TABLE ONLY "public"."ticket_comentario"
    ADD CONSTRAINT "ticket_comentario_id_ticket_fkey" FOREIGN KEY ("id_ticket") REFERENCES "public"."ticket"("id_ticket") ON DELETE CASCADE;



ALTER TABLE ONLY "public"."ticket"
    ADD CONSTRAINT "ticket_id_categoria_fkey" FOREIGN KEY ("id_categoria") REFERENCES "public"."categoria"("id_categoria") ON DELETE SET NULL;



ALTER TABLE ONLY "public"."ticket"
    ADD CONSTRAINT "ticket_id_estado_actual_fkey" FOREIGN KEY ("id_estado_actual") REFERENCES "public"."estado_ticket"("id_estado");



ALTER TABLE ONLY "public"."ticket"
    ADD CONSTRAINT "ticket_id_persona_fkey" FOREIGN KEY ("id_persona") REFERENCES "public"."persona"("id_persona") ON DELETE RESTRICT;



ALTER TABLE ONLY "public"."ticket"
    ADD CONSTRAINT "ticket_id_tecnico_fkey" FOREIGN KEY ("id_tecnico") REFERENCES "public"."persona"("id_persona") ON DELETE SET NULL;



ALTER TABLE ONLY "public"."ticket"
    ADD CONSTRAINT "ticket_id_unidad_fkey" FOREIGN KEY ("id_unidad") REFERENCES "public"."unidad"("id_unidad") ON DELETE RESTRICT;



ALTER TABLE ONLY "public"."torre"
    ADD CONSTRAINT "torre_id_condominio_fkey" FOREIGN KEY ("id_condominio") REFERENCES "public"."condominio"("id_condominio") ON DELETE CASCADE;



ALTER TABLE ONLY "public"."unidad"
    ADD CONSTRAINT "unidad_id_condominio_fkey" FOREIGN KEY ("id_condominio") REFERENCES "public"."condominio"("id_condominio") ON DELETE RESTRICT;



ALTER TABLE ONLY "public"."unidad"
    ADD CONSTRAINT "unidad_id_estado_fkey" FOREIGN KEY ("id_estado") REFERENCES "public"."estado_unidad"("id_estado");



ALTER TABLE ONLY "public"."unidad"
    ADD CONSTRAINT "unidad_id_torre_fkey" FOREIGN KEY ("id_torre") REFERENCES "public"."torre"("id_torre") ON DELETE RESTRICT;



ALTER TABLE ONLY "public"."usuario"
    ADD CONSTRAINT "usuario_id_persona_fkey" FOREIGN KEY ("id_persona") REFERENCES "public"."persona"("id_persona") ON DELETE CASCADE;



ALTER TABLE ONLY "public"."usuario_rol"
    ADD CONSTRAINT "usuario_rol_id_rol_fkey" FOREIGN KEY ("id_rol") REFERENCES "public"."rol"("id_rol") ON DELETE CASCADE;



ALTER TABLE ONLY "public"."usuario_rol"
    ADD CONSTRAINT "usuario_rol_id_usuario_fkey" FOREIGN KEY ("id_usuario") REFERENCES "public"."usuario"("id_usuario") ON DELETE CASCADE;



ALTER TABLE ONLY "public"."vehiculo"
    ADD CONSTRAINT "vehiculo_id_persona_actual_fkey" FOREIGN KEY ("id_persona_actual") REFERENCES "public"."persona"("id_persona") ON DELETE SET NULL;



ALTER TABLE ONLY "public"."vehiculo"
    ADD CONSTRAINT "vehiculo_id_unidad_fkey" FOREIGN KEY ("id_unidad") REFERENCES "public"."unidad"("id_unidad") ON DELETE CASCADE;



ALTER TABLE ONLY "public"."visitante_preautorizado"
    ADD CONSTRAINT "visitante_preautorizado_autorizado_por_fkey" FOREIGN KEY ("autorizado_por") REFERENCES "public"."persona"("id_persona") ON DELETE RESTRICT;



ALTER TABLE ONLY "public"."visitante_preautorizado"
    ADD CONSTRAINT "visitante_preautorizado_id_unidad_fkey" FOREIGN KEY ("id_unidad") REFERENCES "public"."unidad"("id_unidad") ON DELETE CASCADE;



ALTER TABLE ONLY "public"."visitante_preautorizado"
    ADD CONSTRAINT "visitante_preautorizado_id_visitante_fkey" FOREIGN KEY ("id_visitante") REFERENCES "public"."visitante"("id_visitante") ON DELETE CASCADE;



ALTER TABLE ONLY "public"."votacion"
    ADD CONSTRAINT "votacion_id_asamblea_fkey" FOREIGN KEY ("id_asamblea") REFERENCES "public"."asamblea"("id_asamblea") ON DELETE CASCADE;



ALTER TABLE ONLY "public"."votacion"
    ADD CONSTRAINT "votacion_id_persona_fkey" FOREIGN KEY ("id_persona") REFERENCES "public"."persona"("id_persona") ON DELETE RESTRICT;





ALTER PUBLICATION "supabase_realtime" OWNER TO "postgres";


REVOKE USAGE ON SCHEMA "public" FROM PUBLIC;
GRANT ALL ON SCHEMA "public" TO PUBLIC;




































































































































































































