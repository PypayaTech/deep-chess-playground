from src.cnn.module_factory import CNNModuleFactory
from src.fcn.module_factory import FCNModuleFactory
from src.transformer.module_factory import TransformerModuleFactory


class PyTorchModuleFactory:
    @staticmethod
    def create(config: dict[str, str]):
        model_architecture = config["architecture"]
        if model_architecture == "fcn":
            return FCNModuleFactory.create(config)
        elif model_architecture == "cnn":
            return CNNModuleFactory.create(config)
        elif model_architecture == "transformer":
            return TransformerModuleFactory.create(config)
