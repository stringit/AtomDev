from dataclasses import dataclass
from pathlib import Path

from pylizlib.core.data.unit import get_normalized_gb_mb_str
from pylizlib.core.os.snap import Snapshot
from pylizlib.qtfw.domain.sw import SoftwareData


@dataclass
class DevlizSnapshotData:
    snapshot_list: list[Snapshot]

    @property
    def count(self) -> int:
        return len(self.snapshot_list)

    @property
    def get_mb_size(self) -> str:
        total_size = 0
        for config in self.snapshot_list:
            for dir_assoc in config.directories:
                path = Path(dir_assoc.original_path)
                if path.exists() and path.is_dir():
                    for file in path.rglob('*'):
                        if file.is_file():
                            total_size += file.stat().st_size
        return get_normalized_gb_mb_str(total_size)


# @dataclass
# class DevlizSettingsData:
#     starred_dirs: list[Path] = None
#     starred_files: list[Path] = None
#     starred_exes: list[Path] = None
#     tags: list[str] = None
#     custom_snap_data: list[str] = None


@dataclass
class DevlizData:
    monitored_software: list[SoftwareData] = None
    monitored_services: list[SoftwareData] = None
    snapshots: DevlizSnapshotData = None

