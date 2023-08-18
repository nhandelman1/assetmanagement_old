import requests
import datetime


########################################################################################################################
# class Base
# The purpose of subclasses is to make an http request to IEX cloud servers and receive a response. Since they all have
# the same purpose, functionality is abstracted to this base class where possible.
#
# No subclass will override the __init__ function.
#
# Some classes (see 'APISystemMetaData' and 'Account') do not have any endpoints that have required or optional
# parameters and are free to make an http request to and receive a response from. Most classes do and are not free,
# so they have functions with '_params' appended that returns two dictionaries.
# The first dictionary (see 'info_params' in this class) contains a note and cost for each endpoint.
# The second dictionary is created by each endpoint function and returns any required or optional parameters as keys,
# along with the possible values for those parameters as values. Certain key/value pairs have special meaning:
#       ticker-*: (Stocks, ETFs) (the user chooses and passes a single Stock or ETF ticker/symbol. * is 1,2,3...)
#       date-*: (min_date, max_date) (the user chooses and passes a single date bounded by the given min and max. * is
#                1,2,3...)
# Date values in the second dictionary are specified as strings with format YYYYMMDD or YYYYMMD.
# If the values passed are not valid, IEX Cloud will return an HTTP Error Code (see variable _IEXCloudHTTPErrorCodes)
#
# See function do_request. Every HTTP request to IEX cloud has a similar format. Most are GET calls that require the
# IEX cloud publishable key. A few are POST calls. A few require the IEX cloud secret key. After a successful request,
# the function returns a dictionary or a list (of dictionaries or strings). After an unsuccessful request, the function
# returns an error string.
#
# Endpoint function argument is *args but for now, the only expected argument is a dictionary with the same keys as the
# second dictionary in the associated '_params' function. Any date values in the dictionary must be string with format
# YYYYMMDD or YYYYMMD.
# IEX Cloud returns a response with two parts to consider. The first part is a status code, which needs to be checked
# against the _IEXCloudHTTPErrorCodes dictionary. If the status code is not in the dictionary, then no error occurred
# during the request. The second part is the data, which is either a dictionary, a list of dictionaries, a list of
# strings, a single string or a single number. Endpoint functions in sub classes may alter the response returned from
# IEX cloud. APISystemMetadata and Account endpoint functions return a dictionary or a single string. All other endpoint
# functions will always return either a list of dictionary(ies), list of string(s), a list of number(s) or a single
# string. Lists are valid data. A single string is an error string, and should not be considered as valid data.
########################################################################################################################
class Base:
    ENV_URL_DICT = {
        "Production": "https://cloud.iexapis.com/",
        "Sandbox": "https://sandbox.iexapis.com/"
    }

    VERSION_DICT = {
        "Stable": "stable"
    }

    _IEXCloudHTTPErrorCodes = {
        400: "Incorrect Values, No Symbol, Type Required",
        401: "Authorization Restricted, Authorization Required, Restricted, No Key, Secret Key Required, Denied Referer",
        402: "Over Limit, Free tier not allowed, Tier not allowed",
        403: "Authorization Invalid, Disabled Key, Invalid Key, Test token in production, Production token in sandbox, "
             "Circuit Breaker, Inactive",
        404: "Unknown Symbol, Not Found",
        413: "Max Types",
        429: "Too many requests",
        451: "Enterprise Permission Required",
        500: "System Error"
    }

    MAJOR_ENDPOINTS = ["Stock", "Corporate Actions", "Market Info", "Treasuries", "Commodities", "Economic Data",
                       "Reference Data"]

    def __init__(self, env_url_key, version_key, secret_key, publishable_key):
        self.env_version_str = self.ENV_URL_DICT[env_url_key] + self.VERSION_DICT[version_key]
        self.secret_key = secret_key
        self.publishable_key = publishable_key

    @staticmethod
    def previous_dates(num):
        date = datetime.date.today()
        date_list = []
        for i in range(num):
            temp = date - datetime.timedelta(days=i + 1)
            date_list.append(str(temp.year) + str(temp.month) + str(temp.day))
        return date_list

    @staticmethod
    def clean_keys(dict_list, clean_keys):
        for d in dict_list:
            for k in clean_keys:
                d.pop(k, "")
        return dict_list

    @staticmethod
    def ms_epoch_to_datetime_str(dict_list, ms_epoch_keys):
        for d in dict_list:
            for k in ms_epoch_keys:
                if k in d.keys() and d[k] is not None:
                    d[k] = datetime.datetime.fromtimestamp(d[k]/1000).strftime("%Y-%m-%d %H:%M:%S.%f")
        return dict_list

    @staticmethod
    def num_str_list(start, end):
        nums = list(range(start, end))
        return [str(x) for x in nums]

    @staticmethod
    def info_params(note, cost):
        return {"note": note, "cost": cost}

    def endpoints(self):
        return {}

    def set_account_endpoint(self):
        self.__class__ = Account

    def set_major_endpoint(self, major_endpoint):
        if major_endpoint == "Stock":
            self.__class__ = Stock
        elif major_endpoint == "Corporate Actions":
            self.__class__ = CorporateActions
        elif major_endpoint == "Market Info":
            self.__class__ = MarketInfo
        elif major_endpoint == "Treasuries":
            self.__class__ = Treasuries
        elif major_endpoint == "Commodities":
            self.__class__ = Commodities
        elif major_endpoint == "Economic Data":
            self.__class__ = EconomicData
        elif major_endpoint == "Reference Data":
            self.__class__ = ReferenceData
        else:
            self.__class__ = Base

    def time_series_endpoint(self, endpoint, param_dict, symbol_key="symbol", require_sk=False, is_get=True):
        from_date = param_dict["date-1"]
        to_date = param_dict["date-2"]

        if None in [from_date, to_date]:
            return "Date not provided for both date parameters."
        elif from_date > to_date:
            return "From-date must be equal to or less than to-date"

        symbol = param_dict.get(symbol_key)
        param_str = "from=" + from_date + "&to=" + to_date

        return self.do_request("/time-series/" + endpoint + symbol, param_str, require_sk, is_get,
                               ms_epoch_time_keys=["date", "updated"])

    # data_points endpoints return a single string from IEX Cloud.
    # This function will return a list of that string if the request was successful. Otherwise will return the error
    # string returned from do_request().
    def data_points_endpoint(self, endpoint, param_dict, symbol_key="symbol", require_sk=False, is_get=True):
        symbol = param_dict.get(symbol_key)
        res = self.do_request("/data-points/" + endpoint + symbol, None, require_sk, is_get)

        if isinstance(res, str) and "Full Request:" in res:
            return res
        else:
            return [res]

    def do_request(self, endpoint, param_str, require_sk, is_get, clean_keys=(), ms_epoch_time_keys=()):
        full_query = self.env_version_str + endpoint

        if require_sk is not None:
            full_query += "?token="
            full_query += self.secret_key if require_sk else self.publishable_key

            if param_str is not None:
                full_query += "&"
                full_query += param_str

        response = requests.get(full_query) if is_get else requests.post(full_query)
        error_str = self._IEXCloudHTTPErrorCodes.get(response.status_code)
        if error_str is None:
            res = response.json()
            if isinstance(res, list):
                res = self.clean_keys(res, clean_keys)
                return self.ms_epoch_to_datetime_str(res, ms_epoch_time_keys)
            else:
                res = self.clean_keys([res], clean_keys)[0]
                return self.ms_epoch_to_datetime_str([res], ms_epoch_time_keys)[0]
        else:
            return "Full Request: " + full_query + "\n\nStatus Code Error: " + str(response.status_code) + \
                   " indicates one or more of the following issues with the request: " + error_str


class APISystemMetadata(Base):

    """
    {
        "status":"up",
        "version":"BETA",
        "time":1548097469618,
        "currentMonthAPICalls":13506406729
    }
    """
    def API_metadata(self):
        return super().do_request("/status", "", None, True, ms_epoch_time_keys=["time"])


########################################################################################################################
# class Account inherits Base
########################################################################################################################
class Account(Base):

    def account_base_request(self, endpoint, clean_keys=(), ms_epoch_time_keys=()):
        return super().do_request("/account/" + endpoint, None, True, True, clean_keys=clean_keys,
                                  ms_epoch_time_keys=ms_epoch_time_keys)

    '''
    {
        "payAsYouGoEnabled": true,
        "effectiveDate": 1547590582000,
        "endDateEffective": 1547830921000,
        "subscriptionTermType": "monthly",
        "tierName": "launch",
        "messageLimit": 1000000000,
        "messagesUsed": 215141655,
        "circuitBreaker": 3000000000
    }
    '''
    def account_metadata(self):
        return self.account_base_request("metadata", ms_epoch_time_keys=["effectiveDate", "endDateEffective"])

    '''
    {
        "monthlyUsage": 215200,
        "monthlyPayAsYouGo": 0,
        "dailyUsage": {
            "20190120": 115200, 
            "20190121": 100000
        },
        "tokenUsage": {
            "pk_123": 215200
        },
        "keyUsage": {
            "IEX_STATS": 0, 
            "EARNINGS": 115200, 
            "STOCK_QUOTES": 100000
        }
    }
    '''
    def monthly_message_usage(self):
        return self.account_base_request("usage/messages", clean_keys=["dailyUsage", "tokenUsage", "keyUsage"])


