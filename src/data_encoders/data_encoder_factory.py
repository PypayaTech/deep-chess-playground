from src.data_encoders.input_encoders.grid_encoding import GridEncoder
from src.data_encoders.output_encoders.move_encoding_8_8_73 import MoveEncoder8x8x73


class DataEncoderFactory:
    @staticmethod
    def create(config: dict[str, str]):
        encoder_category = config.pop("category").lower()

        if encoder_category == "GridEncoder":
            encoder = DataEncoderFactory.build_grid_encoder(config)
        elif encoder_category == "MoveEncoder8x8x73":
            encoder = DataEncoderFactory.build_move_encoder_8_8_73(config)
        else:
            raise ValueError("Invalid configuration - no valid encoder category found.")

        return encoder

    @staticmethod
    def build_grid_encoder(config):
        return GridEncoder()

    @staticmethod
    def build_move_encoder_8_8_73(config):
        return MoveEncoder8x8x73()
