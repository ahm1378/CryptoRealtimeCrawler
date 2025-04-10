from typing import Dict, List, Any, Optional
import requests
from requests.exceptions import RequestException


class CMCCrawler:
    """
    A crawler for fetching data from CoinMarketCap API.
    
    Attributes:
        api_base_url (str): The base URL for the CoinMarketCap API
        headers (Dict[str, str]): Headers required for API authentication
    """
    
    def __init__(self, api_key: str,
                 api_base_url: str = 'https://pro-api.coinmarketcap.com/v1/') -> None:
        """
        Initialize the CMCCrawler with API credentials.
        
        Args:
            api_key (str): CoinMarketCap API key
            api_base_url (str, optional): Base URL for the API. Defaults to pro-api URL.
        """
        self.__api_base_url = api_base_url
        self.__headers = {
            'Accepts': 'application/json',
            'X-CMC_PRO_API_KEY': api_key,
        }

    def get_cmc_coins_data(self, limit: int = 1000) -> Dict[str, Any]:
        """
        Fetch latest cryptocurrency listings from CoinMarketCap.
        
        Args:
            limit (int, optional): Maximum number of coins to fetch. Defaults to 1000.
            
        Returns:
            Dict[str, Any]: JSON response containing coin data
            
        Raises:
            RequestException: If the API request fails
        """
        end_point = 'cryptocurrency/listings/latest'
        api_url = self.__api_base_url + end_point

        parameters = {
            'start': '1',
            'limit': limit,
            'convert': 'USD'
        }

        try:
            session = requests.Session()
            session.headers.update(self.__headers)
            response = session.get(api_url, params=parameters)
            response.raise_for_status()
            return response.json()
        except RequestException as e:
            raise RequestException(f"Failed to fetch CMC coins data: {str(e)}")

    @staticmethod
    def remove_stablecoins(coins_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Remove stablecoins from the coin data.
        
        Args:
            coins_data (Dict[str, Any]): Raw coin data from CMC
            
        Returns:
            Dict[str, Any]: Filtered coin data without stablecoins
        """
        coins_data_ = coins_data.get('data', [])
        non_stablecoins = [coin for coin in coins_data_ 
                          if 'stablecoin' not in coin.get('tags', [])]
        coins_data['data'] = non_stablecoins
        return coins_data

    @staticmethod
    def get_cmc_chains_data(limit: int = 200) -> Dict[str, Any]:
        """
        Fetch blockchain chain data from CoinMarketCap.
        
        Args:
            limit (int, optional): Maximum number of chains to fetch. Defaults to 200.
            
        Returns:
            Dict[str, Any]: JSON response containing chain data
            
        Raises:
            RequestException: If the API request fails
        """
        try:
            response = requests.get(
                url=f'https://api.coinmarketcap.com/data-api/v3/chain/listing?limit={limit}'
            )
            response.raise_for_status()
            return response.json()
        except RequestException as e:
            raise RequestException(f"Failed to fetch CMC chains data: {str(e)}")

    @staticmethod
    def get_chains_tvl_percentages() -> Dict[str, Any]:
        """
        Fetch TVL (Total Value Locked) percentages for different chains.
        
        Returns:
            Dict[str, Any]: JSON response containing TVL percentages
            
        Raises:
            RequestException: If the API request fails
        """
        try:
            response = requests.get(
                url='https://api.coinmarketcap.com/data-api/v3/chain/tvl/percentage'
            )
            response.raise_for_status()
            return response.json()
        except RequestException as e:
            raise RequestException(f"Failed to fetch chains TVL percentages: {str(e)}")

    @staticmethod
    def get_total_tvl_data() -> Dict[str, Any]:
        """
        Fetch total TVL (Total Value Locked) data across all chains.
        
        Returns:
            Dict[str, Any]: JSON response containing total TVL data
            
        Raises:
            RequestException: If the API request fails
        """
        try:
            response = requests.get(
                url='https://api.coinmarketcap.com/data-api/v3/chain/tvl/total/chart'
            )
            response.raise_for_status()
            return response.json()
        except RequestException as e:
            raise RequestException(f"Failed to fetch total TVL data: {str(e)}")