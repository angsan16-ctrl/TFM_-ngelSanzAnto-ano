-- Ejecutar como administrador (por ejemplo root) DESPUÉS de sustituir CHANGE_ME.
-- No contiene ninguna contraseña real.

CREATE USER IF NOT EXISTS 'saf_app'@'127.0.0.1'
  IDENTIFIED BY 'CHANGE_ME';

GRANT SELECT, INSERT, DELETE
  ON `saf_biomass`.*
  TO 'saf_app'@'127.0.0.1';

FLUSH PRIVILEGES;

SHOW GRANTS FOR 'saf_app'@'127.0.0.1';
