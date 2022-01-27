import json
import requests
import statistics


def main():
    for url in url_to_json('https://muo-backend.cs.man.ac.uk/deployments/levenshulme-bee-network')['deployedOnPlatform']:
        platform = url_to_json(url)
        if platform.get('description') == 'Traffic camera':
            for host in platform['hosts']:
                sensor = url_to_json(host)
                location = sensor['centroid']['geometry']['coordinates']
                for timeseries in sensor['timeseries']:
                    # We don't want speed
                    if 'count' in timeseries:
                        ref = timeseries.split('/')[-1]
                        print(f'Sensor at {location}')
                        scrape(ref)


def url_to_json(url):
    return json.loads(requests.get(url).content)


def scrape(ref):
    print(f'Scraping {ref}')
    start_time = '2021-04-22T00:00:00.000Z'
    end_time = '2022-01-27T15:38:51.077Z'
    resolution = '1d'
    url = f'https://muo-backend.cs.man.ac.uk/rawdata?ref={ref}&start_time={start_time}&end_time={end_time}&resolution={resolution}&interpolate=false&quantity=vehicle-count&cumulative=true'

    data = url_to_json(url)
    # We don't care about the dates yet (until we know when the LTN was installed...)
    # TODO But also ignore outliers like Christmas
    counts = [entry['value'] for entry in data]
    print(statistics.mean(counts))


if __name__ == "__main__":
    main()
