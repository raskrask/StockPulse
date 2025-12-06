import infrastructure.util.io_utils as io_utils

def load_backend_trigger(symbol) -> list:
    filename = f"{symbol}/backtest/triggers.json"
    if io_utils.exists_file(filename):
        return io_utils.load_json(filename)
    return None

def save_backend_trigger(symbol, trigger):
    filename = f"{symbol}/backtest/triggers.json"
    io_utils.save_json(filename, trigger)