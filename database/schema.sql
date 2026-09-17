-- TFM SAF - MySQL 8.x schema
-- Fuente de verdad de columnas: data/plantilla.xlsx
-- Los IDs existentes del Excel se insertan explícitamente; AUTO_INCREMENT queda para altas futuras.

CREATE DATABASE IF NOT EXISTS `saf_biomass`
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_0900_ai_ci;

USE `saf_biomass`;

CREATE TABLE IF NOT EXISTS `source` (
  `source_id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  `source_type` VARCHAR(32) NOT NULL,
  `title` VARCHAR(512) NOT NULL,
  `authors` VARCHAR(512) NULL,
  `journal_or_org` VARCHAR(255) NULL,
  `year` SMALLINT UNSIGNED NULL,
  `doi` VARCHAR(255) NULL,
  `url` VARCHAR(2048) NULL,
  `access_date` DATE NULL,
  `license_notes` VARCHAR(255) NULL,
  `peer_reviewed` VARCHAR(16) NULL,
  `evidence_quality` VARCHAR(32) NULL,
  `primary_or_secondary` VARCHAR(32) NULL,
  `notes` TEXT NULL,
  PRIMARY KEY (`source_id`),
  UNIQUE KEY `uq_source_doi` (`doi`),
  KEY `idx_source_year` (`year`),
  KEY `idx_source_type` (`source_type`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE IF NOT EXISTS `biomass` (
  `biomass_id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  `common_name` VARCHAR(255) NOT NULL,
  `scientific_name` VARCHAR(255) NULL,
  `species` VARCHAR(255) NULL,
  `genus` VARCHAR(255) NULL,
  `family` VARCHAR(255) NULL,
  `biomass_category` VARCHAR(64) NOT NULL,
  `residue_type` VARCHAR(64) NOT NULL,
  `plant_part` VARCHAR(64) NULL,
  `country` VARCHAR(128) NULL,
  `region` VARCHAR(255) NULL,
  `origin_notes` TEXT NULL,
  `description` TEXT NULL,
  `created_at` DATETIME NULL,
  PRIMARY KEY (`biomass_id`),
  KEY `idx_biomass_common_name` (`common_name`),
  KEY `idx_biomass_category` (`biomass_category`),
  KEY `idx_biomass_residue_type` (`residue_type`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE IF NOT EXISTS `biomass_composition` (
  `composition_id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  `biomass_id` BIGINT UNSIGNED NOT NULL,
  `source_id` BIGINT UNSIGNED NOT NULL,
  `sample_label` VARCHAR(255) NOT NULL,
  `measurement_basis` VARCHAR(64) NOT NULL,
  `analytical_method` VARCHAR(255) NULL,
  `cellulose_pct` DECIMAL(10,5) NULL,
  `hemicellulose_pct` DECIMAL(10,5) NULL,
  `lignin_total_pct` DECIMAL(10,5) NULL,
  `acid_insoluble_lignin_pct` DECIMAL(10,5) NULL,
  `acid_soluble_lignin_pct` DECIMAL(10,5) NULL,
  `glucan_pct` DECIMAL(10,5) NULL,
  `xylan_pct` DECIMAL(10,5) NULL,
  `arabinan_pct` DECIMAL(10,5) NULL,
  `mannan_pct` DECIMAL(10,5) NULL,
  `galactan_pct` DECIMAL(10,5) NULL,
  `extractives_pct` DECIMAL(10,5) NULL,
  `ash_pct` DECIMAL(10,5) NULL,
  `moisture_pct` DECIMAL(10,5) NULL,
  `protein_pct` DECIMAL(10,5) NULL,
  `lipids_pct` DECIMAL(10,5) NULL,
  `starch_pct` DECIMAL(10,5) NULL,
  `pectin_pct` DECIMAL(10,5) NULL,
  `volatile_matter_pct` DECIMAL(10,5) NULL,
  `fixed_carbon_pct` DECIMAL(10,5) NULL,
  `carbon_pct` DECIMAL(10,5) NULL,
  `hydrogen_pct` DECIMAL(10,5) NULL,
  `oxygen_pct` DECIMAL(10,5) NULL,
  `nitrogen_pct` DECIMAL(10,5) NULL,
  `sulfur_pct` DECIMAL(10,5) NULL,
  `chlorine_pct` DECIMAL(10,5) NULL,
  `hhv_value` DOUBLE NULL,
  `hhv_unit` VARCHAR(32) NULL,
  `lhv_value` DOUBLE NULL,
  `lhv_unit` VARCHAR(32) NULL,
  `uncertainty_text` TEXT NULL,
  `n_replicates` INT UNSIGNED NULL,
  `country` VARCHAR(128) NULL,
  `region` VARCHAR(255) NULL,
  `page_table_figure` VARCHAR(128) NULL,
  `notes` TEXT NULL,
  PRIMARY KEY (`composition_id`),
  KEY `idx_composition_biomass` (`biomass_id`),
  KEY `idx_composition_source` (`source_id`),
  KEY `idx_composition_biomass_source` (`biomass_id`, `source_id`),
  CONSTRAINT `fk_composition_biomass`
    FOREIGN KEY (`biomass_id`) REFERENCES `biomass` (`biomass_id`)
    ON UPDATE RESTRICT ON DELETE RESTRICT,
  CONSTRAINT `fk_composition_source`
    FOREIGN KEY (`source_id`) REFERENCES `source` (`source_id`)
    ON UPDATE RESTRICT ON DELETE RESTRICT,
  CONSTRAINT `chk_composition_cellulose` CHECK (`cellulose_pct` IS NULL OR `cellulose_pct` BETWEEN 0 AND 100),
  CONSTRAINT `chk_composition_hemicellulose` CHECK (`hemicellulose_pct` IS NULL OR `hemicellulose_pct` BETWEEN 0 AND 100),
  CONSTRAINT `chk_composition_lignin_total` CHECK (`lignin_total_pct` IS NULL OR `lignin_total_pct` BETWEEN 0 AND 100),
  CONSTRAINT `chk_composition_ail` CHECK (`acid_insoluble_lignin_pct` IS NULL OR `acid_insoluble_lignin_pct` BETWEEN 0 AND 100),
  CONSTRAINT `chk_composition_asl` CHECK (`acid_soluble_lignin_pct` IS NULL OR `acid_soluble_lignin_pct` BETWEEN 0 AND 100),
  CONSTRAINT `chk_composition_glucan` CHECK (`glucan_pct` IS NULL OR `glucan_pct` BETWEEN 0 AND 100),
  CONSTRAINT `chk_composition_xylan` CHECK (`xylan_pct` IS NULL OR `xylan_pct` BETWEEN 0 AND 100),
  CONSTRAINT `chk_composition_arabinan` CHECK (`arabinan_pct` IS NULL OR `arabinan_pct` BETWEEN 0 AND 100),
  CONSTRAINT `chk_composition_mannan` CHECK (`mannan_pct` IS NULL OR `mannan_pct` BETWEEN 0 AND 100),
  CONSTRAINT `chk_composition_galactan` CHECK (`galactan_pct` IS NULL OR `galactan_pct` BETWEEN 0 AND 100),
  CONSTRAINT `chk_composition_extractives` CHECK (`extractives_pct` IS NULL OR `extractives_pct` BETWEEN 0 AND 100),
  CONSTRAINT `chk_composition_ash` CHECK (`ash_pct` IS NULL OR `ash_pct` BETWEEN 0 AND 100),
  CONSTRAINT `chk_composition_moisture` CHECK (`moisture_pct` IS NULL OR `moisture_pct` BETWEEN 0 AND 100),
  CONSTRAINT `chk_composition_protein` CHECK (`protein_pct` IS NULL OR `protein_pct` BETWEEN 0 AND 100),
  CONSTRAINT `chk_composition_lipids` CHECK (`lipids_pct` IS NULL OR `lipids_pct` BETWEEN 0 AND 100),
  CONSTRAINT `chk_composition_starch` CHECK (`starch_pct` IS NULL OR `starch_pct` BETWEEN 0 AND 100),
  CONSTRAINT `chk_composition_pectin` CHECK (`pectin_pct` IS NULL OR `pectin_pct` BETWEEN 0 AND 100),
  CONSTRAINT `chk_composition_volatile` CHECK (`volatile_matter_pct` IS NULL OR `volatile_matter_pct` BETWEEN 0 AND 100),
  CONSTRAINT `chk_composition_fixed_carbon` CHECK (`fixed_carbon_pct` IS NULL OR `fixed_carbon_pct` BETWEEN 0 AND 100),
  CONSTRAINT `chk_composition_carbon` CHECK (`carbon_pct` IS NULL OR `carbon_pct` BETWEEN 0 AND 100),
  CONSTRAINT `chk_composition_hydrogen` CHECK (`hydrogen_pct` IS NULL OR `hydrogen_pct` BETWEEN 0 AND 100),
  CONSTRAINT `chk_composition_oxygen` CHECK (`oxygen_pct` IS NULL OR `oxygen_pct` BETWEEN 0 AND 100),
  CONSTRAINT `chk_composition_nitrogen` CHECK (`nitrogen_pct` IS NULL OR `nitrogen_pct` BETWEEN 0 AND 100),
  CONSTRAINT `chk_composition_sulfur` CHECK (`sulfur_pct` IS NULL OR `sulfur_pct` BETWEEN 0 AND 100),
  CONSTRAINT `chk_composition_chlorine` CHECK (`chlorine_pct` IS NULL OR `chlorine_pct` BETWEEN 0 AND 100),
  CONSTRAINT `chk_composition_n_replicates` CHECK (`n_replicates` IS NULL OR `n_replicates` > 0)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE IF NOT EXISTS `molecule` (
  `molecule_id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  `preferred_name` VARCHAR(255) NOT NULL,
  `synonyms` TEXT NULL,
  `canonical_smiles` VARCHAR(2048) NULL,
  `inchi` TEXT NULL,
  `inchikey` CHAR(27) NULL,
  `cas_number` VARCHAR(64) NULL,
  `molecular_formula` VARCHAR(128) NULL,
  `charge` INT NULL,
  `multiplicity` INT UNSIGNED NULL,
  `molecule_role` VARCHAR(64) NOT NULL,
  `renewable_origin` VARCHAR(128) NULL,
  `notes` TEXT NULL,
  PRIMARY KEY (`molecule_id`),
  UNIQUE KEY `uq_molecule_inchikey` (`inchikey`),
  KEY `idx_molecule_name` (`preferred_name`),
  KEY `idx_molecule_role` (`molecule_role`),
  CONSTRAINT `chk_molecule_multiplicity` CHECK (`multiplicity` IS NULL OR `multiplicity` >= 1)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE IF NOT EXISTS `biomass_molecule` (
  `biomass_molecule_id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  `biomass_id` BIGINT UNSIGNED NOT NULL,
  `molecule_id` BIGINT UNSIGNED NOT NULL,
  `source_id` BIGINT UNSIGNED NOT NULL,
  `fraction_origin` VARCHAR(64) NOT NULL,
  `conversion_process` VARCHAR(128) NOT NULL,
  `reported_yield` DOUBLE NULL,
  `yield_unit` VARCHAR(32) NULL,
  `temperature_c` DOUBLE NULL,
  `pressure_bar` DOUBLE NULL,
  `reaction_time_h` DOUBLE NULL,
  `evidence_level` VARCHAR(32) NULL,
  `page_table_figure` VARCHAR(128) NULL,
  `notes` TEXT NULL,
  PRIMARY KEY (`biomass_molecule_id`),
  KEY `idx_biomass_molecule_biomass` (`biomass_id`),
  KEY `idx_biomass_molecule_molecule` (`molecule_id`),
  KEY `idx_biomass_molecule_source` (`source_id`),
  KEY `idx_biomass_molecule_pair` (`biomass_id`, `molecule_id`),
  CONSTRAINT `fk_biomass_molecule_biomass`
    FOREIGN KEY (`biomass_id`) REFERENCES `biomass` (`biomass_id`)
    ON UPDATE RESTRICT ON DELETE RESTRICT,
  CONSTRAINT `fk_biomass_molecule_molecule`
    FOREIGN KEY (`molecule_id`) REFERENCES `molecule` (`molecule_id`)
    ON UPDATE RESTRICT ON DELETE RESTRICT,
  CONSTRAINT `fk_biomass_molecule_source`
    FOREIGN KEY (`source_id`) REFERENCES `source` (`source_id`)
    ON UPDATE RESTRICT ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE IF NOT EXISTS `reaction` (
  `reaction_id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  `source_id` BIGINT UNSIGNED NOT NULL,
  `reaction_name` VARCHAR(255) NOT NULL,
  `reaction_class` VARCHAR(128) NOT NULL,
  `temperature_c` DOUBLE NULL,
  `pressure_bar` DOUBLE NULL,
  `reaction_time_h` DOUBLE NULL,
  `catalyst_text` TEXT NULL,
  `solvent_text` TEXT NULL,
  `conversion_pct` DECIMAL(10,5) NULL,
  `selectivity_pct` DECIMAL(10,5) NULL,
  `yield_pct` DECIMAL(10,5) NULL,
  `yield_basis` VARCHAR(128) NULL,
  `h2_consumption` DOUBLE NULL,
  `h2_unit` VARCHAR(32) NULL,
  `trl` TINYINT UNSIGNED NULL,
  `reactor_type` VARCHAR(255) NULL,
  `page_table_figure` VARCHAR(128) NULL,
  `notes` TEXT NULL,
  PRIMARY KEY (`reaction_id`),
  KEY `idx_reaction_source` (`source_id`),
  KEY `idx_reaction_name` (`reaction_name`),
  KEY `idx_reaction_class` (`reaction_class`),
  CONSTRAINT `fk_reaction_source`
    FOREIGN KEY (`source_id`) REFERENCES `source` (`source_id`)
    ON UPDATE RESTRICT ON DELETE RESTRICT,
  CONSTRAINT `chk_reaction_conversion` CHECK (`conversion_pct` IS NULL OR `conversion_pct` BETWEEN 0 AND 100),
  CONSTRAINT `chk_reaction_selectivity` CHECK (`selectivity_pct` IS NULL OR `selectivity_pct` BETWEEN 0 AND 100),
  CONSTRAINT `chk_reaction_yield` CHECK (`yield_pct` IS NULL OR `yield_pct` BETWEEN 0 AND 100),
  CONSTRAINT `chk_reaction_trl` CHECK (`trl` IS NULL OR `trl` BETWEEN 1 AND 9)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE IF NOT EXISTS `reaction_participant` (
  `participant_id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  `reaction_id` BIGINT UNSIGNED NOT NULL,
  `molecule_id` BIGINT UNSIGNED NOT NULL,
  `participant_role` VARCHAR(32) NOT NULL,
  `stoichiometric_coefficient` DECIMAL(18,8) NULL,
  `notes` TEXT NULL,
  PRIMARY KEY (`participant_id`),
  KEY `idx_participant_reaction` (`reaction_id`),
  KEY `idx_participant_molecule` (`molecule_id`),
  KEY `idx_participant_role` (`participant_role`),
  KEY `idx_participant_reaction_molecule` (`reaction_id`, `molecule_id`),
  CONSTRAINT `fk_participant_reaction`
    FOREIGN KEY (`reaction_id`) REFERENCES `reaction` (`reaction_id`)
    ON UPDATE RESTRICT ON DELETE RESTRICT,
  CONSTRAINT `fk_participant_molecule`
    FOREIGN KEY (`molecule_id`) REFERENCES `molecule` (`molecule_id`)
    ON UPDATE RESTRICT ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE IF NOT EXISTS `fuel_property` (
  `fuel_property_id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  `molecule_id` BIGINT UNSIGNED NOT NULL,
  `source_id` BIGINT UNSIGNED NOT NULL,
  `property_name` VARCHAR(128) NOT NULL,
  `value` DOUBLE NOT NULL,
  `unit` VARCHAR(32) NULL,
  `temperature_c` DOUBLE NULL,
  `pressure_bar` DOUBLE NULL,
  `uncertainty` VARCHAR(255) NULL,
  `measurement_method` VARCHAR(255) NULL,
  `value_origin` VARCHAR(32) NOT NULL,
  `page_table_figure` VARCHAR(128) NULL,
  `notes` TEXT NULL,
  PRIMARY KEY (`fuel_property_id`),
  KEY `idx_fuel_property_molecule` (`molecule_id`),
  KEY `idx_fuel_property_source` (`source_id`),
  KEY `idx_fuel_property_name` (`property_name`),
  KEY `idx_fuel_property_molecule_name` (`molecule_id`, `property_name`),
  CONSTRAINT `fk_fuel_property_molecule`
    FOREIGN KEY (`molecule_id`) REFERENCES `molecule` (`molecule_id`)
    ON UPDATE RESTRICT ON DELETE RESTRICT,
  CONSTRAINT `fk_fuel_property_source`
    FOREIGN KEY (`source_id`) REFERENCES `source` (`source_id`)
    ON UPDATE RESTRICT ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE IF NOT EXISTS `molecular_descriptor` (
  `descriptor_id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  `molecule_id` BIGINT UNSIGNED NOT NULL,
  `descriptor_name` VARCHAR(255) NOT NULL,
  `descriptor_value` DOUBLE NOT NULL,
  `unit` VARCHAR(64) NULL,
  `software` VARCHAR(128) NULL,
  `software_version` VARCHAR(64) NULL,
  `calculation_date` DATE NULL,
  `config_hash` VARCHAR(128) NULL,
  `notes` TEXT NULL,
  PRIMARY KEY (`descriptor_id`),
  KEY `idx_descriptor_molecule` (`molecule_id`),
  KEY `idx_descriptor_name` (`descriptor_name`),
  KEY `idx_descriptor_molecule_name` (`molecule_id`, `descriptor_name`),
  CONSTRAINT `fk_descriptor_molecule`
    FOREIGN KEY (`molecule_id`) REFERENCES `molecule` (`molecule_id`)
    ON UPDATE RESTRICT ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE IF NOT EXISTS `quantum_calculation` (
  `calculation_id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  `molecule_id` BIGINT UNSIGNED NOT NULL,
  `conformer_id` BIGINT UNSIGNED NULL,
  `software` VARCHAR(128) NOT NULL,
  `software_version` VARCHAR(64) NULL,
  `method` VARCHAR(255) NULL,
  `basis_set` VARCHAR(255) NULL,
  `dispersion_correction` VARCHAR(128) NULL,
  `solvent_model` VARCHAR(128) NULL,
  `charge` INT NULL,
  `multiplicity` INT UNSIGNED NULL,
  `status` VARCHAR(32) NOT NULL,
  `started_at` DATETIME NULL,
  `finished_at` DATETIME NULL,
  `input_path` VARCHAR(1024) NULL,
  `output_path` VARCHAR(1024) NULL,
  `geometry_path` VARCHAR(1024) NULL,
  `file_hash` VARCHAR(128) NULL,
  `runtime_seconds` DOUBLE NULL,
  `hardware_notes` TEXT NULL,
  PRIMARY KEY (`calculation_id`),
  KEY `idx_quantum_calc_molecule` (`molecule_id`),
  KEY `idx_quantum_calc_status` (`status`),
  CONSTRAINT `fk_quantum_calc_molecule`
    FOREIGN KEY (`molecule_id`) REFERENCES `molecule` (`molecule_id`)
    ON UPDATE RESTRICT ON DELETE RESTRICT,
  CONSTRAINT `chk_quantum_calc_multiplicity` CHECK (`multiplicity` IS NULL OR `multiplicity` >= 1),
  CONSTRAINT `chk_quantum_calc_runtime` CHECK (`runtime_seconds` IS NULL OR `runtime_seconds` >= 0)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE IF NOT EXISTS `quantum_property` (
  `quantum_property_id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  `calculation_id` BIGINT UNSIGNED NOT NULL,
  `property_name` VARCHAR(255) NOT NULL,
  `value` DOUBLE NOT NULL,
  `unit` VARCHAR(64) NULL,
  `notes` TEXT NULL,
  PRIMARY KEY (`quantum_property_id`),
  KEY `idx_quantum_property_calculation` (`calculation_id`),
  KEY `idx_quantum_property_name` (`property_name`),
  KEY `idx_quantum_property_calc_name` (`calculation_id`, `property_name`),
  CONSTRAINT `fk_quantum_property_calculation`
    FOREIGN KEY (`calculation_id`) REFERENCES `quantum_calculation` (`calculation_id`)
    ON UPDATE RESTRICT ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
