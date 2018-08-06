import random

import aiohttp
import discord
from discord.ext import commands

def find(key, dictionary):
    for k, v in dictionary.items():
        if k == key:
            yield v
        elif isinstance(v, dict):
            for result in find(key, v):
                yield result
        elif isinstance(v, list):
            for d in v:
                for result in find(key, d):
                    yield result

class GirlsFrontier:

    def __init__(self, bot):
        self.bot = bot
        self.data = {'0:20': ['M1911', 'Nagant Revolver', 'P38'], '0:22': ['PPK'], '0:25': ['FNP-9', 'MP-446'], '0:28': ['USP Compact', 'Bren Ten'], '0:30': ['C96', 'P08'], '0:35': ['P99', 'Type 92'], '0:40': ['Astra Revolver', 'M9', 'Makarov'], '0:45': ['Tokarev'], '0:50': ['Colt Revolver', 'Mk23'], '0:52': ['Spitfire'], '0:53': ['K5'], '0:55': ['Stechkin', 'P7'], '1:00': ['Welrod MkII'], '1:02': ['Contender'], '1:05': ['M950A', 'NZ75'], '1:10': ['Grizzly MkV', 'IDW', 'PP-2000'], '1:20': ['m45', 'Spectre M4'], '1:25': ['Type 64'], '1:30': ['Beretta Model 38', 'M3', 'MP40'], '1:40': ['Sten MkII', 'Micro Uzi'], '1:50': ['PPSh-41', 'F1'], '2:00': ['MAC-10', 'Skorpion'], '2:05': ['Z-62'], '2:10': ['PPS-43'], '2:15': ['UMP9', 'UMP45'], '2:18': ['Shipka', 'PP-19-01'], '2:20': ['MP5', 'PP-90'], '2:25': ['Suomi'], '2:28': ['C-MS'], '2:30': ['G36C', 'Thompson'], '2:33': ['SR-3MP'], '2:35': ['Type 79', 'Vector'], '2:40': ['Galil', 'SIG-510'], '2:45': ['F2000', 'Type 63'], '2:50': ['G3', 'L85A1'], '3:00': ['StG44'], '3:10': ['OTs-12', 'G43', 'FN-49'], '3:15': ['ARX-160'], '3:20': ['AK-47', 'FNC', 'BM59'], '3:25': ['Type 56-1', 'XM8'], '3:30': ['AS Val', 'FAMAS', 'TAR-21', 'SVT-38', 'Simonov'], '3:35': ['9A-91'], '3:40': ['G36', 'Ribeyrolles', 'M14', 'SV-98'], '3:45': ['FAL'], '3:48': ['T91'], '3:50': ['Type 95', 'Type 97', 'Hanyang Type 88', 'OTs-44'], '3:52': ['K2'], '3:53': ['MDR'], '3:55': ['HK416'], '3:58': ['RFB'], '4:00': ['M1 Garand'], '4:04': ['G11'], '4:05': ['G41', 'Zas M21'], '4:09': ['AN-94'], '4:10': ['Mosin-Nagant', 'T-5000'], '4:12': ['AK-12'], '4:15': ['SVD'], '4:20': ['PSG-1', 'G28'], '4:25': ['Springfield'], '4:30': ['PTRD', 'PzB 39'], '4:38': ['Carcano M1891'], '4:40': ['Kar98k'], '4:42': ['Carcano M91∕38'], '4:45': ['NTW-20'], '4:50': ['WA2000', 'AAT-52', 'FG42'], '4:52': ['IWS-2000'], '4:55': ['M99'], '5:00': ['Lee-Enfield', 'MG34', 'DP28'], '5:10': ['LWMMG'], '5:20': ['Bren'], '5:40': ['M1919A4'], '5:50': ['MG42'], '6:10': ['M60', 'M2HB'], '6:15': ['Type 80'], '6:20': ['Mk48', 'AEK-999'], '6:25': ['M1918', 'Ameli'], '6:30': ['PK', 'MG3'], '6:35': ['Negev'], '6:40': ['MG4'], '6:45': ['MG5'], '6:50': ['PKP'], '7:14': ['M1014'], '7:15': ['NS2000'], '7:20': ['M500'], '7:25': ['KS-23'], '7:30': ['RMB-93', 'M1897'], '7:40': ['M590', 'SPAS-12'], '7:45': ['M37'], '7:50': ['Super-Shorty'], '7:55': ['USAS-12'], '8:00': ['KSG'], '8:05': ['Saiga-12'], '8:06': ['FP-6'], '8:10': ['S.A.T.8'], '8:12': ['AA-12']}

    @commands.command()
    async def gf(self, ctx, *, unit):
        await ctx.send(f'https://en.gfwiki.com/wiki/{unit.replace(" ","_")}')
        async with self.bot.session.get(f'https://en.gfwiki.com/api.php?action=query&titles=File:{unit.replace(" ","_")}.png&prop=imageinfo&iiprop=url&format=json') as resp:
            json = await resp.json()
        await ctx.send(list(find('url', json))[0])

    @commands.command()
    async def gfp(self, ctx, *, time):
        try:
            await ctx.send(", ".join(self.data[time]))
        except KeyError:
            await ctx.send("unknown time")

def setup(bot):
    bot.add_cog(GirlsFrontier(bot))
