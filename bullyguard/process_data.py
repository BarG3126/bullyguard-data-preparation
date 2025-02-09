from bullyguard.config_schemas.config_schema import Config
from bullyguard.utils.config_utils import get_config
from bullyguard.utils.gcp_utils import access_secret_version
from bullyguard.utils.data_utils import get_raw_data_with_version


@get_config(config_path="../configs", config_name="config")
def process_data(config: Config) -> None:
    version = "v1"
    data_local_save_dir = "./data/raw"
    dvc_remote_repo = "https://github.com/BarG3126/bullyguard-data.git"
    dvc_data_folder = "data/raw"
    github_user_name = "BarG3126"
    github_access_token = access_secret_version("ml-project-447013", "bullyguard-data-github-access-token")

    try:
        get_raw_data_with_version(
            version=version,
            data_local_save_dir=data_local_save_dir,
            dvc_remote_repo=dvc_remote_repo,
            dvc_data_folder=dvc_data_folder,
            github_user_name=github_user_name,
            github_access_token=github_access_token,
        )
    except Exception as e:
        print(f"Error occurred: {str(e)}")
        # Add more detailed error logging here if needed


if __name__ == "__main__":
    process_data()  # type: ignore
