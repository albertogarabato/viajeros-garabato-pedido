"""Run an explicitly labelled, bounded TEST query. Never prints tokens or credentials."""
import argparse
import json
from optimizer import Party
from providers.amadeus_test import AmadeusTest, ProviderError, DEFAULT_ORIGINS


def main():
    parser = argparse.ArgumentParser(description='Comprobar Amadeus TEST, sin precios reales ni reservas.')
    parser.add_argument('--destination', required=True, help='Aeropuerto IATA, no ciudad libre.')
    parser.add_argument('--date', required=True, help='Salida AAAA-MM-DD.')
    parser.add_argument('--adults', type=int, required=True)
    parser.add_argument('--child-ages', type=int, nargs='*', default=[])
    args = parser.parse_args()
    try:
        party = Party(args.adults, tuple(args.child_ages))
        api = AmadeusTest.from_environment(request_limit=6)
        results = []
        for origin in DEFAULT_ORIGINS:
            results.append(api.search_direct(origin, args.destination, args.date, party))
        print(json.dumps({'mode': 'TEST_ONLY', 'results': results,
                          'requestsUsed': api.requests_used}, ensure_ascii=False, indent=2))
    except (ProviderError, ValueError) as exc:
        parser.exit(1, str(exc) + '\n')


if __name__ == '__main__':
    main()
