from Modules.DataManager.ClickhouseClient import ClickhouseClient



class DBclient:

    def __init__(self) -> None:
        pass


    def create_client(self, db_obj, db_host="127.0.0.1"):
        """
        creates a DB client to interact with it
        Parameters:
        db_host (str): The IP of the host where the DB is allocated.
        returns the created client of the database to query
        """ 
        return db_obj.create_client(db_host)


    def get_client(self, db_obj):
        """
        returns the created client of the database to query
        """
        return db_obj.get_client()
    

    def send_generic_query(self, db_obj, query: str):
        """
        sends any given query as string to the DB
        Parameters:
        query (str): query to be sent
        """
        return db_obj.send_generic_query(query)
    

    def get_single_core_idle(self, db_obj, cpu_name, host_name, time_difference):
        """
        Retrieves the idle time of a single core cpu_name of the host defined by host_name during a time window.

        Parameters:
        host_name (str): The name of the host, as it is shown in the console cmd.
        cpu_name (str): The name of the specific core
        time_difference (int): The time during which the measurement is to be taken. It must be equal to a multiple of the collection cycle
        as declared in the collector

        Returns:
        list: A dictionary containing the core name (key), and a list (value) containing the idle time during the time frame, the unix time of the 
        first measurement, the unix time of the prior measurement, the usage percentage
        """
        return db_obj.get_single_core_idle(cpu_name, host_name, time_difference)


    def get_all_cores_idle(self, db_obj, host_name, time_difference):
        """
        Retrieves the idle time of all cores of the host defined by host_name during a time window.

        Parameters:
        host_name (str): The name of the host, as it is shown in the console cmd.
        time_difference (int): The time during which the measurement is to be taken. It must be equal to one collection cycle
        as declared in the collector

        Returns:
        list: A dictionary containing the core name (key), and a list (value) containing the idle time during the time frame, the unix time of the 
        first measurement, the unix time of the prior measurement, the usage percentage
        """
        return db_obj.get_all_cores_idle(host_name, time_difference)


    def get_raw_memory_usage(self,  db_obj, host_name):
        """
        Retrieves the latest memory usage in bytes of the host.

        Parameters:
        host_name (str): The name of the host, as it is shown in the console cmd.

        Returns:
        list: A string containing the measurement
        """
        return db_obj.get_raw_memory_usage(host_name)


    def get_memory_usage_percentage(self,  db_obj, host_name):
        """
        Retrieves the latest memory usage percentage of the host.

        Parameters:
        host_name (str): The name of the host, as it is shown in the console cmd.

        Returns:
        list: A string containing the measurement

        Notes:
        This function uses a query to retrieve the required data from the signoz_traces.signoz_spans table.
        The query limits the number of rows to the product of trace_size and traces_to_avg, and orders the results by timestamp in descending order.
        The results are then grouped by span name.
        """
        return db_obj.get_memory_usage_percentage(host_name)


    def get_cpu_load_15m(self, db_obj, host_name):
        """
        Retrieves the average cpu load of the host for the last 15 minutes.

        Parameters:
        host_name (str): The name of the host, as it is shown in the console cmd.

        Returns:
        list: A list containing the average cpu load, the unix time of the measurement, the name of the measurement

        Notes:
        This function uses a query to retrieve the required data from the signoz_traces.signoz_spans table.
        The query limits the number of rows to the product of trace_size and traces_to_avg, and orders the results by timestamp in descending order.
        The results are then grouped by span name.
        """
        return db_obj.get_cpu_load_15m(host_name)


    def get_cpu_load_5m(self, db_obj, host_name):
        """
        Retrieves the average cpu load of the host for the last 5 minutes.

        Parameters:
        host_name (str): The name of the host, as it is shown in the console cmd.

        Returns:
        list: A list containing the average cpu load, the unix time of the measurement, the name of the measurement

        Notes:
        This function uses a query to retrieve the required data from the signoz_traces.signoz_spans table.
        The query limits the number of rows to the product of trace_size and traces_to_avg, and orders the results by timestamp in descending order.
        The results are then grouped by span name.
        """
        return db_obj.get_cpu_load_5m(host_name)
    

    def get_cpu_load_1m(self, db_obj, host_name):
        """
        Retrieves the average cpu load of the host for the last 1 minute.

        Parameters:
        host_name (str): The name of the host, as it is shown in the console cmd.

        Returns:
        list: A list containing the average cpu load, the unix time of the measurement, the name of the measurement

        Notes:
        This function uses a query to retrieve the required data from the signoz_traces.signoz_spans table.
        The query limits the number of rows to the product of trace_size and traces_to_avg, and orders the results by timestamp in descending order.
        The results are then grouped by span name.
        """
        return db_obj.get_cpu_load_1m(host_name)
    

    def get_trace_avg_number_based(self, db_obj, trace_size, traces_to_avg):
        """
        Retrieves the average latency duration of the trace and the span name.

        Parameters:
        trace_size (int): The size of each trace (number of spans in a complete trace).
        traces_to_avg (int): The number of traces to average.

        Returns:
        list: A list containing the average latency in milliseconds, and span name for each span contained in the trace.

        Notes:
        This function uses a query to retrieve the required data from the signoz_traces.signoz_spans table.
        The query limits the number of rows to the product of trace_size and traces_to_avg, and orders the results by timestamp in descending order.
        The results are then grouped by span name.
        """
        return db_obj.get_trace_avg_number_based(trace_size, traces_to_avg)


    def get_span_avg_time_based(self, db_obj, span_name, limit_time):
        """
        Retrieves the average duration, count, and maximum timestamp for a specified span name within a given time range.

        Parameters:
        span_name (str): The name of the span to retrieve data for.
        limit_time (str): The start time of the time range to retrieve data for in unix.

        Returns:
        list: A list containing the maximum Unix timestamp, maximum timestamp from the latest span with the given name,
        average duration in milliseconds, count, and span name.

        Notes:
        This function uses a query to retrieve the required data from the signoz_traces.signoz_spans table.
        The query filters the results by span name and timestamp, and groups the results by span name.
        The results are then aggregated to calculate the maximum Unix timestamp, maximum timestamp, average duration, and count.
        """  
        if limit_time:
            return db_obj.get_span_avg_time_based(span_name, limit_time)
        else:
            return db_obj.get_span_avg_time_based(span_name)
    
    #TODO: useful methoda that should be implemented
    #get_span_average
    #get_span_grouped_by_name
    #get_latest_span
    #get_span_by_id






if __name__ == '__main__':

    db_client = DBclient()
    db_type = ClickhouseClient()
    db_client.create_client(db_type, "172.22.174.157")
    c =  db_client.get_all_cores_idle(db_obj = db_type, host_name= 'UEcollector', time_difference = 30000)
    print(c)
    # c =  db_client.get_memory_usage_percentage(db_obj = db_type, host_name= 'UEcollector')
    # print(c)
    # c =  db_client.get_cpu_load_1m(db_obj = db_type, host_name= 'UEcollector')
    # print(c)
    # c =  db_client.get_trace_avg_number_based(db_obj = db_type, trace_size = 21, traces_to_avg = 3)
    # print(c)
    # c =  db_client.get_span_avg_time_based(db_obj = db_type, span_name = 'client_request', limit_time = None)
    # print(c)
    