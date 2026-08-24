from odoo import models, api
from ..services.fpl_api_client import FPLApiClient, FPLDataService, FPLApiException
from ..services.fpl_pulse_api_client import FPLPulseLiveApiClient, FPLPulseLiveApiException
import logging

_logger = logging.getLogger(__name__)

class FPLApiMixin(models.AbstractModel):
    _name = 'fpl.api.mixin'
    _description = 'FPL API Mixin'
    
    @api.model
    def get_api_client(self, cookies=None, x_api_authorization=None):
        """
        Get a configured FPL API client
        
        Args:
            cookies (str): Authentication cookies (optional)
            x_api_authorization (str): Authorization header (optional)
            
        Returns:
            FPLApiClient: Configured API client instance
        """
        return FPLApiClient(cookies=cookies, x_api_authorization=x_api_authorization)
    
    @api.model
    def get_data_service(self, cookies=None, x_api_authorization=None):
        """
        Get a configured FPL Data Service
        
        Args:
            cookies (str): Authentication cookies (optional)
            x_api_authorization (str): Authorization header (optional)
            
        Returns:
            FPLDataService: Configured data service instance
        """
        api_client = self.get_api_client(cookies=cookies, x_api_authorization=x_api_authorization)
        return FPLDataService(api_client)
    
    @api.model
    def sync_from_fpl_api(self, endpoint_method, *args, **kwargs):
        """
        Generic method to sync data from FPL API
        
        Args:
            endpoint_method (str): Name of the API client method to call
            *args: Positional arguments for the method
            **kwargs: Keyword arguments for the method
            
        Returns:
            dict: API response data
        """
        try:
            api_client = self.get_api_client()
            method = getattr(api_client, endpoint_method)
            return method(*args, **kwargs)
        except FPLApiException as e:
            _logger.error(f"FPL API sync failed for {endpoint_method}: {str(e)}")
            raise
        except AttributeError:
            _logger.error(f"Unknown API method: {endpoint_method}")
            raise ValueError(f"Unknown API method: {endpoint_method}")

    @api.model
    def get_pulse_live_client(self):
        """
        Get a configured Pulse Live API client (Premier League standings/team-form)

        Returns:
            FPLPulseLiveApiClient: Configured API client instance
        """
        return FPLPulseLiveApiClient()

    @api.model
    def sync_from_pulse_live_api(self, endpoint_method, *args, **kwargs):
        """
        Generic method to sync data from the Pulse Live API

        Args:
            endpoint_method (str): Name of the FPLPulseLiveApiClient method to call
            *args: Positional arguments for the method
            **kwargs: Keyword arguments for the method

        Returns:
            dict: API response data
        """
        try:
            api_client = self.get_pulse_live_client()
            method = getattr(api_client, endpoint_method)
            return method(*args, **kwargs)
        except FPLPulseLiveApiException as e:
            _logger.error(f"Pulse Live API sync failed for {endpoint_method}: {str(e)}")
            raise
        except AttributeError:
            _logger.error(f"Unknown Pulse Live API method: {endpoint_method}")
            raise ValueError(f"Unknown Pulse Live API method: {endpoint_method}")

    def sync_authenticated_data(self, endpoint_method, cookies, x_api_authorization, *args, **kwargs):
        """
        Sync data from authenticated FPL API endpoints
        
        Args:
            endpoint_method (str): Name of the API client method to call
            cookies (str): Authentication cookies
            x_api_authorization (str): Authorization header
            *args: Positional arguments for the method
            **kwargs: Keyword arguments for the method
            
        Returns:
            dict: API response data
        """
        try:
            api_client = self.get_api_client(cookies=cookies, x_api_authorization=x_api_authorization)
            method = getattr(api_client, endpoint_method)
            return method(*args, **kwargs)
        except FPLApiException as e:
            _logger.error(f"FPL API sync failed for {endpoint_method}: {str(e)}")
            raise
        except AttributeError:
            _logger.error(f"Unknown API method: {endpoint_method}")
            raise ValueError(f"Unknown API method: {endpoint_method}")          