########################################################################################################################
# class StockPrices inherits Base
# Includes IEX categories: Stock Prices, Stock Profiles, Stock Fundamentals, Stock Research,
#    Social Sentiment, Options, CEO compensation
########################################################################################################################
class Stock(Base):

    def stock_price_base_request(self, endpoint, param_str, clean_keys=(), ms_epoch_time_keys=()):
        return super().do_request("/stock/" + endpoint, param_str, False, True, clean_keys=clean_keys,
                                  ms_epoch_time_keys=ms_epoch_time_keys)

    def endpoints(self):
        return [
            {"name": "Historical Daily", "param_func": self.historical_daily_params, "api_func": self.historical_daily},
            {"name": "Historical Minute 1 Day", "param_func": self.historical_minute_1d_params, "api_func": self.historical_minute_1d},
            {"name": "Current Day Daily", "param_func": self.current_daily_params, "api_func": self.current_daily},
            {"name": "Current Day 1 Minute", "param_func": self.current_day_minute_params, "api_func": self.current_day_minute},
            {"name": "Company", "param_func": self.company_params, "api_func": self.company},
            {"name": "Insider Top 10", "param_func": self.top_10_insiders_params, "api_func": self.top_10_insiders},
            {"name": "Insider Summary 6 Months", "param_func": self.insider_summary_6_months_params, "api_func": self.insider_summary_6_months},
            {"name": "Insider Transactions 12 Months", "param_func": self.insider_transactions_12_months_params, "api_func": self.insider_transactions_12_months},
            {"name": "Peer Group", "param_func": self.peer_group_params, "api_func": self.peer_group},
            {"name": "Balance Sheet", "param_func": self.balance_sheet_params, "api_func": self.balance_sheet},
            {"name": "Cash Statement", "param_func": self.cash_statement_params, "api_func": self.cash_statement},
            {"name": "Income Statement", "param_func": self.income_statement_params, "api_func": self.income_statement},
            {"name": "Basic Dividends", "param_func": self.basic_dividend_params, "api_func": self.basic_dividend},
            {"name": "Earnings", "param_func": self.earnings_params, "api_func": self.earnings},
            {"name": "Basic Splits", "param_func": self.basic_splits_params, "api_func": self.basic_splits},
            {"name": "Analyst Recommendation", "param_func": self.analyst_recommendations_params, "api_func": self.analyst_recommendations},
            {"name": "Fund Ownership", "param_func": self.fund_ownership_params, "api_func": self.fund_ownership},
            {"name": "Institutional Ownership", "param_func": self.institutional_ownership_params, "api_func": self.institutional_ownership},
            {"name": "Price Target", "param_func": self.price_target_params, "api_func": self.price_target},
            {"name": "Social Sentiment", "param_func": self.social_sentiment_params, "api_func": self.social_sentiment},
            {"name": "Options", "param_func": self.options_params, "api_func": self.options},
            {"name": "CEO Compensation", "param_func": self.ceo_compensation_params, "api_func": self.ceo_compensation},
        ]

    ####################################################################################################################
    # Historical Daily
    ####################################################################################################################

    def historical_daily_params(self):
        return super().info_params(
            "15 years of Adjusted and unadjusted historical OHLCV. Use this endpoint for previous 1d or more. Most "
            "recent trading day available at 4AM ET the following day.", "10 per symbol per day"), \
               {"ticker-1": ("Stocks", "ETFs"), "range": ["max", "5y", "2y", "1y", "ytd", "6m", "3m", "1m", "5d", "1d"]}
    '''
    /chart
    [
        {
            "date": "2017-04-03",
            "open": 143.1192,
            "high": 143.5275,
            "low": 142.4619,
            "close": 143.1092,
            "volume": 19985714,
            "uOpen": 143.1192,
            "uHigh": 143.5275,
            "uLow": 142.4619,
            "uClose": 143.1092,
            "uVolume": 19985714,
            "change": 0.039835,
            "changePercent": 0.028,
            "label": "Apr 03, 17",
            "changeOverTime": -0.0039
        } // , { ... }
    ]
    
    /previous
    {
      "date": "2019-03-25",
      "open": 191.51,
      "close": 188.74,
      "high": 191.98,
      "low": 186.6,
      "volume": 43845293,
      "uOpen": 191.51,
      "uClose": 188.74,
      "uHigh": 191.98,
      "uLow": 186.6,
      "uVolume": 43845293,
      "change": 0,
      "changePercent": 0,
      "changeOverTime": 0,
      "symbol": "AAPL"
    }
    '''
    def historical_daily(self, *args):
        param_dict = args[0]
        symbol = param_dict.get("ticker-1")
        rng = param_dict.get("range")
        if rng == "1d":
            endpoint = symbol + "/previous"
        else:
            rng = "" if rng is None else "/" + rng
            endpoint = symbol + "/chart" + rng

        res = self.stock_price_base_request(endpoint, None, ["changeOverTime", "label", "change", "changePercent", "symbol"])
        if isinstance(res, dict):
            res = [res]
        return res

    ####################################################################################################################
    # Historical Minute 1 Day
    ####################################################################################################################

    def historical_minute_1d_params(self):
        return super().info_params(
            "Only trailing 30 calendar days available. This function retrieves minute data for the given date.",
            "50 per symbol per day"), {"ticker-1": ("Stocks", "ETFs"), "dates": super().previous_dates(30)}

    '''
    [
        {
            "date": "2017-12-15",
            "minute": "09:30",
            "label": "09:30 AM",
            "marketOpen": 143.98,
            "marketClose": 143.775,
            "marketHigh": 143.98,
            "marketLow": 143.775,
            "marketAverage": 143.889,
            "marketVolume": 3070,
            "marketNotional": 441740.275,
            "marketNumberOfTrades": 20,
            "marketChangeOverTime": -0.004,
            "high": 143.98,
            "low": 143.775,
            "open": 143.98,
            "close": 143.775,
            "average": 143.889,
            "volume": 3070,
            "notional": 441740.275,
            "numberOfTrades": 20,
            "changeOverTime": -0.0039,
        } // , { ... }
    ]
    
    The non-market attributes are for IEX data only. 
    '''
    def historical_minute_1d(self, *args):
        param_dict = args[0]
        symbol = param_dict.get("ticker-1")
        date = param_dict.get("dates")
        if date is None:
            return "No date provided."
        return self.stock_price_base_request(symbol + "/chart/date/" + date, None,
            ["label", "marketAverage", "marketNotional", "marketChangeOverTime", "average", "notional", "changeOverTime"])

    ####################################################################################################################
    # Current Daily
    ####################################################################################################################

    def current_daily_params(self):
        return super().info_params("15 minute delayed current day unadjusted OHLC.", "2 per symbol"), \
               {"ticker-1": ("Stocks", "ETFs")}

    '''
    {
      "open": {
        "price": 154,
        "time": 1506605400394
      },
      "close": {
        "price": 153.28,
        "time": 1506605400394
      },
      "high": 154.80,
      "low": 153.25
    }
    '''
    def current_daily(self, *args):
        param_dict = args[0]
        symbol = param_dict.get("ticker-1")
        res = self.stock_price_base_request(symbol + "/ohlc", None)
        if isinstance(res, dict):
            res["open"] = res["open"]["price"]
            res["close"] = res["close"]["price"]
            return res
        else:
            return res

    ####################################################################################################################
    # Current Day Minutes
    ####################################################################################################################

    def current_day_minute_params(self):
        return super().info_params("15 minute delayed current day minute OHLC.", "1 per symbol per minute up to 50"), \
               {"ticker-1": ("Stocks", "ETFs")}

    '''
    [
        {
            "date": "2017-12-15",
            "minute": "09:30",
            "label": "09:30 AM",
            "marketOpen": 143.98,
            "marketClose": 143.775,
            "marketHigh": 143.98,
            "marketLow": 143.775,
            "marketAverage": 143.889,
            "marketVolume": 3070,
            "marketNotional": 441740.275,
            "marketNumberOfTrades": 20,
            "marketChangeOverTime": -0.004,
            "high": 143.98,
            "low": 143.775,
            "open": 143.98,
            "close": 143.775,
            "average": 143.889,
            "volume": 3070,
            "notional": 441740.275,
            "numberOfTrades": 20,
            "changeOverTime": -0.0039,
        } // , { ... }
    ]

    The non-market attributes are for IEX data only. 
    '''
    def current_day_minute(self, *args):
        param_dict = args[0]
        symbol = param_dict.get("ticker-1")
        return self.stock_price_base_request(symbol + "/intraday-prices", None,
             ["label", "marketAverage", "marketNotional", "marketChangeOverTime", "average", "notional", "changeOverTime"])

    ####################################################################################################################
    # Company
    ####################################################################################################################

    def company_params(self):
        return super().info_params("Updates at 4 AM and 5 AM UTC daily.", "1 per symbol"),\
               {"ticker-1": ("Stocks", "ETFs")}

    '''
    {
      "symbol": "AAPL",
      "companyName": "Apple Inc.",
      "exchange": "NASDAQ",
      "industry": "Telecommunications Equipment",
      "website": "http://www.apple.com",
      "description": "Apple, Inc. engages in the design, manufacture, and marketing of mobile communication, 
      media devices, personal computers, and portable digital music players. It operates through the following 
      geographical segments: Americas, Europe, Greater China, Japan, and Rest of Asia Pacific. The Americas segment 
      includes North and South America. The Europe segment consists of European countries, as well as India, the Middle 
      East, and Africa. The Greater China segment comprises of China, Hong Kong, and Taiwan. The Rest of Asia Pacific 
      segment includes Australia and Asian countries. The company was founded by Steven Paul Jobs, Ronald Gerald Wayne, 
      and Stephen G. Wozniak on April 1, 1976 and is headquartered in Cupertino, CA.",
      "CEO": "Timothy Donald Cook",
      "securityName": "Apple Inc.",
      "issueType": "cs",
      "sector": "Electronic Technology",
      "primarySicCode": 3663,
      "employees": 132000,
      "tags": [
        "Electronic Technology",
        "Telecommunications Equipment"
      ],
      "address": "One Apple Park Way",
      "address2": null,
      "state": "CA",
      "city": "Cupertino",
      "zip": "95014-2083",
      "country": "US",
      "phone": "1.408.974.3123"
    }
    '''
    def company(self, *args):
        param_dict = args[0]
        symbol = param_dict.get("ticker-1")
        res = self.stock_price_base_request(symbol + "/company", None)
        if isinstance(res, str):
            return res
        else:
            return [res]

    ####################################################################################################################
    # Top 10 Insider Roster
    ####################################################################################################################

    def top_10_insiders_params(self):
        return super().info_params("Updates at 5 AM, 6AM ET daily", "5000 per symbol"), {"ticker-1": ("Stocks",)}

    '''
    [
        {
            entityName : "Random insider",
            position : 12345,
            reportDate : 1546387200000
        }
    ]
    '''
    def top_10_insiders(self, *args):
        param_dict = args[0]
        symbol = param_dict.get("ticker-1")
        return self.stock_price_base_request(symbol + "/insider-roster", None, ms_epoch_time_keys=["reportDate"])

    ####################################################################################################################
    # Insider Summary - Last 6 months
    ####################################################################################################################

    def insider_summary_6_months_params(self):
        return super().info_params("Updates at 5 AM, 6AM ET daily", "5000 per symbol"), {"ticker-1": ("Stocks",)}

    '''
    [
        {
            "fullName": "John Appleseed",
            "netTransacted": -15,
            "reportedTitle": "General Counsel",
            "totalBought": 0,
            "totalSold": -15
        },
    ]
    '''

    def insider_summary_6_months(self, *args):
        param_dict = args[0]
        symbol = param_dict.get("ticker-1")
        return self.stock_price_base_request(symbol + "/insider-summary", None)

    ####################################################################################################################
    # Insider Transactions - Last 12 months
    ####################################################################################################################

    def insider_transactions_12_months_params(self):
        return super().info_params("","50 per transaction"), {"ticker-1": ("Stocks",)}

    '''
    [
        {
            "effectiveDate": 1522540800000,
            "fullName": "Joe Smith",
            "reportedTitle": "Vice President",
            "tranPrice": 0,
            "tranShares": 10000,
            "tranValue": 0
        }
    ]
    '''
    def insider_transactions_12_months(self, *args):
        param_dict = args[0]
        symbol = param_dict.get("ticker-1")
        return self.stock_price_base_request(symbol + "/insider-transaction", None, ms_epoch_time_keys=["effectiveDate"])

    ####################################################################################################################
    # Peer Group
    ####################################################################################################################
    def peer_group_params(self):
        return super().info_params("Updates at 8AM UTC daily", "500 per call"), {"ticker-1": ("Stocks", "ETFs")}

    '''
    Response from IEX cloud:
    [
        "MSFT",
        "NOK",
        "IBM",
        "BBRY",
        "HPQ",
        "GOOGL",
        "XLK"
    ]
    '''
    def peer_group(self, *args):
        param_dict = args[0]
        symbol = param_dict.get("ticker-1")
        return self.stock_price_base_request(symbol + "/peers", None)

    ####################################################################################################################
    # Balance Sheet
    ####################################################################################################################

    def balance_sheet_params(self):
        return super().info_params(
            "Available quarterly (most recent 12) or annually (most recent 4). Updates at 8AM, 9AM UTC daily. Set "
            "quarterly to '' to choose annual.", "3000 per symbol per period"), \
               {"ticker-1": ("Stocks",), "quarter": [''] + super().num_str_list(1, 13), "annual": super().num_str_list(1, 5)}

    '''
    {
      "symbol": "AAPL",
      "balancesheet": [
        {
          "reportDate": "2017-03-31",
          "fiscalDate": "2017-03-31",
          "currency": "USD",
          "currentCash": 25913000000,
          "shortTermInvestments": 40388000000,
          "receivables": 23186000000,
          "inventory": 3956000000,
          "otherCurrentAssets": 12087000000,
          "currentAssets": 131339000000,
          "longTermInvestments": 170799000000,
          "propertyPlantEquipment": 41304000000,
          "goodwill": null,
          "intangibleAssets": null,
          "otherAssets": 22283000000,
          "totalAssets": 365725000000,
          "accountsPayable": 55888000000,
          "currentLongTermDebt": 8784000000,
          "otherCurrentLiabilities": 40230000000,
          "totalCurrentLiabilities": 116866000000,
          "longTermDebt": 93735000000,
          "otherLiabilities": 4268000000,
          "minorityInterest": 0,
          "totalLiabilities": 258578000000,
          "commonStock": 40201000000,
          "retainedEarnings": 70400000000,
          "treasuryStock": null,
          "capitalSurplus": null,
          "shareholderEquity": 107147000000,
          "netTangibleAssets": 107147000000
        } // , { ... }
      ]
    }
    '''
    def balance_sheet(self, *args):
        param_dict = args[0]
        symbol = param_dict.get("ticker-1")
        quarter = param_dict["quarter"]
        annual = param_dict["annual"]

        if quarter == '':
            param_str = "period=annual&last=" + annual
        else:
            param_str = "period=quarter&last=" + quarter

        res = self.stock_price_base_request(symbol + "/balance-sheet", param_str)
        if isinstance(res, dict):
            return res["balancesheet"]
        else:
            return res

    ####################################################################################################################
    # Cash Statement
    ####################################################################################################################

    def cash_statement_params(self):
        return super().info_params(
            "Available quarterly (most recent 12) or annually (most recent 4). Updates at 8AM, 9AM UTC daily. Set "
            "quarterly to '' to choose annual.", "1000 per symbol per period"), \
               {"ticker-1": ("Stocks",), "quarter": [''] + super().num_str_list(1, 13), "annual": super().num_str_list(1, 5)}

    '''
    {
      "symbol": "AAPL",
      "cashflow": [
        {
          "reportDate": "2018-09-30",
          "fiscalDate": "2018-09-30",
          "currency": "USD",
          "netIncome": 14125000000,
          "depreciation": 2754000000,
          "changesInReceivables": -9082000000,
          "changesInInventories": 1942000000,
          "cashChange": -6058000000,
          "cashFlow": 19523000000,
          "capitalExpenditures": -3041000000,
          "investments": -926000000,
          "investingActivityOther": 1566000000,
          "totalInvestingCashFlows": -3001000000,
          "dividendsPaid": -3530000000,
          "netBorrowings": -27000000,
          "otherFinancingCashFlows": -260000000,
          "cashFlowFinancing": -22580000000,
          "exchangeRateEffect": null
        } // , { ... }
      ]
    }
    '''
    def cash_statement(self, *args):
        param_dict = args[0]
        symbol = param_dict.get("ticker-1")
        quarter = param_dict["quarter"]
        annual = param_dict["annual"]

        if quarter == '':
            param_str = "period=annual&last=" + annual
        else:
            param_str = "period=quarter&last=" + quarter

        res = self.stock_price_base_request(symbol + "/cash_flow", param_str)
        if isinstance(res, dict):
            return res["cashflow"]
        else:
            return res

    ####################################################################################################################
    # Income Statement
    ####################################################################################################################

    def income_statement_params(self):
        return super().info_params(
            "Available quarterly (most recent 12) or annually (most recent 4). Updates at 8AM, 9AM UTC daily. Set "
            "quarterly to '' to choose annual.", "1000 per symbol per period"), \
               {"ticker-1": ("Stocks",), "quarter": [''] + super().num_str_list(1, 13), "annual": super().num_str_list(1, 5)}

    '''
    {
      "symbol": "AAPL",
      "income": [
        {
          "reportDate": "2017-03-31",
          "fiscalDate": "2017-03-31",
          "currency": "USD",
          "totalRevenue": 62681000000,
          "costOfRevenue": 39086000000,
          "grossProfit": 23595000000,
          "researchAndDevelopment": 3750000000,
          "sellingGeneralAndAdmin": 4216000000,
          "operatingExpense": 47052000000,
          "operatingIncome": 15629000000,
          "otherIncomeExpenseNet": 792000000,
          "ebit": 15629000000,
          "interestIncome": 868000000,
          "pretaxIncome": 16421000000,
          "incomeTax": 2296000000,
          "minorityInterest": 0,
          "netIncome": 14125000000,
          "netIncomeBasic": 14125000000
        } // , { ... }
      ]
    }
    '''
    def income_statement(self, *args):
        param_dict = args[0]
        symbol = param_dict.get("ticker-1")
        quarter = param_dict["quarter"]
        annual = param_dict["annual"]

        if quarter == '':
            param_str = "period=annual&last=" + annual
        else:
            param_str = "period=quarter&last=" + quarter

        res = self.stock_price_base_request(symbol + "/income", param_str)
        if isinstance(res, dict):
            return res["income"]
        else:
            return res

    ####################################################################################################################
    # Basic Dividend
    ####################################################################################################################

    def basic_dividend_params(self):
        return super().info_params(
            "5 years of dividend data for US equities, ETFs and mutual funds. Updated at 9AM UTC daily. Use "
            "'Advanced Dividends' for 13+ years of comprehensive dividend data.", "10 per symbol per period"), \
               {"ticker-1": ("Stocks", "ETFs"), "range": ["5y", "2y", "1y", "ytd", "6m", "3m", "1m", "next"]}

    '''
    [
        {
            "symbol": "AAPL",
            "exDate": "2017-08-10",
            "paymentDate": "2017-08-17",
            "recordDate": "2017-08-14",
            "declaredDate": "2017-08-01",
            "amount": 0.63,
            "flag": "Dividend income",
            "currency": "USD",
            "description": "Apple declares dividend of .63",
            "frequency": "quarterly"
        } // , { ... }
    ]
    '''
    def basic_dividend(self, *args):
        param_dict = args[0]
        symbol = param_dict.get("ticker-1")
        rng = param_dict.get("range")

        return self.stock_price_base_request(symbol + "/dividends/" + rng, None)

    ####################################################################################################################
    # Earnings and Upcoming Earnings Estimates
    ####################################################################################################################

    def earnings_params(self):
        return super().info_params(
            "Available quarterly (most recent 4), annually (most recent 4) and estimate for next quarter and annual. "
            "Updates at 9AM, 11AM, 12PM UTC daily. Set quarterly to '' to choose annual.", "1000 per symbol per period"), \
               {"ticker-1": ("Stocks",), "quarter": [''] + super().num_str_list(1, 5) + ["upcoming"],
                "annual": super().num_str_list(1, 5) + ["upcoming"]}

    '''
    {
        "symbol": "AAPL",
        "earnings": [
            {
                "actualEPS": 2.46,
                "consensusEPS": 2.36,
                "announceTime": "AMC",
                "numberOfEstimates": 34,
                "EPSSurpriseDollar": 0.1,
                "EPSReportDate": "2019-04-30",
                "fiscalPeriod": "Q1 2019",
                "fiscalEndDate": "2019-03-31",
                "yearAgo": 2.73,
                "yearAgoChangePercent": -0.0989
            },
            {
                "actualEPS": 4.18,
                "consensusEPS": 4.17,
                "announceTime": "AMC",
                "numberOfEstimates": 35,
                "EPSSurpriseDollar": 0.01,
                "EPSReportDate": "2019-01-29",
                "fiscalPeriod": "Q4 2018",
                "fiscalEndDate": "2018-12-31",
                "yearAgo": 3.89,
                "yearAgoChangePercent": 0.0746
            }
        ]
    }
    
    {
      "symbol": "AAPL",
      "estimates": [
        {
          "consensusEPS": 2.02,
          "announceTime": "AMC",
          "numberOfEstimates": 14,
          "reportDate": "2017-04-15",
          "fiscalPeriod": "Q2 2017",
          "fiscalEndDate": "2017-03-31",
          "currency": "USD"
        }
      ]
    }
    '''
    def earnings(self, *args):
        param_dict = args[0]
        symbol = param_dict.get("ticker-1")
        quarter = param_dict["quarter"]
        annual = param_dict["annual"]

        if quarter == "upcoming" or (quarter == '' and annual == "upcoming"):
            if quarter == 'upcoming':
                param_str = "period=quarter" + annual
            else:
                param_str = "period=annual" + quarter

            res = self.stock_price_base_request(symbol + "/estimates", param_str)
            if isinstance(res, dict):
                return res["estimates"]
            else:
                return res
        else:
            if quarter == '':
                param_str = "period=annual&last=" + annual
            else:
                param_str = "period=quarter&last=" + quarter

            res = self.stock_price_base_request(symbol + "/earnings", param_str)
            if isinstance(res, dict):
                return res["earnings"]
            else:
                return res

    ####################################################################################################################
    # Basic Splits
    ####################################################################################################################

    def basic_splits_params(self):
        return super().info_params(
            "5 years of split data for US equities, ETFs and mutual funds. Updated at 9AM UTC daily. Use "
            "'Advanced Splits' for 12+ years of comprehensive split data.", "10 per symbol per record"), \
               {"ticker-1": ("Stocks", "ETFs"), "range": ["5y", "2y", "1y", "ytd", "6m", "3m", "1m", "next"]}

    '''
    [
        {
            "exDate": "2017-08-10",
            "declaredDate": "2017-08-01",
            "ratio": 0.142857,
            "toFactor": 7,
            "fromFactor": 1,
            "description": "7-for-1 split"
        } // , { ... }
    ]
    '''
    def basic_splits(self, *args):
        param_dict = args[0]
        symbol = param_dict.get("ticker-1")
        rng = param_dict.get("range")

        return self.stock_price_base_request(symbol + "/splits/" + rng, None)

    ####################################################################################################################
    # Analyst Recommendations
    ####################################################################################################################

    def analyst_recommendations_params(self):
        return super().info_params(
            "Data from the last 4 months. Updates at 9AM, 11AM, 12PM UTC daily.", "1000 per symbol"), \
               {"ticker-1": ("Stocks",)}

    '''
    [
        {
            "consensusEndDate": 1542240000000,
            "consensusStartDate": 1541462400000,
            "corporateActionsAppliedDate": 1055721600000,
            "ratingBuy": 8,
            "ratingOverweight": 2,
            "ratingHold": 1,
            "ratingUnderweight": 1,
            "ratingSell": 1,
            "ratingNone": 2,
            "ratingScaleMark": 1.042857
        }
    ]
    '''
    def analyst_recommendations(self, *args):
        param_dict = args[0]
        symbol = param_dict.get("ticker-1")

        return self.stock_price_base_request(symbol + "/recommendation-trends", None,
                         ms_epoch_time_keys=["consensusEndDate", "consensusStartDate", "corporateActionsAppliedDate"])

    ####################################################################################################################
    # Fund Ownership
    ####################################################################################################################

    def fund_ownership_params(self):
        return super().info_params(
            "Top 10 fund holders, meaning any firm not defined as buy-side or sell-side such as mutual funds, pension "
            "funds, endowments, investment firms, and other large entities that manage funds on behalf of others. "
            "Updates at 5AM, 6AM ET daily", "10000 per symbol per period"), {"ticker-1": ("Stocks", "ETFs")}

    '''
    [
        {
            "adjHolding": 150,
            "adjMv": 87,
            "entityProperName": "Random Corporation",
            "reportDate": 1490918400000,
            "reportedHolding": 100,
            "reportedMv": 100 
        }
    ]
    '''

    def fund_ownership(self, *args):
        param_dict = args[0]
        symbol = param_dict.get("ticker-1")

        return self.stock_price_base_request(symbol + "/fund-ownership", None, ms_epoch_time_keys=["reportDate"])

    ####################################################################################################################
    # Institutional Ownership
    ####################################################################################################################

    def institutional_ownership_params(self):
        return super().info_params(
            "Returns the top 10 institutional holders, defined as buy-side or sell-side firms. Updates at 5AM, 6AM ET "
            "daily", "10000 per symbol per period"), {"ticker-1": ("Stocks", "ETFs")}

    '''
    [
        {
            "adjHolding": 10085320,
            "adjMv": 59188155,
            "entityProperName": "Random Corp.",
            "reportDate": 1548892800000,
            "reportedHolding": 2085320
        }
    ]
    '''

    def institutional_ownership(self, *args):
        param_dict = args[0]
        symbol = param_dict.get("ticker-1")

        return self.stock_price_base_request(symbol + "/institutional-ownership", None, ms_epoch_time_keys=["reportDate"])

    ####################################################################################################################
    # Price Target
    ####################################################################################################################

    def price_target_params(self):
        return super().info_params(
            "Provides the latest avg, high, and low analyst price target for a symbol. Updates at 10AM, 11AM, 12PM UTC "
            "daily", "500 per symbol"), {"ticker-1": ("Stocks",)}

    '''
    {
      "symbol": "AAPL",
      "updatedDate": "2019-01-30",
      "priceTargetAverage": 178.59,
      "priceTargetHigh": 245,
      "priceTargetLow": 140,
      "numberOfAnalysts": 34,
      "currency": "USD"
    }
    '''
    def price_target(self, *args):
        param_dict = args[0]
        symbol = param_dict.get("ticker-1")

        res = self.stock_price_base_request(symbol + "/price-target", None)
        if isinstance(res, str):
            return res
        else:
            return [res]

    ####################################################################################################################
    # Social Sentiment
    ####################################################################################################################

    def social_sentiment_params(self):
        return super().info_params(
            "Social sentiment date from StockTwits. Daily or Minute. Not available after June 1, 2020.",
            "100 per symbol for daily sentiment. 200 per symbol per day for minute sentiment."), \
               {"ticker-1": ("Stocks", "ETFs"), "type": ["daily", "minute"], "date-1": (None, "2020-06-01")}

    '''
    // Daily
    {
      "sentiment": 0.20365833333333336,
      "totalScores": 24,
      "positive": 0.88,
      "negative": 0.12
    }
    
    // By minute
    [
      {
        "sentiment": 0.23336666666666664,
        "totalScores": 3,
        "positive": 1,
        "negative": 0,
        "minute": "1258"
      },
    ]
    '''
    def social_sentiment(self, *args):
        param_dict = args[0]
        date = param_dict["date-1"]
        if date is None:
            return "No date provided."

        symbol = param_dict.get("ticker-1")
        type = param_dict["type"]
        res = self.stock_price_base_request(symbol + "/sentiment/" + type + "/" + date, None)
        if isinstance(res, dict):
            return [res]
        else:
            return res

    ####################################################################################################################
    # Options
    ####################################################################################################################

    def options_params(self):
        return super().info_params(
            "End of day options data. Not available until 9:30 AM ET on the next trading day. Expiration Date is by "
            "YYYYMM. A date returned as YYYYMMDD will be truncated to YYYYMM. Expiration dates seem to go back 14 "
            "months and forward 12 months.", "1000 per symbol per date"), \
               {"ticker-1": ("Stocks", "ETFs"), "date-1": (None, None), "side": ["", "call", "put"]}

    '''
    [
        {
            "symbol": "AAPL",
            "id": "AAPL20190621C00240000",
            "expirationDate": "20190621",
            "contractSize": 100,
            "strikePrice": 240,
            "closingPrice": 0.39,
            "side": "call",
            "type": "equity",
            "volume": 884,
            "openInterest": 12197,
            "bid": 0.38,
            "ask": 0.42,
            "lastUpdated": "2019-04-25",
            "isAdjusted": false
        },
    ]
    '''
    def options(self, *args):
        param_dict = args[0]
        date = param_dict["date-1"]
        if date is None:
            return "No date provided."

        symbol = param_dict.get("ticker-1")
        date = date[0:6]
        side = "" if param_dict["side"] == "" else "/" + param_dict["side"]

        return self.stock_price_base_request(symbol + "/options/" + date + side, None)

    ####################################################################################################################
    # CEO Compensation
    ####################################################################################################################
    def ceo_compensation_params(self):
        return super().info_params("CEO compensation for a company. Updates at 1AM daily", "20 per symbol"), \
               {"ticker-1": ("Stocks",)}

    '''
    {
        "symbol": "AVGO",
        "name": "Hock E. Tan",
        "companyName": "Broadcom Inc.",
        "location": "Singapore, Asia",
        "salary": 1100000,
        "bonus": 0,
        "stockAwards": 98322843,
        "optionAwards": 0,
        "nonEquityIncentives": 3712500,
        "pensionAndDeferred": 0,
        "otherComp": 75820,
        "total": 103211163,
        "year": "2017"
    }
    '''
    def ceo_compensation(self, *args):
        param_dict = args[0]
        symbol = param_dict.get("ticker-1")
        res = self.stock_price_base_request(symbol + "/ceo-compensation", None)
        if isinstance(res, str):
            return res
        else:
            return [res]


