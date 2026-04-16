iimport os
import discord
from discord.ext import commands
import requests

# Configuración del TOKEN
TOKEN = os.environ.get("DISCORD_BOT_TOKEN")

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# DICCIONARIO CORREGIDO (IDs oficiales de Sim Companies)
PRODUCTOS = {
    # Energía y Minería
    "agua": 1, "energia": 2, "petroleo": 12, "mineral_hierro": 42, "bauxita": 15, 
    "silicio": 16, "oro": 46, "oro_barras": 47, "carbon": 41, "metano": 74,
    # Agricultura
    "semillas": 66, "manzanas": 3, "naranjas": 4, "uvas": 10, "grano": 6, 
    "filetes": 7, "salchichas": 8, "huevos": 9, "caña_azucar": 72, "algodon": 40, 
    "leche": 117, "cafe": 118, "vegetales": 120, "pan": 133, "queso": 137,
    # Construcción (IDs Corregidos)
    "hormigon": 100, "piedra_caliza": 101, "arcilla": 102, "cemento": 103, 
    "ladrillos": 104, "madera": 106, "tablones": 108, "ventanas": 109, "unidades": 110,
    # Electrónica
    "procesadores": 24, "componentes_electronicos": 21, "baterias": 22, 
    "pantallas": 23, "smartphones": 26, "tablets": 25, "laptops": 27, 
    "monitores": 28, "televisores": 29, "software": 65, "robots": 114,
    # Otros
    "transporte": 13, "acero": 43, "vidrio": 45, "aluminio": 18, "plastico": 19, "cuero": 44,
    "camiones": 57, "coche_economico": 55, "coche_lujo": 56
}

@bot.event
async def on_ready():
    print(f'Bot {bot.user} está en línea y corregido.')

@bot.command()
async def precio(ctx, *, producto: str):
    producto_key = producto.lower().replace(" ", "_")

    if producto_key not in PRODUCTOS:
        await ctx.send(f"No encuentro '{producto}'. Usa !productos para ver la lista.")
        return

    id_prod = PRODUCTOS[producto_key]
    # URL Corregida: API v3 + Realm 0 (Magnates)
    url = f"https://simcompanies.com{id_prod}/"

    try:
        response = requests.get(url, headers={"User-Agent": "SimCompaniesBot/1.0"})
        response.raise_for_status()
        data = response.json()

        if not data:
            await ctx.send(f"No hay ofertas de **{producto}** en el mercado.")
            return

        mejor = data[0]
        p_actual = mejor['price']
        cantidad = mejor['quantity']
        calidad = mejor['quality']
        
        # El transporte en la API v3 se calcula con 'fees'
        fees = mejor.get('fees', 0)
        transporte_ud = fees / cantidad if cantidad > 0 else 0
        
        # Cálculos de rentabilidad
        precio_contrato = p_actual * 0.97
        tasa_mercado = p_actual * 0.04
        neto_mercado = p_actual - transporte_ud - tasa_mercado

        embed = discord.Embed(
            title=f"Mercado: {producto.capitalize()}",
            color=discord.Color.blue()
        )
        embed.add_field(name="Mejor Precio", value=f"${p_actual:,.2f}", inline=True)
        embed.add_field(name="Calidad", value=f"Q{calidad}", inline=True)
        embed.add_field(name="Cantidad", value=f"{cantidad:,}", inline=True)
        
        embed.add_field(name="Costo Transporte/ud", value=f"${transporte_ud:,.3f}", inline=True)
        embed.add_field(name="Venta Contrato (-3%)", value=f"${precio_contrato:,.2f}", inline=True)
        embed.add_field(
            name="Resumen de Venta en Mercado (Neto)",
            value=f"Precio: ${p_actual:,.2f}\n- Transporte: ${transporte_ud:,.2f}\n- Comisión (4%): ${tasa_mercado:,.2f}\n**Total Neto: ${neto_mercado:,.2f}**",
            inline=False
        )

        await ctx.send(embed=embed)

    except Exception as e:
        await ctx.send("Error al conectar con la API de Sim Companies.")
        print(f"Error: {e}")

@bot.command()
async def productos(ctx):
    # Genera una lista simple para no saturar el mensaje de Discord
    lista = ", ".join(sorted(PRODUCTOS.keys()))
    embed = discord.Embed(
        title="Productos Disponibles",
        description=f"```{lista}```",
        color=discord.Color.green()
    )
    await ctx.send(embed=embed)

if not TOKEN:
    print("ERROR: Falta DISCORD_BOT_TOKEN.")
else:
    bot.run(TOKEN)
