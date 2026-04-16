import os
import discord
from discord.ext import commands
import requests

TOKEN = os.environ.get("DISCORD_BOT_TOKEN")

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# IDs oficiales de Sim Companies
PRODUCTOS = {
    "agua": 1, "energia": 2, "petroleo": 12, "mineral_hierro": 42, "bauxita": 15, 
    "silicio": 16, "oro": 46, "oro_barras": 47, "carbon": 41, "metano": 74,
    "semillas": 66, "manzanas": 3, "naranjas": 4, "uvas": 10, "grano": 6, 
    "filetes": 7, "salchichas": 8, "huevos": 9, "caña_azucar": 72, "algodon": 40, 
    "leche": 117, "cafe": 118, "vegetales": 120, "pan": 133, "queso": 137,
    "hormigon": 100, "piedra_caliza": 101, "arcilla": 102, "cemento": 103, 
    "ladrillos": 104, "madera": 106, "tablones": 108, "ventanas": 109, "unidades": 110,
    "procesadores": 24, "componentes_electronicos": 21, "baterias": 22, 
    "pantallas": 23, "smartphones": 26, "tablets": 25, "laptops": 27, 
    "monitores": 28, "televisores": 29, "software": 65, "robots": 114,
    "transporte": 13, "acero": 43, "vidrio": 45, "aluminio": 18, "plastico": 19, "cuero": 44,
    "camiones": 57, "coche_economico": 55, "coche_lujo": 56
}

@bot.command()
async def precio(ctx, *, producto: str):
    producto_key = producto.lower().replace(" ", "_")
    if producto_key not in PRODUCTOS:
        await ctx.send(f"No encuentro '{producto}'.")
        return

    id_prod = PRODUCTOS[producto_key]
    # URL oficial v3 para el Realm 0 (Magnates)
    url = f"https://simcompanies.com{id_prod}/"
    
    # IMPORTANTE: El servidor a veces bloquea peticiones sin un User-Agent de navegador
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()

        if not data or len(data) == 0:
            await ctx.send(f"No hay ofertas para **{producto}**.")
            return

        # La API v3 devuelve una LISTA de ofertas, tomamos la primera (la más barata)
        mejor_oferta = data[0] 
        p_actual = mejor_oferta['price']
        cantidad = mejor_oferta['quantity']
        calidad = mejor_oferta['quality']
        vendedor = mejor_oferta['seller']['company']

        embed = discord.Embed(title=f"Mercado: {producto.capitalize()}", color=0x00ff00)
        embed.add_field(name="Precio Mínimo", value=f"${p_actual:,.3f}", inline=True)
        embed.add_field(name="Calidad", value=f"Q{calidad}", inline=True)
        embed.add_field(name="Cantidad", value=f"{cantidad:,}", inline=True)
        embed.add_field(name="Vendedor", value=vendedor, inline=False)
        embed.set_footer(text="Datos de Sim Companies API v3")

        await ctx.send(embed=embed)

    except Exception as e:
        print(f"Error detallado: {e}")
        await ctx.send("Hubo un problema al consultar la API. Verifica que el ID del producto sea correcto.")

@bot.run(TOKEN)
