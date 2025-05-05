import abc

from edpapi_fh_dortmund_project_emulate.experiment.experiment import ExperimentStatistics
from edpapi_fh_dortmund_project_emulate.span.Span import Span


class ExperimentService:
    @abc.abstractmethod
    def get_experiments(self) -> list[str]:
        """
        Get names of conducted experiments

        :param app_name: application name

        :returns: list of experiment names
        """

    @abc.abstractmethod
    def get_experiment_by_name(self, name: str) -> list[Span]:
        """
        Gets details of the experiment steps

        :param name: name of the experiment

        :returns: details of every experiment step
        """

    @abc.abstractmethod
    def get_experiment_statistics_for_app(
        self,
        exp_name: str,
        app_name: str,
        extra_statistics: bool = False,
        raw_data: bool = False,
        nanos: bool = False,
    ) -> list[ExperimentStatistics]:
        """
        Get span time statistics for given app during the specified experiment

        :param exp_name: experiment name
        :param app_name: application name
        :param extra_statistics: calculate additional statistics using pandas
        :param raw_data: return raw span data
        :param nanos: return durations in nanoseconds

        :returns: details of app span durations during every step of the experiment
        """
