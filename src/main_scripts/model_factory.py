from src.cnn.model_factory import CNNModelFactory
from src.fcn.model_factory import FCNModelFactory
from src.transformer.model_factory import TransformerModelFactory


class ModelFactory:
    @staticmethod
    def create(config: dict[str, str]):
        model_architecture = config["architecture"]
        if model_architecture == "fcn":
            return FCNModelFactory.create(config)
        elif model_architecture == "cnn":
            return CNNModelFactory.create(config)
        elif model_architecture == "transformer":
            return TransformerModelFactory.create(config)
