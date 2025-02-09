from hydra.core.config_store import ConfigStore
from pydantic.dataclasses import dataclass
from omegaconf import MISSING


@dataclass
class DatasetReaderConfig:
    _target_: str = MISSING
    dataset_dir: str = MISSING
    dataset_name: str = MISSING


@dataclass
class GHCDatsetReaderConfig(DatasetReaderConfig):
    _target_: str = "bullyguard.data_processing.dataset_readers.GHCDatasetReader"
    dev_split_ratio: float = MISSING


@dataclass
class DatasetReaderManagerConfig:
    _target_: str = "bullyguard.data_processing.dataset_readers.DatasetReaderManager"
    dataset_readers: dict[str, DatasetReaderConfig] = MISSING


def setup_config() -> None:
    cs = ConfigStore.instance()
    cs.store(name="dataset_reader_manager_schema", node=DatasetReaderManagerConfig, group="dataset_reader_manager")

    cs.store(name="ghc_dataset_reader_schema", node=GHCDatsetReaderConfig, group="dataset_reader_manager/dataset_reader")