########################################################################################################################
# class CorporateActions inherits Base
########################################################################################################################
class CorporateActions(Base):

    def corporate_actions_base_request(self, endpoint, param_str, clean_keys=(), ms_epoch_time_keys=()):
        return super().do_request("/time-series/" + endpoint, param_str, False, True, clean_keys=clean_keys,
                                  ms_epoch_time_keys=ms_epoch_time_keys)

    def endpoints(self):
        return [
            {"name": "Advanced Dividends", "param_func": self.advanced_dividends_params, "api_func": self.advanced_dividends},
            {"name": "Advanced Splits", "param_func": self.advanced_splits_params, "api_func": self.advanced_splits}
        ]

    ####################################################################################################################
    # Advanced Dividends
    ####################################################################################################################

    def advanced_dividends_params(self):
        return super().info_params(
            "Detailed dividend information going back 12+ years for 39000 US equities, mutual funds, ADRs and ETFs. "
            "Updated 5AM, 10AM, 8PM UTC.", "Warning; Expensive. 75000 per dividend returned."), \
               {"ticker-1": ("Stocks", "ETFs")}
    '''
    [
      {
        "symbol": "ASML",
        "exDate": "2019-11-04",
        "recordDate": "2019-11-05",
        "paymentDate": "2019-11-15",
        "announceDate": "2019-10-16",
        "currency": "USD",
        "frequency": "semi-annual",
        "amount": "1.1697",
        "description": "New York Shares",
        "flag": "Cash",
        "securityType": "Depository Receipts",
        "notes": "(As on 04/11/2019) USDRJPM<BR>Security Name: ASML HOLDING NV (ASML US) - ADR - Final Announcement<BR>CUSIP: N07059210<BR>DR Record Date:November 05, 2019<BR>DR Payment/Value Date:November 15, 2019<BR>Foreign Payment Date:November 15, 2019<BR>Euro per foreign share 1.05<BR>DR Ratio 1 : 1<BR>Euro per DR 1.05<BR>Foreign Exchange Date<BR>Final Foreign Exchange Rate: 1.114<BR>Inclusive of a fee of 0.0000000<BR>All amounts are in USD<BR>Withholding Tax Rate 15%<BR>Rate per DR 1.1697000<BR>Withholding Amount 0.1754550<BR>Dividend Fee 0.0000000<BR>DSC 0.0000000<BR>Final Dividend Rate per DR 0.9942450<BR><BR>(As on 04/11/2019)USDIVINVEST <BR>Symbol ASML<BR>New.Amount 0.9942<BR>Exchange NASDAQ<BR>Div.DecDate 00-00-0000<BR>Div.ExDate 11/04/2019<BR>Div.RecDate 11/05/2019<BR>Div.PayDate 11-15-2019<BR><BR>(As on 01/11/2019)DEDIVS<BR>Ex date :04/11/2019<BR><BR>(As on 16/10/2019 ) USDRJPM_APPX<BR>Security Name: ASML HOLDING NV (ASML US) - ADR - Initial Announcement<BR>CUSIP: N07059210<BR>DR Record Date:November 05, 2019<BR>DR Payment/Value Date: November 15, 2019<BR>Foreign Exchange Date: 10/15/2019<BR>F X Conversion Rate :1.1034<BR>All amounts are in USD:<BR>Withholding Tax Rate 15%<BR>Rate per DR 1.1585700<BR>Withholding Amount 0.1737855<BR>Dividend Fee 0.0000000<BR>DSC 0.0000000<BR>Approximate Dividend Rate per DR 0.9847845<BR><BR>(As on 16/10/2019)USDIVINVEST<BR>Symbol ASML<BR>New.Amount 0.9848<BR>Exchange NASDAQ<BR>Div.DecDate 00-00-0000<BR>Div.ExDate 11/04/2019<BR>Div.RecDate 11/05/2019<BR>Div.PayDate 11-15-2019<BR>",
        "figi": "BBG000K6MRN4",
        "lastUpdated": "2019-11-05",
        "countryCode": "US",
        "parValue": "",
        "parValueCurrency": "USD",
        "netAmount": "0.994245",
        "grossAmount": "1.1697",
        "marker": "Interim",
        "taxRate": "15",
        "fromFactor": "",
        "toFactor": "",
        "adrFee": "",
        "coupon": "",
        "declaredCurrencyCD": "",
        "declaredGrossAmount": "",
        "isNetInvestmentIncome": 1,
        "isDAP": 1,
        "isApproximate": 1,
        "fxDate": "2019-11-15",
        "secondPaymentDate": null,
        "secondExDate": null,
        "fiscalYearEndDate": "2019-12-31",
        "periodEndDate": "2019-06-30",
        "optionalElectionDate": null,
        "toDate": null,
        "registrationDate": null,
        "installmentPayDate": null,
        "declaredDate": "2019-10-16",
        "refid": "1691530",
        "created": "2019-10-17",
        "id": "ADVANCED_DIVIDENDS",
        "source": "IEX Cloud",
        "key": "US",
        "subkey": "ASML",
        "date": 1572825600000,
        "updated": 1573134765000
      },
      // ...
    ]
    '''
    def advanced_dividends(self, *args):
        param_dict = args[0]
        symbol = param_dict.get("ticker-1")
        return self.corporate_actions_base_request("advanced_dividends/" + symbol, None,
                                                   ms_epoch_time_keys=["date", "updated"])

    ####################################################################################################################
    # Advanced Splits
    ####################################################################################################################
    def advanced_splits_params(self):
        return super().info_params(
            "Detailed split information going back 12+ years. Updated 5AM, 10AM, 8PM UTC daily.",
            "Warning; Expensive. 75000 per dividend returned."), {"ticker-1": ("Stocks", "ETFs")}

    '''
    [
      {
        "symbol": "CRPYF",
        "exDate": "2020-01-15",
        "recordDate": "2020-01-14",
        "paymentDate": "2020-01-15",
        "fromFactor": 10,
        "toFactor": 1,
        "ratio": 10,
        "description": "Ordinary Shares",
        "splitType": "Reverse Split",
        "flag": "Stock",
        "securityType": "Equity Shares",
        "notes": "(As on 07/11/2019) ZAJSE<BR>Share Consolidation<BR><BR>It is intended that following completion of 
            the Proposed Transaction, the Company s issued share capital will be consolidated on the basis of 10 
            Ordinary Shares of 1 pence each for 1 new ordinary share of 10 pence (a  Consolidated Ordinary Share ), 
            by reference to the Capital & Regional Shares in issue at 6.00 p.m. on 14 January 2020 on the UK Register",
        "figi": "BBG000CQTXJ4",
        "lastUpdated": "2019-11-08",
        "countryCode": "US",
        "parValue": 0.01,
        "parValueCurrency": "GBP",
        "oldParValue": 0.01,
        "oldParValueCurrency": "GBP",
        "refid": "6057319",
        "created": "2019-11-07",
        "id": "ADVANCED_SPLITS",
        "source": "IEX Cloud",
        "key": "CRPYF",
        "subkey": "6057319",
        "date": 1579046400000,
        "updated": 1574689890000
      }
      // ...
    ]
    '''
    def advanced_splits(self, *args):
        param_dict = args[0]
        symbol = param_dict.get("ticker-1")
        return self.corporate_actions_base_request("advanced_splits/" + symbol, None,
                                                   ms_epoch_time_keys=["date", "updated"])


