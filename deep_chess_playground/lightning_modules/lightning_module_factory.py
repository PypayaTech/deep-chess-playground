from deep_chess_playground.lightning_modules.basic_module import BasicModule
from deep_chess_playground.lightning_modules.binary_classifier import BinaryClassifier
from deep_chess_playground.lightning_modules.multiclass_classifier import MultiClassClassifier
from deep_chess_playground.lightning_modules.regressor import Regressor
from deep_chess_playground.pytorch_modules.pytorch_module_factory import PyTorchModuleFactory
from pypaya_python_tools import ConfigurableObjectGenerator


_object_generator = ConfigurableObjectGenerator()


class LightningModuleFactory:
    @staticmethod
    def build_module(config):
        module_category = config.pop("category").lower()
        if module_category == "Basic":
            module = LightningModuleFactory.build_basic_module(config)
        elif module_category == "BinaryClassifier":
            module = LightningModuleFactory.build_binary_classifier(config)
        elif module_category == "MultiClassClassifier":
            module = LightningModuleFactory.build_multiclass_classifier(config)
        elif module_category == "Regressor":
            module = LightningModuleFactory.build_regressor(config)
        else:
            raise ValueError("Invalid configuration - no valid lightning module category found.")
        return module

    @staticmethod
    def build_basic_module(config):
        return BasicModule(pytorch_module=PyTorchModuleFactory.build_module(config["pytorch_module"]),
                           optimizer=_object_generator.create(config["optimizer"]),
                           loss_fn=_object_generator.create(config["loss_function"]),
                           metrics={name: _object_generator.create(metric_config)
                                    for name, metric_config in config["metrics"]})

    @staticmethod
    def build_binary_classifier(config):
        return BinaryClassifier(pytorch_module=PyTorchModuleFactory.build_module(config["pytorch_module"]),
                                optimizer=_object_generator.create(config["optimizer"]),
                                threshold=config["threshold"],
                                metrics={name: _object_generator.create(metric_config)
                                         for name, metric_config in config["metrics"]})

    @staticmethod
    def build_multiclass_classifier(config):
        return MultiClassClassifier(pytorch_module=PyTorchModuleFactory.build_module(config["pytorch_module"]),
                                    optimizer=_object_generator.create(config["optimizer"]),
                                    num_classes=config["num_classes"],
                                    metrics={name: _object_generator.create(metric_config)
                                             for name, metric_config in config["metrics"]})

    @staticmethod
    def build_regressor(config):
        return Regressor(pytorch_module=PyTorchModuleFactory.build_module(config["pytorch_module"]),
                         optimizer=_object_generator.create(config["optimizer"]),
                         metrics={name: _object_generator.create(metric_config)
                                  for name, metric_config in config["metrics"]})
