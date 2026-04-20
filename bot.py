import os
import discord
from discord.ext import commands
import requests

TOKEN = os.environ.get("DISCORD_BOT_TOKEN")

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

PRODUCTOS = {
    "energia": 1, "agua": 2, "manzanas": 3, "naranjas": 4, "petroleo": 5,
    "grano": 6, "filetes": 7, "salchichas": 8, "huevos": 9, "gasolina": 11, "diesel": 12,
    "unidades": 111, "transporte": 13,
    "bauxita": 15, "silicio": 16, "aluminio": 18, "plastico": 19,
    "procesadores": 20, "componentes_electronicos": 21, "baterias": 22,
    "pantallas": 23, "smartphones": 24, "tablets": 25, "laptops": 26,
    "monitores": 27, "televisores": 28,
    "investigacion_energia": 30, "investigacion_mineria": 31, "investigacion_electronica": 32,
    "algodon": 40, "mineral_hierro": 42, "acero": 43, "arena": 44, "vidrio": 45,
    "cuero": 46, "motores_electricos": 48,
    "motores_combustion": 52, "coche_economico": 55, "coche_lujo": 56,
    "carroceria": 57, "neumaticos": 58,
    "ropa": 62, "bolsos": 64, "software": 65, "semillas": 66,
    "oro": 68, "oro_barras": 69, "caña_azucar": 72, "metano": 74,
    "fuselaje": 77, "compuesto_carbono": 76,"alas": 78, "electronico_alto": 79, "computadora_vuelo": 80,
    "combustible_cohete": 83, "motor_jet": 89, "propulsor": 92,
    "avion_lujo": 96, "satelite": 99,
    "hormigon": 101, "ladrillos": 102, "cemento": 103 , "arcilla": 104,
    "piedra_caliza": 105, "madera": 106, "tablones": 108, "ventanas": 109, 
    "robots": 114, "leche": 117, "cafe": 118, "vegetales": 120,
    "pan": 133, "azucar": 135, "queso": 137,
    "uvas": 10, "camiones": 59,
}

@bot.event
async def on_ready():
    print(f'{bot.user} conectado y listo.')

@bot.command()
async def precio(ctx, *, producto: str):
    producto = producto.lower().replace(" ", "_")

    if producto not in PRODUCTOS:
        await ctx.send(f"No encuentro el producto '{producto}'. Usa !productos para ver la lista.")
        return

    id_prod = PRODUCTOS[producto]
    url = f"https://www.simcompanies.com/api/v3/market/0/{id_prod}/"

    try:
        response = requests.get(url, headers={"User-Agent": "SimCompaniesBot/1.0"})
        data = response.json()

        if not data:
            await ctx.send("No hay ofertas en el mercado ahora mismo.")
            return

        mejor = data[0]
        p_actual = mejor['price']
        cantidad = mejor['quantity']
        calidad = mejor['quality']
        fees = mejor.get('fees', 0)
        transporte_ud = fees / cantidad if cantidad > 0 else 0
        precio_venta = p_actual * 0.97

        embed = discord.Embed(
            title=f"Mercado: {producto.replace('_', ' ').capitalize()}",
            color=discord.Color.blue(),
            description="Datos del reino de Magnates (Realm 0)"
        )
        embed.add_field(name="Precio mercado", value=f"${p_actual:,.3f}", inline=True)
        embed.add_field(name="Calidad", value=f"Q{calidad}", inline=True)
        embed.add_field(name="Cantidad", value=f"{cantidad:,} unidades", inline=True)
        tasa_mercado = p_actual * 0.04
        venta_mercado_neta = p_actual - transporte_ud - tasa_mercado

        embed.add_field(name="Costo transporte/ud", value=f"${transporte_ud:,.3f}", inline=True)
        embed.add_field(name="Tasa venta mercado (4%)", value=f"${tasa_mercado:,.3f}", inline=True)
        embed.add_field(name="Venta por contrato (-3%)", value=f"${precio_venta:,.3f} /ud", inline=True)
        embed.add_field(
            name="Vender producción en mercado",
            value=f"${p_actual:,.3f} − ${transporte_ud:,.3f} transporte − ${tasa_mercado:,.3f} tasa (4%) = **${venta_mercado_neta:,.3f}** /ud",
            inline=False
        )

        await ctx.send(embed=embed)

    except Exception as e:
        await ctx.send("Hubo un problema al consultar la API.")
        print(f"Error: {e}")