########################################################################################################################
# class MarketInfo inherits Base
########################################################################################################################
class MarketInfo(Base):

    def market_info_base_request(self, endpoint, param_str, clean_keys=(), ms_epoch_time_keys=()):
        return super().do_request("/stock/market/" + endpoint, param_str, False, True, clean_keys=clean_keys,
                                  ms_epoch_time_keys=ms_epoch_time_keys)

    def endpoints(self):
        return [
            {"name": "Earnings Today", "param_func": self.earnings_today_params, "api_func": self.earnings_today},
            {"name": "Today IPO Calendar", "param_func": self.today_ipo_calendar_params, "api_func": self.today_ipo_calendar},
            {"name": "Upcoming IPO Calendar", "param_func": self.upcoming_ipo_calendar_params, "api_func": self.upcoming_ipo_calendar},
            {"name": "Market Volume (U.S.)", "param_func": self.market_volume_us_params, "api_func": self.market_volume_us},
            {"name": "Sector Performance", "param_func": self.sector_performance_params, "api_func": self.sector_performance}
        ]

    ####################################################################################################################
    # Earnings Today
    ####################################################################################################################
    def earnings_today_params(self):
        return super().info_params(
            "Earnings reported today for 'before the open', 'after market close' and 'other'. "
            "Updated 9AM, 11AM, 12PM UTC daily.", "1001 per symbol."), {}

    '''
    {
      "bto": [
        {
            "consensusEPS": "-0.03",
            "announceTime": "BTO",
            "numberOfEstimates": 4,
            "fiscalPeriod": "Q4 2018",
            "fiscalEndDate": "2018-12-31",
            "symbol": "Z",
            "quote": {
              ...
            },
        },
        ...
      ],
      "amc": [
        {
            "consensusEPS": "-0.03",
            "announceTime": "AMC",
            "numberOfEstimates": 4,
            "fiscalPeriod": "Q4 2018",
            "fiscalEndDate": "2018-12-31",
            "symbol": "NBEV",
            "quote": {
              ...
            },
        },
        ...
      ],
      "other": []
    }
    '''
    def earnings_today(self, *args):
        res = self.market_info_base_request("today-earnings", None)
        if isinstance(res, dict):
            dict_list = res["bto"] + res["amc"] + res["other"]
            return super().clean_keys(dict_list, ["quote"])
        else:
            return res

    ####################################################################################################################
    # IPO Today
    ####################################################################################################################
    def today_ipo_calendar_params(self):
        return super().info_params("Today IPOs but also seems to include recent past IPOs."
                                   "Updated 10AM, 10:30AM UTC daily.", "500 per symbol."), {}

    '''
    {
        "rawData": [
            {
                "symbol": "VCNX",
                "companyName": "VACCINEX, INC.",
                "expectedDate": "2018-08-09",
                "leadUnderwriters": [
                    "BTIG, LLC",
                    "Oppenheimer & Co. Inc."
                ],
                "underwriters": [
                    "Ladenburg Thalmann & Co. Inc."
                ],
                "companyCounsel": [
                    "Hogan Lovells US LLP and Harter Secrest & Emery LLP"
                ],
                "underwriterCounsel": [
                    "Mintz, Levin, Cohn, Ferris, Glovsky and Popeo, P.C."
                ],
                "auditor": "Computershare Trust Company, N.A",
                "market": "NASDAQ Global",
                "cik": "0001205922",
                "address": "1895 MOUNT HOPE AVE",
                "city": "ROCHESTER",
                "state": "NY",
                "zip": "14620",
                "phone": "585-271-2700",
                "ceo": "Maurice Zauderer",
                "employees": 44,
                "url": "www.vaccinex.com",
                "status": "Filed",
                "sharesOffered": 3333000,
                "priceLow": 12,
                "priceHigh": 15,
                "offerAmount": null,
                "totalExpenses": 2400000,
                "sharesOverAlloted": 499950,
                "shareholderShares": null,
                "sharesOutstanding": 11474715,
                "lockupPeriodExpiration": "",
                "quietPeriodExpiration": "",
                "revenue": 206000,
                "netIncome": -7862000,
                "totalAssets": 4946000,
                "totalLiabilities": 6544000,
                "stockholderEquity": -133279000,
                "companyDescription": "",
                "businessDescription": "",
                "useOfProceeds": "",
                "competition": "",
                "amount": 44995500,
                "percentOffered": "29.05"
            },
            ...
        ],
        "viewData": [
            {
                "Company": "VACCINEX, INC.",
                "Symbol": "VCNX",
                "Price": "$12.00 - 15.00",
                "Shares": "3,333,000",
                "Amount": "44,995,500",
                "Float": "11,474,715",
                "Percent": "29.05%",
                "Market": "NASDAQ Global",
                "Expected": "2018-08-09"
            },
            ...
        ]
    }
    '''
    def today_ipo_calendar(self, *args):
        res = self.market_info_base_request("today-ipos", None)
        if isinstance(res, dict):
            return res["rawData"]
        else:
            return res

    ####################################################################################################################
    # IPO Upcoming
    ####################################################################################################################
    def upcoming_ipo_calendar_params(self):
        return super().info_params("Upcoming IPOs but also seems to include recent past IPOs."
                                   "Updated 10AM, 10:30AM UTC daily.", "100 per symbol."), {}

    '''
    same json response as today_ipo_calendar()
    '''
    def upcoming_ipo_calendar(self, *args):
        res = self.market_info_base_request("upcoming-ipos", None)
        if isinstance(res, dict):
            return res["rawData"]
        else:
            return res

    ####################################################################################################################
    # Market Volume U.S.
    ####################################################################################################################
    def market_volume_us_params(self):
        return super().info_params("Returns real time traded volume on US markets.", "1 per call."), {}

    '''
    [
      {
        "mic": "TRF",
        "tapeId": "-",
        "venueName": "TRF Volume",
        "volume": 589171705,
        "tapeA": 305187928,
        "tapeB": 119650027,
        "tapeC": 164333750,
        "marketPercent": 0.37027,
        "lastUpdated": 1480433817317
      },
      {
        "mic": "XNGS",
        "tapeId": "Q",
        "venueName": "NASDAQ",
        "volume": 213908393,
        "tapeA": 90791123,
        "tapeB": 30731818,
        "tapeC": 92385452,
        "marketPercent": 0.13443,
        "lastUpdated": 1480433817311
      },//...
    ]
    '''
    def market_volume_us(self, *args):
        return self.market_info_base_request("volume", None, ms_epoch_time_keys=["lastUpdated"])

    ####################################################################################################################
    # Sector Performance U.S.
    ####################################################################################################################
    def sector_performance_params(self):
        return super().info_params("15 minute delayed sector performance from the current trading day. "
                                   "Based on sector ETFs.", "11 per call (1 per 11 sectors) ."), {}

    '''
    [
      {
        "type": "sector",
        "name": "Industrials",
        "performance": 0.00711,
        "lastUpdated": 1533672000437
      },
      ...
    ]
    '''
    def sector_performance(self, *args):
        return self.market_info_base_request("sector-performance", None, clean_keys=["type"],
                                             ms_epoch_time_keys=["lastUpdated"])


