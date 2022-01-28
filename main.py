import collections
import json
import requests
import statistics
import subprocess
import time


def main():
    process = start_abstreet_with_map(
        'data/system/gb/manchester/maps/levenshulme.bin')
    print('Scraping sensor data')

    per_road = collections.defaultdict(int)
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
                        count = scrape_mean_vehicle_count(ref)
                        # Map this location to a RoadID
                        road_id = int(requests.get(
                            f'http://localhost:1234/map/get-nearest-road?lon={location[0]}&lat={location[1]}&threshold_meters=100').text)
                        print(
                            f'{ref} at {location} (road {road_id}) has count {count}')
                        # TODO We usually have both directons per road. Until
                        # the A/B Street traffic count format handles
                        # DirectedRoadID, just sum
                        per_road[road_id] += count

    process.terminate()

    output = {
        'map': {
            'city': {
                'country': 'gb',
                'city': 'manchester'
            },
            'map': 'levenshulme'
        },
        'description': 'from Manchester-I data',
        'per_road': list(per_road.items())
    }
    print(json.dumps(output))


def start_abstreet_with_map(map_path):
    # Start the A/B Street headless API and load the correct map. This requires
    # things to already be built, with maps downloaded, and all in a certain
    # path
    print('Starting A/B Street API')
    abst_path = '/home/dabreegster/abstreet'
    process = subprocess.Popen([abst_path + '/target/release/headless',
                               '--port', '1234'], cwd=abst_path, stderr=subprocess.PIPE)
    for line in iter(process.stderr.readline, ''):
        if line:
            line = str(line)
            print(line)
            if 'Listening on' in line:
                print(f'Loading {map_path}')
                requests.get(
                    'http://localhost:1234/sim/load-blank?map=' + map_path)
                return process


def url_to_json(url):
    return json.loads(requests.get(url).content)


def scrape_mean_vehicle_count(ref):
    start_time = '2021-04-22T00:00:00.000Z'
    end_time = '2022-01-27T15:38:51.077Z'
    resolution = '1d'
    url = f'https://muo-backend.cs.man.ac.uk/rawdata?ref={ref}&start_time={start_time}&end_time={end_time}&resolution={resolution}&interpolate=false&quantity=vehicle-count&cumulative=true'

    data = url_to_json(url)
    # We don't care about the dates yet (until we know when the LTN was installed...)
    # TODO But also ignore outliers like Christmas
    counts = [entry['value'] for entry in data]
    return int(statistics.mean(counts))


if __name__ == "__main__":
    main()
