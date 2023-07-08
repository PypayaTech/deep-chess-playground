from src.fcn.data_module_factory import FCNDataModuleFactory
from src.cnn.data_module_factory import CNNDataModuleFactory
from src.transformer.data_module_factory import TransformerDataModuleFactory


class DataModuleFactory:
    @staticmethod
    def create(config: dict[str, str]):
        data_module_type = config["type"]
        if data_module_type == "fcn":
            return FCNDataModuleFactory.create(config)
        elif data_module_type == "cnn":
            return CNNDataModuleFactory.create(config)
        elif data_module_type == "transformer":
            return TransformerDataModuleFactory.create(config)