########################################################################################################################
# class Treasuries inherits Base
########################################################################################################################
class Treasuries(Base):

    def endpoints(self):
        return [
            {"name": "Daily Treasury Rates", "param_func": self.daily_treasuries_params, "api_func": self.daily_treasuries}
        ]

    ####################################################################################################################
    # Daily Treasuries
    ####################################################################################################################
    def daily_treasuries_params(self):
        return super().info_params("History available since 1962. Updated 6AM, 11PM UTC. Date-1 is from. Date-2 is to.",
                                   "Warning: Expensive. 1000 per symbol per date."),\
               {"maturity": ["DGS30", "DGS20", "DGS10", "DGS5", "DGS2", "DGS1", "DGS6MO", "DGS3MO", "DGS1MO"],
                "date-1": ("1962-01-01", None), "date-2": ("1962-01-01", None)}

    '''
    [
      {
        "value": 1.77,
        "id": "TREASURY",
        "source": "IEX Cloud",
        "key": "COMPOUT",
        "subkey": "NONE",
        "date": 1574208000000,
        "updated": 1574359220000
      }
      // ...
    ]
    '''
    def daily_treasuries(self, *args):
        return super().time_series_endpoint("treasury/", args[0], symbol_key="maturity")


########################################################################################################################
# class Commodities inherits Base
########################################################################################################################
class Commodities(Base):

    def endpoints(self):
        return [
            {"name": "Oil Price", "param_func": self.oil_prices_params, "api_func": self.oil_prices},
            {"name": "Natural Gas Price", "param_func": self.natural_gas_prices_params, "api_func": self.natural_gas_prices},
            {"name": "Heating Oil Price", "param_func": self.heating_oil_prices_params, "api_func": self.heating_oil_prices},
            {"name": "Jet Fuel Price", "param_func": self.jet_fuel_prices_params, "api_func": self.jet_fuel_prices},
            {"name": "Diesel Price", "param_func": self.diesel_prices_params, "api_func": self.diesel_prices},
            {"name": "Gas Price", "param_func": self.gas_prices_params, "api_func": self.gas_prices},
            {"name": "Propane Price", "param_func": self.propane_prices_params, "api_func": self.propane_prices}
        ]

    ####################################################################################################################
    # Oil Prices
    ####################################################################################################################
    def oil_prices_params(self):
        return super().info_params("Daily history available since 1986. Updated weekly at 6AM UTC Friday. WTI and Brent."
                                   "Date-1 is from. Date-2 is to.", "Warning: Expensive. 1000 per symbol per date."), \
               {"symbol": ["DCOILWTICO", "DCOILBRENTEU"], "date-1": ("1986-01-01", None), "date-2": ("1986-01-01", None)}

    '''
    [
      {
        "value": 1.77,
        "id": "ENERGY",
        "source": "IEX Cloud",
        "key": "DCOILWTICO",
        "subkey": "NONE",
        "date": 1574208000000,
        "updated": 1574359220000
      }
      // ...
    ]
    '''

    def oil_prices(self, *args):
        return super().time_series_endpoint("energy/", args[0])

    ####################################################################################################################
    # Natural Gas Prices
    ####################################################################################################################
    def natural_gas_prices_params(self):
        return super().info_params("Daily history available since 1997. Updated daily at 6AM UTC. "
                                   "Henry Hub Natural Gas Spot Price"
                                   "Date-1 is from. Date-2 is to.", "Warning: Expensive. 1000 per symbol per date."), \
               {"symbol": ["DHHNGSP"], "date-1": ("1997-01-01", None), "date-2": ("1997-01-01", None)}

    '''
    [
      {
        "value": 1.77,
        "id": "ENERGY",
        "source": "IEX Cloud",
        "key": "DCOILWTICO",
        "subkey": "NONE",
        "date": 1574208000000,
        "updated": 1574359220000
      }
      // ...
    ]
    '''

    def natural_gas_prices(self, *args):
        return super().time_series_endpoint("energy/", args[0])

    ####################################################################################################################
    # Heating Oil Prices
    ####################################################################################################################
    def heating_oil_prices_params(self):
        return super().info_params("Daily history available since 1986. Updated daily at 6AM UTC. "
                                   "No. 2 Heating Oil New York Harbor."
                                   "Date-1 is from. Date-2 is to.", "Warning: Expensive. 1000 per symbol per date."), \
               {"symbol": ["DHOILNYH"], "date-1": ("1986-01-01", None), "date-2": ("1986-01-01", None)}

    '''
    [
      {
        "value": 1.77,
        "id": "ENERGY",
        "source": "IEX Cloud",
        "key": "DCOILWTICO",
        "subkey": "NONE",
        "date": 1574208000000,
        "updated": 1574359220000
      }
      // ...
    ]
    '''

    def heating_oil_prices(self, *args):
        return super().time_series_endpoint("energy/", args[0])

    ####################################################################################################################
    # Jet Fuel Prices
    ####################################################################################################################
    def jet_fuel_prices_params(self):
        return super().info_params("Daily history available since 1990. Updated daily at 6AM UTC. "
                                   "Kerosense Type Jet Fuel US Gulf Coast."
                                   "Date-1 is from. Date-2 is to.", "Warning: Expensive. 1000 per symbol per date."), \
               {"symbol": ["DJFUELUSGULF"], "date-1": ("1990-01-01", None), "date-2": ("1990-01-01", None)}

    '''
    [
      {
        "value": 1.77,
        "id": "ENERGY",
        "source": "IEX Cloud",
        "key": "DCOILWTICO",
        "subkey": "NONE",
        "date": 1574208000000,
        "updated": 1574359220000
      }
      // ...
    ]
    '''

    def jet_fuel_prices(self, *args):
        return super().time_series_endpoint("energy/", args[0])

    ####################################################################################################################
    # Diesel Prices
    ####################################################################################################################
    def diesel_prices_params(self):
        return super().info_params("Daily history available since 1994. Updated weekly at 6AM UTC. "
                                   "US Diesel Sales Price."
                                   "Date-1 is from. Date-2 is to.", "Warning: Expensive. 1000 per symbol per date."), \
               {"symbol": ["GASDESW"], "date-1": ("1994-01-01", None), "date-2": ("1994-01-01", None)}

    '''
    [
      {
        "value": 1.77,
        "id": "ENERGY",
        "source": "IEX Cloud",
        "key": "DCOILWTICO",
        "subkey": "NONE",
        "date": 1574208000000,
        "updated": 1574359220000
      }
      // ...
    ]
    '''

    def diesel_prices(self, *args):
        return super().time_series_endpoint("energy/", args[0])

    ####################################################################################################################
    # Gas Prices
    ####################################################################################################################
    def gas_prices_params(self):
        return super().info_params("Daily history available since 1990. Updated weekly at 6AM UTC. "
                                   "Regular, Midgrade, Premium. In dollars per gallon."
                                   "Date-1 is from. Date-2 is to.", "Warning: Expensive. 1000 per symbol per date."), \
               {"symbol": ["GASREGCOVW", "GASMIDCOVW", "GASPRMCOVW"], "date-1": ("1990-01-01", None), "date-2": ("1990-01-01", None)}

    '''
    [
      {
        "value": 1.77,
        "id": "ENERGY",
        "source": "IEX Cloud",
        "key": "DCOILWTICO",
        "subkey": "NONE",
        "date": 1574208000000,
        "updated": 1574359220000
      }
      // ...
    ]
    '''

    def gas_prices(self, *args):
        return super().time_series_endpoint("energy/", args[0])

    ####################################################################################################################
    # Propane Prices
    ####################################################################################################################
    def propane_prices_params(self):
        return super().info_params("Daily history available since 1992. Updated daily at 6AM UTC. "
                                   "Propane Prices Mont Belvieu Texas. In dollars per gallon."
                                   "Date-1 is from. Date-2 is to.", "Warning: Expensive. 1000 per symbol per date."), \
               {"symbol": ["DPROPANEMBTX"], "date-1": ("1992-01-01", None), "date-2": ("1992-01-01", None)}

    '''
    [
      {
        "value": 1.77,
        "id": "ENERGY",
        "source": "IEX Cloud",
        "key": "DCOILWTICO",
        "subkey": "NONE",
        "date": 1574208000000,
        "updated": 1574359220000
      }
      // ...
    ]
    '''

    def propane_prices(self, *args):
        return super().time_series_endpoint("energy/", args[0])