@bot.command()
async def precioq(ctx, *, producto: str):
    producto = producto.lower().replace(" ", "_")

    if producto not in PRODUCTOS:
        await ctx.send(f"No encuentro el producto '{producto}'. Usa !productos para ver la lista.")
        return

    id_prod = PRODUCTOS[producto]
    url = f"https://www.simcompanies.com/api/v3/market/0/{id_prod}/"

    try:
        response = requests.get(url, headers={"User-Agent": "SimCompaniesBot/1.0"})
        data = response.json()

        if not data:
            await ctx.send("No hay ofertas en el mercado ahora mismo.")
            return

        # Agrupar por calidad y quedarse con el precio más barato de cada una
        por_calidad = {}
        for oferta in data:
            q = oferta['quality']
            if q not in por_calidad or oferta['price'] < por_calidad[q]['price']:
                por_calidad[q] = oferta

        embed = discord.Embed(
            title=f"Precios por calidad: {producto.replace('_', ' ').capitalize()}",
            color=discord.Color.gold(),
            description="Mejor precio disponible por nivel de calidad (Realm 0)"
        )

        for q in sorted(por_calidad.keys()):
            oferta = por_calidad[q]
            precio_venta = oferta['price'] * 0.97
            cant = oferta['quantity']
            fees = oferta.get('fees', 0)
            transporte_ud = fees / cant if cant > 0 else 0
            tasa_mercado = oferta['price'] * 0.04
            venta_mercado_neta = oferta['price'] - transporte_ud - tasa_mercado
            embed.add_field(
                name=f"Q{q} — {cant:,} uds",
                value=(
                    f"Precio mercado: ${oferta['price']:,.3f}\n"
                    f"Transporte/ud: ${transporte_ud:,.3f}\n"
                    f"Tasa venta (4%): ${tasa_mercado:,.3f}\n"
                    f"Contrato (-3%): ${precio_venta:,.3f}\n"
                    f"Vender en mercado: **${venta_mercado_neta:,.3f}**/ud"
                ),
                inline=True
            )

        await ctx.send(embed=embed)

    except Exception as e:
        await ctx.send("Hubo un problema al consultar la API.")
        print(f"Error: {e}")

@bot.command()
async def productos(ctx):
    categorias = {
        "Energia y Mineria": ["energia", "agua", "petroleo", "mineral_hierro", "arena", "bauxita",
                               "silicio", "oro", "oro_barras", "carbon", "arcilla", "piedra_caliza", "metano", "gasolina", "diesel"],
        "Agricultura y Alimentos": ["semillas", "manzanas", "naranjas", "uvas", "grano", "filetes",
                                     "salchichas", "huevos", "caña_azucar", "algodon", "leche", "cafe",
                                     "vegetales", "pan", "queso", "azucar"],
        "Materiales y Construccion": ["unidades", "acero", "vidrio", "aluminio", "plastico",
                                       "cuero", "hormigon", "ladrillos", "madera", "tablones", "ventanas", "cemento" ],
        "Electronica y Tecnologia": ["procesadores", "componentes_electronicos", "baterias", "pantallas",
                                      "smartphones", "tablets", "laptops", "monitores", "televisores",
                                      "software", "robots", "electronico_alto"],
        "Automotriz": ["motores_combustion", "motores_electricos", "carroceria", "neumaticos",
                        "coche_economico", "coche_lujo", "camiones", "compuesto_carbono"],
        "Aeroespacial": ["combustible_cohete", "propulsor", "satelite", "avion_lujo", "fuselaje",
                          "alas", "motor_jet", "computadora_vuelo"],
    }

    embed = discord.Embed(
        title="Productos disponibles",
        color=discord.Color.green(),
        description="Usa !precio <nombre> para consultar el precio.\nReemplaza espacios con _ (ejemplo: !precio oro_barras)"
    )

    for categoria, items in categorias.items():
        embed.add_field(
            name=categoria,
            value=", ".join(items),
            inline=False
        )

    await ctx.send(embed=embed)

if not TOKEN:
    print("ERROR: No se encontro DISCORD_BOT_TOKEN. Configura el secreto primero.")
else:
    bot.run(TOKEN)
