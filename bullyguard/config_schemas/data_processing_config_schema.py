from hydra.core.config_store import ConfigStore
from omegaconf import MISSING
from pydantic.dataclasses import dataclass

from bullyguard.config_schemas.data_processing import dataset_cleaners_schema, dataset_readers_schema
from bullyguard.config_schemas.dask_cluster import dask_cluster_schema
from bullyguard.config_schemas.infrastructure import gcp_schema


@dataclass
class DataProcessConfig:
    version: str = MISSING
    data_local_save_dir: str = "./data/raw"
    dvc_remote_repo: str = "https://github.com/BarG3126/bullyguard-data.git"
    dvc_data_folder: str = "data/raw"
    github_user_name: str = "BarG3126"
    github_access_token_secret_id: str = "bullyguard-data-github-access-token"

    infrastructure: gcp_schema.GCPConfig = gcp_schema.GCPConfig()

    dataset_reader_manager: dataset_readers_schema.DatasetReaderManagerConfig = MISSING

    dataset_cleaner_manager: dataset_cleaners_schema.DatasetCleanerManagerConfig = MISSING

    dask_cluster: dask_cluster_schema.LocalDaskClusterConfig = MISSING

    processed_data_save_dir: str = MISSING


def setup_config() -> None:
    gcp_schema.setup_config()
    dataset_readers_schema.setup_config()
    dataset_cleaners_schema.setup_config()
    dask_cluster_schema.setup_config()

    cs = ConfigStore.instance()
    cs.store(name="data_processing_config_schema", node=DataProcessConfig)
