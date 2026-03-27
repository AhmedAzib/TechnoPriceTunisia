import asyncio
import ccxt.pro as ccxt  # Requires ccxt.pro license
import sys
from datetime import datetime

class CryptoDashboard:
    def __init__(self, exchange_id='binance', symbol='BTC/USDT'):
        self.exchange_id = exchange_id
        self.symbol = symbol
        self.running = False
        
        # Initialize exchange
        try:
            self.exchange = getattr(ccxt, exchange_id)()
        except AttributeError:
            print(f"Error: Exchange '{exchange_id}' not found in ccxt.")
            sys.exit(1)

    async def fetch_ticker(self):
        """Fetches ticker data via WebSocket."""
        print(f"Starting dashboard for {self.symbol} on {self.exchange_id}...")
        print("Press Ctrl+C to stop.\n")
        
        while self.running:
            try:
                # watch_ticker returns a dictionary with ticker data
                ticker = await self.exchange.watch_ticker(self.symbol)
                self.display_data(ticker)
                
            except ccxt.NetworkError as e:
                print(f"\n[Network Error] {e}")
                await asyncio.sleep(5)  # Wait before retrying
            except ccxt.ExchangeError as e:
                print(f"\n[Exchange Error] {e}")
                await asyncio.sleep(5)
            except Exception as e:
                print(f"\n[Unexpected Error] {type(e).__name__}: {str(e)}")
                # Depending on severity, we might want to break or continue
                await asyncio.sleep(5)
                
    def display_data(self, ticker):
        """Formats and displays the ticker data."""
        # Simple dashboard display: Clear line and overwrite or just print log style
        # For a "Dashboard" feel in console, we usually clear screen, but that can be flickering.
        # Let's do a clean log output with fixed width for professional look or just print lines.
        # User asked for "dashboard", so let's try to keep it clean.
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        last_price = ticker.get('last')
        
        # Basic formatting
        output = f"[{timestamp}] {self.symbol} | Price: {last_price}"
        
        # If we have 24h change info
        if 'percentage' in ticker and ticker['percentage'] is not None:
            change = ticker['percentage']
            output += f" | 24h Change: {change:.2f}%"
            
        print(output)

    async def close(self):
        await self.exchange.close()

    async def run(self):
        try:
            await self.fetch_ticker()
        except KeyboardInterrupt:
            print("\nStopping dashboard...")
        finally:
            await self.close()

async def main():
    dashboard = CryptoDashboard(symbol='BTC/USDT')
    await dashboard.run()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nExited by user.")