########################################################################################################################
# class EconomicData inherits Base
########################################################################################################################
class EconomicData(Base):

    def endpoints(self):
        return [
            {"name": "CD Rates", "param_func": self.cd_rates_params, "api_func": self.cd_rates},
            {"name": "Consumer Price Index", "param_func": self.consumer_price_index_params, "api_func": self.consumer_price_index},
            {"name": "Credit Card Interest Rate", "param_func": self.credit_card_interest_rate_params, "api_func": self.credit_card_interest_rate},
            {"name": "Federal Fund Rate", "param_func": self.federal_funds_rate_params, "api_func": self.federal_funds_rate},
            {"name": "Real GDP", "param_func": self.real_gdp_growth_params, "api_func": self.real_gdp_growth},
            {"name": "Institutional Money Funds", "param_func": self.institutional_money_funds_params, "api_func": self.institutional_money_funds},
            {"name": "Initial Claims", "param_func": self.initial_claims_params, "api_func": self.initial_claims},
            {"name": "Industrial Production Index", "param_func": self.industrial_production_index_params, "api_func": self.industrial_production_index},
            {"name": "Mortgage Rates", "param_func": self.mortgage_rates_params, "api_func": self.mortgage_rates},
            {"name": "Total Housing Starts", "param_func": self.total_housing_starts_params, "api_func": self.total_housing_starts},
            {"name": "Total Payrolls", "param_func": self.total_payrolls_params, "api_func": self.total_payrolls},
            {"name": "Total Vehicle Sales", "param_func": self.total_vehicle_sales_params, "api_func": self.total_vehicle_sales},
            {"name": "Retail Money Funds", "param_func": self.retail_money_funds_params, "api_func": self.retail_money_funds},
            {"name": "Unemployment Rate", "param_func": self.unemployment_rate_params, "api_func": self.unemployment_rate}
        ]

    ####################################################################################################################
    # CD Rates
    ####################################################################################################################
    def cd_rates_params(self):
        return super().info_params(
            "Current non-jumbo (NJ) less than $100000 money market and jumbo greater than $100000 money market. "
            "Updated weekly at 6AM UTC Friday", "1000 per symbol per date."), {"symbol": ["MMNRNJ", "MMNRJD"]}

    '''
    2.5
    '''
    def cd_rates(self, *args):
        return super().data_points_endpoint("market/", args[0])

    ####################################################################################################################
    # Consumer Price Index
    ####################################################################################################################
    def consumer_price_index_params(self):
        return super().info_params(
            "Current consumer price index for all urban consumers. Updated monthly at 6AM UTC.",
            "1000 per symbol per date."), {"symbol": ["CPIAUCSL"]}

    '''
    2.5
    '''
    def consumer_price_index(self, *args):
        return super().data_points_endpoint("market/", args[0])

    ####################################################################################################################
    # Credit Card Interest Rate
    ####################################################################################################################
    def credit_card_interest_rate_params(self):
        return super().info_params(
            "Current commercial bank credit card interest rate in percent. Updated monthly at 6AM UTC.",
            "1000 per symbol per date."), {"symbol": ["TERMCBCCALLNS"]}

    '''
    15.1
    '''
    def credit_card_interest_rate(self, *args):
        return super().data_points_endpoint("market/", args[0])

    ####################################################################################################################
    # Federal Funds Rate
    ####################################################################################################################
    def federal_funds_rate_params(self):
        return super().info_params(
            "Current effective federal funds rate. Updated monthly at 6AM UTC.", "1000 per symbol per date."), \
               {"symbol": ["FEDFUNDS"]}

    '''
    2.5
    '''
    def federal_funds_rate(self, *args):
        return super().data_points_endpoint("market/", args[0])

    ####################################################################################################################
    # Real GDP
    ####################################################################################################################
    def real_gdp_growth_params(self):
        return super().info_params("Quarterly history available since 1947. Updated quarterly at 6AM UTC. "
                                   "Date-1 is from. Date-2 is to.", "Warning: Expensive. 1000 per symbol per date."), \
               {"symbol": ["A191RL1Q225SBEA"], "date-1": ("1947-01-01", None), "date-2": ("1947-01-01", None)}

    '''
    [
      {
        "value": 1.77,
        "id": "ECONOMIC",
        "source": "IEX Cloud",
        "key": "DGS10",
        "subkey": "NONE",
        "date": 1574208000000,
        "updated": 1574359220000
      }
      // ...
    ]
    '''
    def real_gdp_growth(self, *args):
        return super().time_series_endpoint("economic/", args[0])

    ####################################################################################################################
    # Institutional Money Funds
    ####################################################################################################################
    def institutional_money_funds_params(self):
        return super().info_params(
            "Current weekly institutional money funds in billions of dollars. Updated weekly at 6AM UTC.",
            "1000 per symbol per date."), {"symbol": ["WIMFSL"]}

    '''
    2,195
    '''
    def institutional_money_funds(self, *args):
        return super().data_points_endpoint("market/", args[0])

    ####################################################################################################################
    # Initial Claims
    ####################################################################################################################
    def initial_claims_params(self):
        return super().info_params(
            "Current 4 week moving average of initial claims. Updated weekly at 6AM UTC",
            "1000 per symbol per date."), {"symbol": ["IC4WSA"]}

    '''
    210,000
    '''
    def initial_claims(self, *args):
        return super().data_points_endpoint("market/", args[0])

    ####################################################################################################################
    # Industrial Production Index
    ####################################################################################################################
    def industrial_production_index_params(self):
        return super().info_params(
            "Current industrial production index. Updated monthly at 6AM UTC",
            "1000 per symbol per date."), {"symbol": ["INDPRO"]}

    '''
    2.5
    '''
    def industrial_production_index(self, *args):
        return super().data_points_endpoint("market/", args[0])

    ####################################################################################################################
    # Mortgage Rates
    ####################################################################################################################
    def mortgage_rates_params(self):
        return super().info_params("US Daily history available since 1971. Updated weekly at 6AM UTC Friday."
                                   "30 year fixed, 15 year fixed and 5/1-Year adjustable averages."
                                   "Date-1 is from. Date-2 is to.", "Warning: Expensive. 1000 per symbol per date."), \
               {"symbol": ["MORTGAGE30US", "MORTGAGE15US", "MORTGAGE5US"], "date-1": ("1971-01-01", None),
                "date-2": ("1971-01-01", None)}

    '''
    [
      {
        "value": 1.77,
        "id": "ECONOMIC",
        "source": "IEX Cloud",
        "key": "DGS10",
        "subkey": "NONE",
        "date": 1574208000000,
        "updated": 1574359220000
      }
      // ...
    ]
    '''
    def mortgage_rates(self, *args):
        return super().time_series_endpoint("economic/", args[0])

    ####################################################################################################################
    # Total Housing Starts
    ####################################################################################################################
    def total_housing_starts_params(self):
        return super().info_params("US daily privately owned housing starts since 1959 in thousands of units, "
                                   "seasonally adjusted annual rate. Updated monthly at 6AM UTC. "
                                   "Date-1 is from. Date-2 is to.", "Warning: Expensive. 1000 per symbol per date."), \
               {"symbol": ["HOUST"], "date-1": ("1959-01-01", None), "date-2": ("1959-01-01", None)}

    '''
    [
      {
        "value": 1.77,
        "id": "ECONOMIC",
        "source": "IEX Cloud",
        "key": "DGS10",
        "subkey": "NONE",
        "date": 1574208000000,
        "updated": 1574359220000
      }
      // ...
    ]
    '''
    def total_housing_starts(self, *args):
        return super().time_series_endpoint("economic/", args[0])

    ####################################################################################################################
    # Total Payrolls
    ####################################################################################################################
    def total_payrolls_params(self):
        return super().info_params("Total non-farm payrolls in thousands of persons seasonally adjusted. Updated "
                                   "monthly at 6AM UTC", "1000 per symbol per date."), {"symbol": ["PAYEMS"]}

    '''
    160000
    '''
    def total_payrolls(self, *args):
        return super().data_points_endpoint("market/", args[0])

    ####################################################################################################################
    # Total Vehicle Sales
    ####################################################################################################################
    def total_vehicle_sales_params(self):
        return super().info_params("Total vehicle sales in millions of units. Updated monthly at 6AM UTC",
                                   "1000 per symbol per date."), {"symbol": ["TOTALSA"]}

    '''
    15.5
    '''
    def total_vehicle_sales(self, *args):
        return super().data_points_endpoint("market/", args[0])

    ####################################################################################################################
    # Retail Money Funds
    ####################################################################################################################
    def retail_money_funds_params(self):
        return super().info_params("Weekly retail money funds in billions of dollars, seasonally adjusted. Updated "
                                   "weekly at 6AM UTC", "1000 per symbol per date."), {"symbol": ["WRMFSL"]}

    '''
    999
    '''
    def retail_money_funds(self, *args):
        return super().data_points_endpoint("market/", args[0])

    ####################################################################################################################
    # Unemployment Rate
    ####################################################################################################################
    def unemployment_rate_params(self):
        return super().info_params("US civilian unemployment rate as a percent, seasonally adjusted, since 1948."
                                   " Updated monthly at 6AM UTC. Date-1 is from. Date-2 is to.",
                                   "Warning: Expensive. 1000 per symbol per date."), \
               {"symbol": ["UNRATE"], "date-1": ("1948-01-01", None), "date-2": ("1948-01-01", None)}

    '''
    [
      {
        "value": 1.77,
        "id": "ECONOMIC",
        "source": "IEX Cloud",
        "key": "DGS10",
        "subkey": "NONE",
        "date": 1574208000000,
        "updated": 1574359220000
      }
      // ...
    ]
    '''
    def unemployment_rate(self, *args):
        return super().time_series_endpoint("economic/", args[0])


