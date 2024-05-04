import importlib
from typing import Any, Dict, Tuple


class PythonObjectFactory:
    """Generates Python objects from a given configuration."""

    @staticmethod
    def create(config: Dict[str, Any]) -> Any:
        """
        Given a dictionary configuration, this function generates the desired Python object.

        If the configuration includes a nested dictionary, the function calls itself recursively
        to handle this nested configuration.

        The function requires a "module" field to be provided in the configuration,
        otherwise it raises a ValueError.

        Args:
            config (Dict[str, Any]): A dictionary containing the configuration of the object.

        Returns:
            Any: An instance of a class.

        Raises:
            ValueError: If no "module" field is found in the configuration.
        """
        module_name = config.pop("module")
        module, class_name = PythonObjectFactory.get_module_and_class(module_name)
        for key, value in config.items():
            if isinstance(value, dict):
                config[key] = PythonObjectFactory.create(value)
        obj = getattr(module, class_name)(**config)
        return obj

    @staticmethod
    def get_module_and_class(full_name: str) -> Tuple[Any, str]:
        """
        Given a full class name (including the module), this function returns the associated module and class.

        The name can be a dot-separated string representing the path to a class within a package.

        Args:
            full_name (str): The name of the class including the module path.

        Returns:
            Tuple[Any, str]: The module and class name associated with the name.

        Raises:
            AttributeError: If an unsupported module or class is requested.
            ImportError: If the module cannot be imported.
        """
        module_name, class_name = full_name.rsplit('.', 1)
        module = importlib.import_module(module_name)
        return module, class_name
