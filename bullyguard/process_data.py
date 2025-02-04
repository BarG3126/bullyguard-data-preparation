from bullyguard.config_schemas.config_schema import Config
from bullyguard.utils.config_utils import get_config
from bullyguard.utils.gcp_utils import access_secret_version


@get_config(config_path="../configs", config_name="config")
def process_data(config: Config) -> None:
    print(config)

    github_access_token = access_secret_version("ml-project-447013", "bullyguard-data-github-access-token")
    print(f"{github_access_token=}")


if __name__ == "__main__":
    process_data()  # type: ignore
