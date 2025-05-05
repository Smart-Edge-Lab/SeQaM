from itertools import chain

from edpapi_fh_dortmund_project_emulate.experiment.experiment import ExperimentStatistics


def merge_experiment_steps(experimental_steps: list[ExperimentStatistics]) -> list[ExperimentStatistics]:
    """
    Merges experiment steps so that overlapping steps
    share
    """
    experimental_steps_sorted = sorted(experimental_steps, key=lambda x: x.start_time)
    times: list[int] = sorted(
        chain.from_iterable([[c.start_time, c.end_time] for c in experimental_steps_sorted])
    )
    merged: list[ExperimentStatistics] = []
    for i in range(1, len(times)):
        s = times[i - 1]
        e = times[i]
        ongoing = [i for i in experimental_steps_sorted if i.start_time <= s < i.end_time]
        commands = [i.commands[0] for i in ongoing]
        if commands:
            step = ExperimentStatistics(
                start_time=s,
                end_time=e,
                commands=commands,
                indexes=[i.indexes[0] for i in ongoing],
            )
        else:
            step = ExperimentStatistics(
                start_time=s,
                end_time=e,
                commands=['idle'],
                indexes=[],
            )
        merged.append(step)
    return merged
