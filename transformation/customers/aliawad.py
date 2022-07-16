from pandas import DataFrame
from transformation.tsm_builder import TSMInterface

class AliAwadTransformer(TSMInterface):
    def __init__(self, config_yaml) -> None:
        super().__init__(config_yaml)

    def load_casesummary(self) -> DataFrame:
        return None
        
    def load_casetypes(self) -> DataFrame:
        return None

    def load_insurancemaster(self):
        return super().load_insurancemaster(full_file_path)