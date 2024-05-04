from src.lightning_modules.basic_module import BasicModule
from src.lightning_modules.binary_classifier import BinaryClassifier
from src.lightning_modules.multiclass_classifier import MultiClassClassifier
from src.lightning_modules.regressor import Regressor
from src.pytorch_modules.pytorch_module_factory import PyTorchModuleFactory
from src.utils.python_object_factory import PythonObjectFactory


class LightningModuleFactory:
    @staticmethod
    def build_module(config):
        module_category = config.pop("category").lower()
        if module_category == "basic":
            module = LightningModuleFactory.build_basic_module(config)
        elif module_category == "binaryclassifier":
            module = LightningModuleFactory.build_binary_classifier(config)
        elif module_category == "multiclassclassifier":
            module = LightningModuleFactory.build_multiclass_classifier(config)
        elif module_category == "regressor":
            module = LightningModuleFactory.build_regressor(config)
        else:
            raise ValueError("Invalid configuration - no valid lightning module category found.")
        return module

    @staticmethod
    def build_basic_module(config):
        return BasicModule(pytorch_module=PyTorchModuleFactory.build_module(config["pytorch_module"]),
                           optimizer=PythonObjectFactory.create(config["optimizer"]),
                           loss_fn=PythonObjectFactory.create(config["loss_function"]),
                           metrics={name: PythonObjectFactory.create(metric_config)
                                    for name, metric_config in config["metrics"]})

    @staticmethod
    def build_binary_classifier(config):
        return BinaryClassifier(pytorch_module=PyTorchModuleFactory.build_module(config["pytorch_module"]),
                                optimizer=PythonObjectFactory.create(config["optimizer"]),
                                threshold=config["threshold"],
                                metrics={name: PythonObjectFactory.create(metric_config)
                                         for name, metric_config in config["metrics"]})

    @staticmethod
    def build_multiclass_classifier(config):
        return MultiClassClassifier(pytorch_module=PyTorchModuleFactory.build_module(config["pytorch_module"]),
                                    optimizer=PythonObjectFactory.create(config["optimizer"]),
                                    num_classes=config["num_classes"],
                                    metrics={name: PythonObjectFactory.create(metric_config)
                                             for name, metric_config in config["metrics"]})

    @staticmethod
    def build_regressor(config):
        return Regressor(pytorch_module=PyTorchModuleFactory.build_module(config["pytorch_module"]),
                         optimizer=PythonObjectFactory.create(config["optimizer"]),
                         metrics={name: PythonObjectFactory.create(metric_config)
                                  for name, metric_config in config["metrics"]})
