# Change Log

## v2.4.0 - 2024-04-16
### Added
 * Added Report Data table (Sai Pavan Kamma)
### Fixed
 * Add log level to `StreamHandler` (Michael Bentz)

## v2.3.1 - 2024-04-12
### Added
 * Add verbose support for `configure_logging` (Vaibhavi Deshpande)
 * Make `JobStatus` fields nullable and increase job summary data length (Michael Bentz)

## v2.3.0 - 2024-02-22
### Added
 * Add configure_logging (Michael Bentz)
 * Add ScriptHelper (Michael Bentz)

## v2.2.0 - 2023-12-13
### Added
 * Add eager loading support for `query_model` and deprecate `update_model` (Michael Bentz)

## v2.1.0 - 2023-12-11
### Changed
 * Return model on crud function calls (Michael Bentz)
### Fixed
 * Fix update_model function (Michael Bentz)
 

## v2.0.0 - 2023-12-06
### Changed
 * Remove `poetry.lock` (Michael Bentz)
 * __[Breaking Change]__ Refactor to use SQLModel (Michael Bentz)

## v1.1.0 - 2023-11-17
### Added
* Added DbClient

### Changed
* Renamed prevent_overwrite to get_unique_filename

## v0.1.0 - 2023-08-23
### Added
* Added send emails (Michael Bentz)
* Added prevent_overwrite (Michael Bentz)
