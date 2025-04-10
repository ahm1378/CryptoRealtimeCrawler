import numpy as np
import pandas as pd
import os, logging, time, csv

from typing import Callable, Any
from decimal import Decimal


class SharedUtils:

    @staticmethod
    def now():
        return pd.Timestamp.now().replace(second=0, microsecond=0)
    
    
    @staticmethod
    def check_directories(directories):
        """
        Check directories and create them if they do not exist.

        This function takes a list of directory paths as input. It iterates over each directory path
        in the list, checks if the directory exists, and creates it if it does not.

        Parameters:
        - directories (list of str): A list of directory paths to be checked and created if needed.

        Returns:
        - None
        """
        for directory in directories:
            if not os.path.exists(directory):
                os.makedirs(directory)
    

    @staticmethod
    def check_and_create_csv(file_path, header):
        """
        Check if a CSV file exists, and if it doesn't, create it with the specified header.

        Parameters:
        file_path (str): The path to the CSV file.
        header (list): A list of strings representing the header row of the CSV file.

        Returns:
        None
        """
        # Check if the file exists
        if not os.path.exists(file_path):
            # Create the file and write the header row
            with open(file_path, 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(header)
    

    @staticmethod
    def initialize_log(log_file : str = 'data/events.log', 
                       add_stream_handler: bool = False):
        """
        Initializes a logging instance if not already initialized.

        Parameters:
        - log_file (str): Path to the log file.
        
        Returns:
        - logging.Logger: A configured logging instance.
        """
        log = logging.getLogger(__name__)
        if not log.handlers:  # Check if the logger already has handlers
            log.setLevel(logging.DEBUG)  # Set to DEBUG to capture all levels of messages
            
            formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(funcName)s - %(message)s')
            
            file_handler = logging.FileHandler(log_file)
            file_handler.setFormatter(formatter)
            file_handler.setLevel(logging.INFO)  # File handler captures INFO and above levels
            log.addHandler(file_handler)
            

            if add_stream_handler:
                stream_handler = logging.StreamHandler()
                stream_handler.setFormatter(formatter)
                stream_handler.setLevel(logging.DEBUG)  # Stream handler captures all levels of logs
                log.addHandler(stream_handler)
        # else:
        #     log.warning("Logger already initialized with handlers.")

        return log
    

    @staticmethod
    def retry(func: Callable[..., Any], retries: int = 3, delay: int = 1, 
            backoff: int = 2, timeout: int = None, 
            raise_none: bool = True, *args, **kwargs) -> Any:
        """
        Retry calling the provided function with the given arguments and keyword arguments.

        Parameters:
        - func : callable : The function to be retried.
        - retries : int : The number of retry attempts.
        - delay : int : Initial delay between retries (in seconds).
        - backoff : int : Backoff factor for exponential backoff.
        - timeout : int : Maximum time (in seconds) to wait for each retry attempt.
        - raise_none (bool, optional): Whether to raise an exception if None response received. Defaults to True.

        Returns:
        - Any : The result of the function call, if successful.

        Raises:
        - ValueError : If all retry attempts fail.
        - TimeoutError : If the maximum timeout is reached.
        """

        last_exception = None
        for attempt in range(1, retries + 1):
            try:
                start_time = time.time()
                response = func(*args, **kwargs)
                end_time = time.time()

                # Check if response is None and treat it as an error
                if raise_none and (not response):
                    raise ValueError("Received None response.")
                
                return response
            except Exception as e:
                last_exception = e
                if timeout and (end_time - start_time) >= timeout:
                    raise TimeoutError("Timeout reached.") from None
                if attempt > 1:  # Skip sleep on first try
                    time.sleep(delay * (backoff ** (attempt - 1)))

        # Raise an exception with the last encountered error
        raise ValueError(f"All retries failed. Last exception: {last_exception}")


    @staticmethod
    def count_decimal_places(num):
        decimal_part = Decimal(str(num)) % 1
        return -decimal_part.as_tuple().exponent if decimal_part else 0