from typing import Optional
import dask.dataframe as dd
import psutil
from shutil import rmtree
from bullyguard.utils.utils import run_shell_command
from bullyguard.utils.gcp_utils import access_secret_version


def get_cmd_to_get_raw_data(
    version: str,
    data_local_save_dir: str,
    dvc_remote_repo: str,
    dvc_data_folder: str,
    github_user_name: str,
    github_access_token: str,
) -> str:
    without_https = dvc_remote_repo.replace("https://", "")
    dvc_remote_repo = f"https://{github_user_name}:{github_access_token}@{without_https}"
    command = f"dvc get {dvc_remote_repo} {dvc_data_folder} --rev {version} -o {data_local_save_dir}"
    return command


def get_raw_data_with_version(
    version: str,
    data_local_save_dir: str,
    dvc_remote_repo: str,
    dvc_data_folder: str,
    github_user_name: str,
    github_access_token: str,
) -> None:
    rmtree(data_local_save_dir, ignore_errors=True)
    command = get_cmd_to_get_raw_data(
        version, data_local_save_dir, dvc_remote_repo, dvc_data_folder, github_user_name, github_access_token
    )
    run_shell_command(command)


def get_nrof_partitions(
    df_memory_usage: int,
    nrof_workers: int,
    available_memory: Optional[int],
    min_partition_size: int,
    aimed_nrof_partitions_per_worker: int,
) -> int:
    """Calculates the optimal number of partitions for a Dask DataFrame based on memory constraints.

    This function determines the number of partitions needed to efficiently process a DataFrame
    across multiple workers while respecting memory limitations and partition size requirements.

    Args:
        df_memory_usage: Total memory usage of the DataFrame in bytes.
        nrof_workers: Number of available worker processes.
        available_memory: Optional memory limit in bytes. If None, uses available system memory.
        min_partition_size: Minimum allowed size for each partition in bytes.
        aimed_nrof_partitions_per_worker: Target number of partitions per worker.

    Returns:
        int: Optimal number of partitions for the DataFrame.

    Examples:
        >>> memory_usage = 1024 * 1024 * 100  # 100MB
        >>> get_nrof_partitions(memory_usage, 4, None, 15 * 1024**2, 10)
        8
    """
    # Get available system memory if not provided
    if available_memory is None:
        available_memory = psutil.virtual_memory().available

    # Handle cases where DataFrame is smaller than minimum partition size
    if df_memory_usage <= min_partition_size:
        return 1

    # Handle cases where DataFrame can be evenly distributed across workers
    # within minimum partition size constraints
    if df_memory_usage / nrof_workers <= min_partition_size:
        return round(df_memory_usage / min_partition_size)

    # Calculate minimum partitions needed to fit in available memory
    nrof_partitions_per_worker = 0
    required_memory = float("inf")
    while required_memory > available_memory:
        nrof_partitions_per_worker += 1
        required_memory = df_memory_usage / nrof_partitions_per_worker

    # Optimize number of partitions while respecting constraints
    nrof_partitions = nrof_partitions_per_worker * nrof_workers
    while (df_memory_usage / (nrof_partitions + 1)) > min_partition_size and (
        nrof_partitions // nrof_workers
    ) < aimed_nrof_partitions_per_worker:
        nrof_partitions += 1

    return nrof_partitions


def repartition_dataframe(
    df: dd.core.DataFrame,
    nrof_workers: int,
    available_memory: Optional[int] = None,
    min_partition_size: int = 15 * 1024**2,
    aimed_nrof_partitions_per_worker: int = 10,
) -> dd.core.DataFrame:
    """Repartitions a Dask DataFrame for optimal processing across workers.

    This function optimizes the partitioning of a Dask DataFrame based on available workers,
    memory constraints, and efficiency considerations. It first consolidates the DataFrame
    into a single partition to ensure even distribution, then repartitions it to the
    calculated optimal number of partitions.

    Args:
        df: Input Dask DataFrame to be repartitioned.
        nrof_workers: Number of available worker processes.
        available_memory: Optional memory limit in bytes. If None, uses available system memory.
            Defaults to None.
        min_partition_size: Minimum size for each partition in bytes.
            Defaults to 15MB (15 * 1024**2).
        aimed_nrof_partitions_per_worker: Target number of partitions per worker.
            Defaults to 10.

    Returns:
        dd.core.DataFrame: Repartitioned Dask DataFrame optimized for parallel processing.

    Examples:
        >>> import dask.dataframe as dd
        >>> df = dd.from_pandas(pd.DataFrame({'A': range(1000)}), npartitions=2)
        >>> optimized_df = repartition_dataframe(df, nrof_workers=4)
    """
    # Calculate total memory usage of the DataFrame
    df_memory_usage = df.memory_usage(deep=True).sum().compute()

    # Calculate optimal number of partitions
    nrof_partitions = get_nrof_partitions(
        df_memory_usage,
        nrof_workers,
        available_memory,
        min_partition_size,
        aimed_nrof_partitions_per_worker
    )

    # Repartition DataFrame: first consolidate, then split into optimal partitions
    partitioned_df: dd.core.DataFrame = df.repartition(npartitions=1).repartition(
        npartitions=nrof_partitions
    )  # type: ignore

    return partitioned_df


def get_repo_address_with_access_token(
    gcp_project_id: str, gcp_secret_id: str, repo_address: str, user_name: str
) -> str:
    access_token = access_secret_version(gcp_project_id, gcp_secret_id)
    repo_address = repo_address.replace("https://", "")
    return f"https://{user_name}:{access_token}@{repo_address}"
