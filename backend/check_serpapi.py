"""Check account safely; optional single live one-way search, no key on CLI."""
import argparse,json,os
from providers.serpapi_flights import SerpApiFlights,ProviderError


def main():
 parser=argparse.ArgumentParser(description='SerpApi: comprobar cuenta o una consulta acotada de vuelos.')
 parser.add_argument('--origin',nargs='+',default=['SCQ','LCG','VGO','OPO','MAD'])
 parser.add_argument('--destination');parser.add_argument('--date')
 parser.add_argument('--adults',type=int,default=1);parser.add_argument('--children',type=int,default=0)
 args=parser.parse_args()
 try:
  api=SerpApiFlights(os.environ.get('SERPAPI_API_KEY'),request_limit=1)
  if args.destination or args.date:
   if not args.destination or not args.date:parser.error('Indica destino y fecha juntos.')
   data=api.one_way(args.origin,args.destination,args.date,args.adults,args.children)
  else:data=api.account_summary()
  print(json.dumps(data,ensure_ascii=False,indent=2))
 except (ProviderError,ValueError) as exc:parser.exit(1,str(exc)+'\n')


if __name__=='__main__':main()
