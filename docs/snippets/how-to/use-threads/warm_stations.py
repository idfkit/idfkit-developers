from __future__ import annotations

from idfkit.weather import WeatherStation

stations: list[WeatherStation] = ...  # type: ignore[assignment]
# --8<-- [start:example]
from concurrent.futures import ThreadPoolExecutor

from idfkit.weather import WeatherDownloader

downloader = WeatherDownloader()

# Download each station once, before the parallel part starts: safe to skip, but it saves bandwidth.
files = {station.wmo: downloader.download(station) for station in stations}

with ThreadPoolExecutor() as pool:
    epw_paths = list(pool.map(lambda station: files[station.wmo].epw, stations))
# --8<-- [end:example]
