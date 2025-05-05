import unittest

from edpapi_fh_dortmund_project_emulate.experiment.experiment import ExperimentStatistics
from edpapi_fh_dortmund_project_emulate.experiment.merge_utils import merge_experiment_steps


class MergeExperimentStepsTest(unittest.TestCase):
    def test_merge_c1_ends_before_c2(self) -> None:
        """
        c1 starts alone.
        Then c2 joins in the meanwhile.
        c1 ends before c2.
        c3 starts when c1 and c2 are already finished.
        """
        steps = [
            ExperimentStatistics(
                commands=['c1'],
                indexes=[1],
                start_time=1,
                end_time=3,
            ),
            ExperimentStatistics(
                commands=['c2'],
                indexes=[2],
                start_time=2,
                end_time=5,
            ),
            ExperimentStatistics(
                commands=['c3'],
                indexes=[3],
                start_time=7,
                end_time=10,
            ),
        ]
        merged = merge_experiment_steps(steps)
        self.assertEqual(
            [
                ExperimentStatistics(
                    commands=['c1'],
                    indexes=[1],
                    start_time=1,
                    end_time=2,
                ),
                ExperimentStatistics(
                    commands=['c1', 'c2'],
                    indexes=[1, 2],
                    start_time=2,
                    end_time=3,
                ),
                ExperimentStatistics(
                    commands=['c2'],
                    indexes=[2],
                    start_time=3,
                    end_time=5,
                ),
                ExperimentStatistics(
                    commands=['idle'],
                    indexes=[],
                    start_time=5,
                    end_time=7,
                ),
                ExperimentStatistics(
                    commands=['c3'],
                    indexes=[3],
                    start_time=7,
                    end_time=10,
                ),
            ], merged
        )

    def test_merge_c2_ends_before_c1(self) -> None:
        """
        c1 starts alone.
        Then c2 joins in the meanwhile.
        c2 ends before c1.
        c3 starts when c1 and c2 are already finished.
        """
        steps = [
            ExperimentStatistics(
                commands=['c1'],
                indexes=[1],
                start_time=1,
                end_time=6,
            ),
            ExperimentStatistics(
                commands=['c2'],
                indexes=[2],
                start_time=2,
                end_time=5,
            ),
            ExperimentStatistics(
                commands=['c3'],
                indexes=[3],
                start_time=7,
                end_time=10,
            ),
        ]
        merged = merge_experiment_steps(steps)
        self.assertEqual(
            [
                ExperimentStatistics(
                    commands=['c1'],
                    indexes=[1],
                    start_time=1,
                    end_time=2,
                ),
                ExperimentStatistics(
                    commands=['c1', 'c2'],
                    indexes=[1, 2],
                    start_time=2,
                    end_time=5,
                ),
                ExperimentStatistics(
                    commands=['c1'],
                    indexes=[1],
                    start_time=5,
                    end_time=6,
                ),
                ExperimentStatistics(
                    commands=['idle'],
                    indexes=[],
                    start_time=6,
                    end_time=7,
                ),
                ExperimentStatistics(
                    commands=['c3'],
                    indexes=[3],
                    start_time=7,
                    end_time=10,
                ),
            ], merged
        )

    def test_real_scenario1(self) -> None:
        PROCESS_START = 1724923694926
        CPU_LOAD_START = 1724923694926 - PROCESS_START
        CPU_LOAD_DURATION = 60204
        CPU_LOAD_END = CPU_LOAD_START + CPU_LOAD_DURATION
        MEMORY_LOAD_START = 1724923697408 - PROCESS_START
        MEMORY_LOAD_DURATION = 10021
        MEMORY_LOAD_END = MEMORY_LOAD_START + MEMORY_LOAD_DURATION
        NETWORK_LOAD_START = 1724923697455 - PROCESS_START
        NETWORK_LOAD_DURATION = 5053
        NETWORK_LOAD_END = NETWORK_LOAD_START + NETWORK_LOAD_DURATION
        NETWORK_BANDWIDTH_START = 1724923698401 - PROCESS_START
        NETWORK_BANDWIDTH_DURATION = 30126
        NETWORK_BANDWIDTH_END = NETWORK_BANDWIDTH_START + NETWORK_BANDWIDTH_DURATION
        input: list[dict[str, str | int]] = [
            {
                "name": "cpu_load time:60s",
                "timestamp": CPU_LOAD_START,
                "duration": CPU_LOAD_DURATION,
            },
            {
                "name": "memory_load time:10s",
                "timestamp": MEMORY_LOAD_START,
                "duration": MEMORY_LOAD_DURATION,
            },
            {
                "name": "network_load time:5s",
                "timestamp": NETWORK_LOAD_START,
                "duration": NETWORK_LOAD_DURATION,
            },
            {
                "name": "network_bandwidth time:30s",
                "timestamp": NETWORK_BANDWIDTH_START,
                "duration": NETWORK_BANDWIDTH_DURATION,
            }
        ]
        steps = [
            ExperimentStatistics(
                commands=[str(c['name'])],
                indexes=[i],
                start_time=int(c['timestamp']),
                end_time=int(c['timestamp']) + int(c['duration']),
            ) for i, c in enumerate(input)
        ]
        merged = merge_experiment_steps(steps)
        self.assertEqual([
            ExperimentStatistics(
                commands=['cpu_load time:60s'],
                indexes=[0],
                start_time=CPU_LOAD_START, end_time=MEMORY_LOAD_START
            ),
            ExperimentStatistics(
                commands=[
                    'cpu_load time:60s',
                    'memory_load time:10s'],
                indexes=[0, 1],
                start_time=MEMORY_LOAD_START, end_time=NETWORK_LOAD_START
            ),
            ExperimentStatistics(
                commands=[
                    'cpu_load time:60s',
                    'memory_load time:10s',
                    'network_load time:5s'],
                indexes=[0, 1, 2], start_time=NETWORK_LOAD_START, end_time=NETWORK_BANDWIDTH_START,
            ),
            ExperimentStatistics(
                commands=[
                    'cpu_load time:60s',
                    'memory_load time:10s',
                    'network_load time:5s',
                    'network_bandwidth time:30s',
                ],
                indexes=[0, 1, 2, 3], start_time=NETWORK_BANDWIDTH_START, end_time=NETWORK_LOAD_END,
            ),
            ExperimentStatistics(
                commands=[
                    'cpu_load time:60s',
                    'memory_load time:10s',
                    'network_bandwidth time:30s',
                ],
                indexes=[0, 1, 3],
                start_time=NETWORK_LOAD_END, end_time=MEMORY_LOAD_END,
            ),
            ExperimentStatistics(
                commands=[
                    'cpu_load time:60s',
                    'network_bandwidth time:30s',
                ],
                indexes=[0, 3],
                start_time=MEMORY_LOAD_END, end_time=NETWORK_BANDWIDTH_END,
            ),
            ExperimentStatistics(
                commands=[
                    'cpu_load time:60s',
                ],
                indexes=[0],
                start_time=NETWORK_BANDWIDTH_END, end_time=CPU_LOAD_END,
            ),
        ], merged
        )
