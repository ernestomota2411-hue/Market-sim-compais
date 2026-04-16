import os
import discord
from discord.ext import commands
import requests

# Configuración del TOKEN
TOKEN = os.environ.get("DISCORD_BOT_TOKEN")

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# Diccionario con IDs oficiales
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

@bot.event
async def on_ready():
    print(f'Bot {bot.user} está en línea.')

@bot.command()
async def precio(ctx, *, producto: str):
    producto_key = producto.lower().replace(" ", "_")

    if producto_key not in PRODUCTOS:
        await ctx.send(f"No encuentro '{producto}'. Usa !productos.")
        return

    id_prod = PRODUCTOS[producto_key]
    
    # CORRECCIÓN: URL de la API v3 (Realm 0 = Magnates)
    url = f"https://simcompanies.com{id_prod}/"

    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        if not data or len(data) == 0:
            await ctx.send(f"No hay ofertas de **{producto}** en el mercado.")
            return

        # Obtenemos la mejor oferta (la primera)
        mejor = data[0]
        p_actual = mejor['price']
        cantidad = mejor['quantity']
        calidad = mejor['quality']
        
        # En la API v3, el costo de transporte se deduce de 'transport' (unidades de transporte necesarias)
        # Para calcular el costo monetario, necesitaríamos el precio del transporte actual, 
        # pero usaremos una aproximación o el valor de la API si está disponible.
        transp_needed = mejor.get('transport', 0)
        
        # Cálculos estándar
        precio_contrato = p_actual * 0.97
        comision_mercado = p_actual * 0.03 # La comisión real es 3%
        neto_mercado = p_actual - comision_mercado

        embed = discord.Embed(
            title=f"Mercado: {producto.capitalize()}",
            color=discord.Color.blue()
        )
        embed.add_field(name="Mejor Precio", value=f"${p_actual:,.2f}", inline=True)
        embed.add_field(name="Calidad", value=f"Q{calidad}", inline=True)
        embed.add_field(name="Cantidad", value=f"{cantidad:,}", inline=True)
        
        embed.add_field(name="Transporte req.", value=f"{transp_needed} uds", inline=True)
        embed.add_field(name="Venta Contrato (-3%)", value=f"${precio_contrato:,.2f}", inline=True)
        embed.add_field(
            name="Resumen de Venta en Mercado (Neto)",
            value=f"Precio: ${p_actual:,.2f}\n- Comisión (3%): ${comision_mercado:,.2f}\n**Total Neto: ${neto_mercado:,.2f}**\n*(Sin contar costo de transporte)*",
            inline=False
        )

        await ctx.send(embed=embed)

    except Exception as e:
        await ctx.send("Error al conectar con la API de Sim Companies.")
        print(f"Error: {e}")

@bot.command()
async def productos(ctx):
    lista = ", ".join(sorted(PRODUCTOS.keys()))
    # Dividir en partes si la lista es muy larga (Discord limita a 2000 caracteres)
    if len(lista) > 2000:
        lista = lista[:1990] + "..."
    
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
    
