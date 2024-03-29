import numpy as np
from scipy.optimize import minimize

sp100_stocks = ['AAPL','MSFT','AMZN','FB','BRKB','GOOGL','GOOG','JPM','JNJ','V','PG','XOM','UNH','BAC','MA','T','DIS','INTC','HD','VZ','MRK','PFE','CVX','KO','CMCSA','CSCO','PEP','WFC','C','BA','ADBE','WMT','CRM','MCD','MDT','BMY','ABT','NVDA','NFLX','AMGN','PM','PYPL','TMO','COST','ABBV','ACN','HON','NKE','UNP','UTX','NEE','IBM','TXN','AVGO','LLY','ORCL','LIN','SBUX','AMT','LMT','GE','MMM','DHR','QCOM','CVS','MO','LOW','FIS','AXP','BKNG','UPS','GILD','CHTR','CAT','MDLZ','GS','USB','CI','ANTM','BDX','TJX','ADP','TFC','CME','SPGI','COP','INTU','ISRG','CB','SO','D','FISV','PNC','DUK','SYK','ZTS','MS','RTN','AGN','BLK']

def MonthDiff(d1, d2):
    return (d1.year - d2.year) * 12 + d1.month - d2.month

def Return(values):
    return (values[-1] - values[0]) / values[0]
    
def Volatility(values):
    values = np.array(values)
    returns = (values[1:] - values[:-1]) / values[:-1]
    return np.std(returns)  

# Custom fee model
class CustomFeeModel(FeeModel):
    def GetOrderFee(self, parameters):
        fee = parameters.Security.Price * parameters.Order.AbsoluteQuantity * 0.00005
        return OrderFee(CashAmount(fee, "USD"))

# Quandl free data
class QuandlFutures(PythonQuandl):
    def __init__(self):
        self.ValueColumnName = "settle"

# Quandl short interest data.
class QuandlFINRA_ShortVolume(PythonQuandl):
    def __init__(self):
        self.ValueColumnName = 'SHORTVOLUME'    # also 'TOTALVOLUME' is accesible

# Quantpedia futures data - back adjusted.
# NOTE: IMPORTANT: Data order must be ascending (datewise)
class QuantpediaFutures(PythonData):
    def GetSource(self, config, date, isLiveMode):
        return SubscriptionDataSource("data.quantpedia.com/backtesting_data/futures/back_adjusted/{0}.csv".format(config.Symbol.Value), SubscriptionTransportMedium.RemoteFile, FileFormat.Csv)

    def Reader(self, config, line, date, isLiveMode):
        data = QuantpediaFutures()
        data.Symbol = config.Symbol
        
        if not line[0].isdigit(): return None
        split = line.split(';')
        
        data.Time = datetime.strptime(split[0], "%Y%m%d") + timedelta(days=1)
        data['settle'] = float(split[1])
        data.Value = float(split[1])

        return data
		
# Quantpedia data
# NOTE: IMPORTANT: Data order must be ascending (datewise)
# class QuantpediaFutures(PythonData):
#     def GetSource(self, config, date, isLiveMode):
#         return SubscriptionDataSource("data.quantpedia.com/backtesting_data/futures/{0}.csv".format(config.Symbol.Value), SubscriptionTransportMedium.RemoteFile, FileFormat.Csv)

#     def Reader(self, config, line, date, isLiveMode):
#         data = QuantpediaFutures()
#         data.Symbol = config.Symbol
        
#         if not line[0].isdigit(): return None
#         split = line.split(';')
        
#         data.Time = datetime.strptime(split[0], "%d.%m.%Y") + timedelta(days=1)
#         data['settle'] = float(split[1])
#         data.Value = float(split[1])

#         return data
        
