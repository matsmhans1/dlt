from typing import Any

from dlt.common.exceptions import DltException
from dlt.common.data_types import TDataType
from dlt.common.schema.typing import (
    TSchemaContractDict,
    TSchemaContractEntities,
    TSchemaEvolutionMode,
)
from dlt.common.normalizers.naming import NamingConvention


class SchemaException(DltException):
    def __init__(self, schema_name: str, msg: str) -> None:
        self.schema_name = schema_name
        if schema_name:
            msg = f"In schema: {schema_name}: " + msg
        super().__init__(msg)


class InvalidSchemaName(ValueError, SchemaException):
    MAXIMUM_SCHEMA_NAME_LENGTH = 64

    def __init__(self, schema_name: str) -> None:
        self.name = schema_name
        super().__init__(
            schema_name,
            f"{schema_name} is an invalid schema/source name. The source or schema name must be a"
            " valid Python identifier ie. a snake case function name and have maximum"
            f" {self.MAXIMUM_SCHEMA_NAME_LENGTH} characters. Ideally should contain only small"
            " letters, numbers and underscores.",
        )


# TODO: does not look like a SchemaException
# class InvalidDatasetName(ValueError, SchemaException):
#     def __init__(self, destination_name: str) -> None:
#         self.destination_name = destination_name
#         super().__init__(
#             f"Destination {destination_name} does not accept empty datasets. Please pass the"
#             " dataset name to the destination configuration ie. via dlt pipeline."
#         )


class CannotCoerceColumnException(SchemaException):
    def __init__(
        self,
        schema_name: str,
        table_name: str,
        column_name: str,
        from_type: TDataType,
        to_type: TDataType,
        coerced_value: Any,
    ) -> None:
        self.table_name = table_name
        self.column_name = column_name
        self.from_type = from_type
        self.to_type = to_type
        self.coerced_value = coerced_value
        super().__init__(
            schema_name,
            f"Cannot coerce type in table {table_name} column {column_name} existing type"
            f" {from_type} coerced type {to_type} value: {coerced_value}",
        )


class TablePropertiesConflictException(SchemaException):
    def __init__(self, schema_name: str, table_name: str, prop_name: str, val1: str, val2: str):
        self.table_name = table_name
        self.prop_name = prop_name
        self.val1 = val1
        self.val2 = val2
        super().__init__(
            schema_name,
            f"Cannot merge partial tables for {table_name} due to property {prop_name}: {val1} !="
            f" {val2}",
        )


class ParentTableNotFoundException(SchemaException):
    def __init__(
        self, schema_name: str, table_name: str, parent_table_name: str, explanation: str = ""
    ) -> None:
        self.table_name = table_name
        self.parent_table_name = parent_table_name
        super().__init__(
            schema_name,
            f"Parent table {parent_table_name} for {table_name} was not found in the"
            f" schema.{explanation}",
        )


class CannotCoerceNullException(SchemaException):
    def __init__(self, schema_name: str, table_name: str, column_name: str) -> None:
        super().__init__(
            schema_name,
            f"Cannot coerce NULL in table {table_name} column {column_name} which is not nullable",
        )


class SchemaCorruptedException(SchemaException):
    pass


class SchemaEngineNoUpgradePathException(SchemaException):
    def __init__(
        self, schema_name: str, init_engine: int, from_engine: int, to_engine: int
    ) -> None:
        self.init_engine = init_engine
        self.from_engine = from_engine
        self.to_engine = to_engine
        super().__init__(
            schema_name,
            f"No engine upgrade path in schema {schema_name} from {init_engine} to {to_engine},"
            f" stopped at {from_engine}. You possibly tried to run an older dlt"
            " version against a destination you have previously loaded data to with a newer dlt"
            " version.",
        )


class DataValidationError(SchemaException):
    def __init__(
        self,
        schema_name: str,
        table_name: str,
        column_name: str,
        schema_entity: TSchemaContractEntities,
        contract_mode: TSchemaEvolutionMode,
        table_schema: Any,
        schema_contract: TSchemaContractDict,
        data_item: Any = None,
        extended_info: str = None,
    ) -> None:
        """Raised when `data_item` violates `contract_mode` on a `schema_entity` as defined by `table_schema`

        Schema, table and column names are given as a context and full `schema_contract` and causing `data_item` as an evidence.
        """
        msg = ""
        if schema_name:
            msg = f"Schema: {schema_name} "
        msg += f"Table: {table_name} "
        if column_name:
            msg += f"Column: {column_name}"
        msg = (
            "In "
            + msg
            + f" . Contract on {schema_entity} with mode {contract_mode} is violated. "
            + (extended_info or "")
        )
        super().__init__(schema_name, msg)
        self.table_name = table_name
        self.column_name = column_name

        # violated contract
        self.schema_entity = schema_entity
        self.contract_mode = contract_mode

        # some evidence
        self.table_schema = table_schema
        self.schema_contract = schema_contract
        self.data_item = data_item


class UnknownTableException(KeyError, SchemaException):
    def __init__(self, schema_name: str, table_name: str) -> None:
        self.table_name = table_name
        super().__init__(schema_name, f"Trying to access unknown table {table_name}.")


class TableIdentifiersFrozen(SchemaException):
    def __init__(
        self,
        schema_name: str,
        table_name: str,
        to_naming: NamingConvention,
        from_naming: NamingConvention,
        details: str,
    ) -> None:
        self.table_name = table_name
        self.to_naming = to_naming
        self.from_naming = from_naming
        msg = (
            f"Attempt to normalize identifiers for a table {table_name} from naming"
            f" {str(type(from_naming))} to {str(type(to_naming))} changed one or more identifiers. "
        )
        msg += (
            " This table already received data and tables were created at the destination. By"
            " default changing the identifiers is not allowed. "
        )
        msg += (
            " Such changes may result in creation of a new table or a new columns while the old"
            " columns with data will still be kept. "
        )
        msg += (
            " You may disable this behavior by setting"
            " schema.allow_identifier_change_on_table_with_data to True or removing `x-normalizer`"
            " hints from particular tables. "
        )
        msg += f" Details: {details}"
        super().__init__(schema_name, msg)


class ColumnNameConflictException(SchemaException):
    pass
