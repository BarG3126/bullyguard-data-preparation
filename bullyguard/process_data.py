from bullyguard.config_schemas.data_processing_config_schema import DataProcessConfig
from bullyguard.utils.config_utils import get_config
from bullyguard.utils.gcp_utils import access_secret_version
from bullyguard.utils.data_utils import get_raw_data_with_version


@get_config(config_path="../configs", config_name="data_processing_config")
def process_data(config: DataProcessConfig) -> None:

    github_access_token = access_secret_version(config.infrastructure.project_id, config.github_access_token_secret_id)

    try:
        get_raw_data_with_version(
            version=config.version,
            data_local_save_dir=config.data_local_save_dir,
            dvc_remote_repo=config.dvc_remote_repo,
            dvc_data_folder=config.dvc_data_folder,
            github_user_name=config.github_user_name,
            github_access_token=github_access_token
        )
    except Exception as e:
        print(f"Error occurred: {str(e)}")
        # Add more detailed error logging here if needed


if __name__ == "__main__":
    process_data()  # type: ignore