# NOTE: Manager for new trades. It's represented by certain count of equally weighted brackets for long and short positions.
# If there's a place for new trade, it will be managed for time of holding period.
class TradeManager():
    def __init__(self, algorithm, long_size, short_size, holding_period):
        self.algorithm = algorithm  # algorithm to execute orders in.
        
        self.long_size = long_size
        self.short_size = short_size
        self.weight = 1 / (self.long_size + self.short_size)
        
        self.long_len = 0
        self.short_len = 0
    
        # Arrays of ManagedSymbols
        self.symbols = []
        
        self.holding_period = holding_period    # Days of holding.
    
    # Add stock symbol object
    def Add(self, symbol, long_flag):
        # Open new long trade.
        managed_symbol = ManagedSymbol(symbol, self.holding_period, long_flag)
        
        if long_flag:
            # If there's a place for it.
            if self.long_len < self.long_size:
                self.symbols.append(managed_symbol)
                self.algorithm.SetHoldings(symbol, self.weight)
                self.long_len += 1
            else:
                self.algorithm.Log("There's not place for additional trade.")

        # Open new short trade.
        else:
            # If there's a place for it.
            if self.short_len < self.short_size:
                self.symbols.append(managed_symbol)
                self.algorithm.SetHoldings(symbol, - self.weight)
                self.short_len += 1
            else:
                self.algorithm.Log("There's not place for additional trade.")
    
    # Decrement holding period and liquidate symbols.
    def TryLiquidate(self):
        symbols_to_delete = []
        for managed_symbol in self.symbols:
            managed_symbol.days_to_liquidate -= 1
            
            # Liquidate.
            if managed_symbol.days_to_liquidate == 0:
                symbols_to_delete.append(managed_symbol)
                self.algorithm.Liquidate(managed_symbol.symbol)
                
                if managed_symbol.long_flag: self.long_len -= 1
                else: self.short_len -= 1

        # Remove symbols from management.
        for managed_symbol in symbols_to_delete:
            self.symbols.remove(managed_symbol)
    
    def LiquidateTicker(self, ticker):
        symbol_to_delete = None
        for managed_symbol in self.symbols:
            if managed_symbol.symbol.Value == ticker:
                self.algorithm.Liquidate(managed_symbol.symbol)
                symbol_to_delete = managed_symbol
                if managed_symbol.long_flag: self.long_len -= 1
                else: self.short_len -= 1
                
                break
        
        if symbol_to_delete: self.symbols.remove(symbol_to_delete)
        else: self.algorithm.Debug("Ticker is not held in portfolio!")
    
class ManagedSymbol():
    def __init__(self, symbol, days_to_liquidate, long_flag):
        self.symbol = symbol
        self.days_to_liquidate = days_to_liquidate
        self.long_flag = long_flag
        
class PortfolioOptimization(object):
    def __init__(self, df_return, risk_free_rate, num_assets):
        self.daily_return = df_return
        self.risk_free_rate = risk_free_rate
        self.n = num_assets # numbers of risk assets in portfolio
        self.target_vol = 0.05

    def annual_port_return(self, weights):
        # calculate the annual return of portfolio
        return np.sum(self.daily_return.mean() * weights) * 252

    def annual_port_vol(self, weights):
        # calculate the annual volatility of portfolio
        return np.sqrt(np.dot(weights.T, np.dot(self.daily_return.cov() * 252, weights)))

    def min_func(self, weights):
        # method 1: maximize sharp ratio
        return - self.annual_port_return(weights) / self.annual_port_vol(weights)
        
        # method 2: maximize the return with target volatility
        #return - self.annual_port_return(weights) / self.target_vol

    def opt_portfolio(self):
        # maximize the sharpe ratio to find the optimal weights
        cons = ({'type': 'eq', 'fun': lambda x: np.sum(x) - 1})
        bnds = tuple((0, 1) for x in range(2)) + tuple((0, 0.25) for x in range(self.n - 2))
        opt = minimize(self.min_func,                               # object function
                       np.array(self.n * [1. / self.n]),            # initial value
                       method='SLSQP',                              # optimization method
                       bounds=bnds,                                 # bounds for variables 
                       constraints=cons)                            # constraint conditions
                      
        opt_weights = opt['x']
 
        return opt_weights
