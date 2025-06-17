#  OpenAQ CPCB Downloader (CLI)

A command-line tool to download air quality data from the OpenAQ API for selected Indian cities using CPCB sensors. This tool helps researchers, developers, and enthusiasts to gather hourly or daily air quality data efficiently.

---

##  Features

- Download **hourly** or **daily** air quality data from the OpenAQ API.
- Specify a **date range** using `--from-date` and `--to-date`.
- Automatically detects available CPCB sensors and location IDs within the city.
- Supports major Indian cities: **Chennai**, **Delhi**, **Gurugram**, etc.
- Saves the collected data into a clean `.csv` file.
- Handles errors gracefully when no data is available.

---

##  Requirements

Install the dependencies using:

```bash
pip install -r requirements.txt
```
## CLI Usage 
```bash
python main.py --city <city-name> --type <hourly/daily> --output <filename.csv> --from-date <YYYY-MM-DD> --to-date <YYYY-MM-DD>
```
## Author
N.S. Jayasurya

## License
This project is licensed under the BSD License - see the [LICENSE.md](LICENSE.md) file for details
