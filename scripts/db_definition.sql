-- Schema de la BD Postgres hecha hosteada en Neon

-- ─────────────────────────────────────────
-- TABLA: clientes
-- ─────────────────────────────────────────
CREATE TABLE clientes (
    id          SERIAL PRIMARY KEY,
    nombre      VARCHAR(100) NOT NULL,
    apellido    VARCHAR(100) NOT NULL,
    email       VARCHAR(150) UNIQUE,
    telefono    VARCHAR(20),
    direccion   TEXT,
    created_at  TIMESTAMP DEFAULT NOW(),
    updated_at  TIMESTAMP DEFAULT NOW()
);

-- ─────────────────────────────────────────
-- TABLA: productos
-- ─────────────────────────────────────────
CREATE TABLE productos (
    id               SERIAL PRIMARY KEY,
    nombre           VARCHAR(150) NOT NULL,
    descripcion      TEXT,
    precio_unitario  NUMERIC(10, 2) NOT NULL CHECK (precio_unitario >= 0),
    unidad_medida    VARCHAR(30) DEFAULT 'unidad',  -- unidad, kg, litro, etc.
    categoria        VARCHAR(80),
    created_at       TIMESTAMP DEFAULT NOW(),
    updated_at       TIMESTAMP DEFAULT NOW()
);

-- ─────────────────────────────────────────
-- TABLA: inventario (1 fila por producto)
-- ─────────────────────────────────────────
CREATE TABLE inventario (
    id            SERIAL PRIMARY KEY,
    producto_id   INT UNIQUE NOT NULL REFERENCES productos(id) ON DELETE CASCADE,
    stock_actual  NUMERIC(10, 2) NOT NULL DEFAULT 0 CHECK (stock_actual >= 0),
    stock_minimo  NUMERIC(10, 2) NOT NULL DEFAULT 0,
    stock_maximo  NUMERIC(10, 2),
    updated_at    TIMESTAMP DEFAULT NOW()
);

-- ─────────────────────────────────────────
-- TABLA: compras (entradas de mercadería)
-- ─────────────────────────────────────────
CREATE TABLE compras (
    id             SERIAL PRIMARY KEY,
    producto_id    INT NOT NULL REFERENCES productos(id) ON DELETE RESTRICT,
    proveedor      VARCHAR(150),
    cantidad       NUMERIC(10, 2) NOT NULL CHECK (cantidad > 0),
    precio_compra  NUMERIC(10, 2) NOT NULL CHECK (precio_compra >= 0),
    fecha_compra   DATE NOT NULL DEFAULT CURRENT_DATE,
    created_at     TIMESTAMP DEFAULT NOW()
);

-- ─────────────────────────────────────────
-- TABLA: ventas (cabecera)
-- ─────────────────────────────────────────
CREATE TABLE ventas (
    id           SERIAL PRIMARY KEY,
    cliente_id   INT REFERENCES clientes(id) ON DELETE SET NULL,
    total        NUMERIC(10, 2) NOT NULL DEFAULT 0,
    fecha_venta  DATE NOT NULL DEFAULT CURRENT_DATE,
    created_at   TIMESTAMP DEFAULT NOW()
);

-- ─────────────────────────────────────────
-- TABLA: detalle_ventas (líneas de la venta)
-- ─────────────────────────────────────────
CREATE TABLE detalle_ventas (
    id               SERIAL PRIMARY KEY,
    venta_id         INT NOT NULL REFERENCES ventas(id) ON DELETE CASCADE,
    producto_id      INT NOT NULL REFERENCES productos(id) ON DELETE RESTRICT,
    cantidad         NUMERIC(10, 2) NOT NULL CHECK (cantidad > 0),
    precio_unitario  NUMERIC(10, 2) NOT NULL,
    subtotal         NUMERIC(10, 2) GENERATED ALWAYS AS (cantidad * precio_unitario) STORED
);

-- ─────────────────────────────────────────
-- TRIGGER: actualizar inventario al comprar
-- ─────────────────────────────────────────
CREATE OR REPLACE FUNCTION fn_actualizar_stock_compra()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE inventario
    SET stock_actual = stock_actual + NEW.cantidad,
        updated_at   = NOW()
    WHERE producto_id = NEW.producto_id;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_stock_compra
AFTER INSERT ON compras
FOR EACH ROW EXECUTE FUNCTION fn_actualizar_stock_compra();

-- ─────────────────────────────────────────
-- TRIGGER: descontar inventario al vender
-- ─────────────────────────────────────────
CREATE OR REPLACE FUNCTION fn_actualizar_stock_venta()
RETURNS TRIGGER AS $$
BEGIN
    IF (SELECT stock_actual FROM inventario WHERE producto_id = NEW.producto_id) < NEW.cantidad THEN
        RAISE EXCEPTION 'Stock insuficiente para el producto %', NEW.producto_id;
    END IF;

    UPDATE inventario
    SET stock_actual = stock_actual - NEW.cantidad,
        updated_at   = NOW()
    WHERE producto_id = NEW.producto_id;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_stock_venta
AFTER INSERT ON detalle_ventas
FOR EACH ROW EXECUTE FUNCTION fn_actualizar_stock_venta();