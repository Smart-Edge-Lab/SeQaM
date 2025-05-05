import time
from datetime import datetime, timezone


class ExperimentFile():
    def __init__(self) -> None:
        self._filename_ = ""   


    def create_file(self, name: str):
        """
        Creates a new file with the given name and writes an initial info line to it.
        
        Parameters:
            name (str): The name of the file to be created.
        """
        self._filename_ = f"scenario_{name}.txt"
        with open(self._filename_, "w") as f:
            f.write(str(self.generate_info_line("init"))+"\n")
            f.close()
            

    def write_to_file(self, event: str):
        """
        Appends an info line to the existing file.
        
        Parameters:
            event (str): The event to be written to the file.
        """   
        with open(self._filename_, "a") as f:
            f.write(str(self.generate_info_line(event))+"\n")
            f.close()


    def generate_info_line (self, event: str):
        """
        Generates an info line with the current UTC Unix time in microseconds and the given event.
        
        Parameters:
            event (str): The event to be included in the info line.
        
        Returns:
            dict: A dictionary containing the UTC Unix time in microseconds and the event.
        """
        #unix_time = int(round(time.time() * 1000))
        # timestamp is stored in UTC time
        unix_time = int(datetime.now(timezone.utc).timestamp() * 1000000)
        return {"UTC_Unix_us": unix_time, "Action": event}





if __name__ == "__main__":
    ef = ExperimentFile()
    ef.create_file("test")
    time.sleep(0.2)
    ef.write_to_file("event1")
    time.sleep(0.1)
    ef.write_to_file("event2")