########################################################################################################################
# class ReferenceData inherits Base
########################################################################################################################
class ReferenceData(Base):

    def reference_data_base_request(self, endpoint, param_str, clean_keys=(), ms_epoch_time_keys=()):
        return super().do_request("/ref-data/" + endpoint, param_str, False, True, clean_keys=clean_keys,
                                  ms_epoch_time_keys=ms_epoch_time_keys)

    def endpoints(self):
        return [
            {"name": "Cryptocurrency Symbols", "param_func": self.cryptocurrency_symbols_params, "api_func": self.cryptocurrency_symbols},
            {"name": "FX Symbols", "param_func": self.fx_symbols_params, "api_func": self.fx_symbols}
        ]

    ####################################################################################################################
    # Cryptocurrency Symbols
    ####################################################################################################################
    def cryptocurrency_symbols_params(self):
        return super().info_params("All available cryptocurrency symbols. Updated daily at 8AM UTC.", "1 per call"), {}

    '''
    [
      {
        "symbol": "BTCUSD",
        "name": "Bitcoin to USD",
        "exchange": null,
        "date": "2019-08-19",
        "type": "crypto",
        "iexId": null,
        "region": "US",
        "currency": "USD",
        "isEnabled": true
      },
      {
        "symbol": "ETHUSD",
        "name": "Ethereum to USD",
        "exchange": null,
        "date": "2019-08-19",
        "iexId": null,
        "type": "crypto",
        "region": "US",
        "currency": "USD",
        "isEnabled": true
      },
      ...
    ]
    '''
    def cryptocurrency_symbols(self, *args):
        return self.reference_data_base_request("crypto/symbols", None)

    ####################################################################################################################
    # FX Symbols
    ####################################################################################################################
    def fx_symbols_params(self):
        return super().info_params("All available FX currencies and pairs. Updated daily at 7AM, 9AM UTC.",
                                   "1 per call"), {"Category": ["currencies", "pairs"]}

    '''
    {
      "currencies": [
        {
          "code": "USD",
          "name": "U.S. Dollar"
        },
      //...
      ],
      "pairs": [
        { 
          "fromCurrency": "EUR",
          "toCurrency": "USD",
          "symbol": "EURUSD"
        }, 
      //...
      ]
    }
    '''
    def fx_symbols(self, *args):
        res = self.reference_data_base_request("fx/symbols", None)
        if isinstance(res, str):
            return res
        else:
            category = args[0]["Category"]
            return res[category]