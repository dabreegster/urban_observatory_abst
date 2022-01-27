import json
import requests
import statistics


def main():
    ref = 'ca-traffic__37000007__vehicle-count_E'
    start_time = '2021-04-22T00:00:00.000Z'
    end_time = '2022-01-27T15:38:51.077Z'
    resolution = '1d'
    scrape(
        f'https://muo-backend.cs.man.ac.uk/rawdata?ref={ref}&start_time={start_time}&end_time={end_time}&resolution={resolution}&interpolate=false&quantity=vehicle-count&cumulative=true')


def scrape(url):
    data = json.loads(requests.get(url).content)
    # We don't care about the dates yet (until we know when the LTN was installed...)
    # TODO But also ignore outliers like Christmas
    counts = [entry['value'] for entry in data]
    print(statistics.mean(counts))


if __name__ == "__main__":
    main()
