import os
import discord
from discord.ext import commands
import requests

# Configuración del Bot
TOKEN = os.environ.get("DISCORD_BOT_TOKEN")

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# Diccionario Completo de IDs (Realm 0 - Magnates)
PRODUCTOS = {
    # Energia y Mineria
    "agua": 1, "energia": 2, "petroleo": 12, "mineral_hierro": 42, "bauxita": 15, 
    "silicio": 16, "oro": 46, "oro_barras": 47, "carbon": 41, "metano": 74, "arena": 73,
    # Agricultura y Alimentos
    "semillas": 66, "manzanas": 3, "naranjas": 4, "uvas": 10, "grano": 6, 
    "filetes": 7, "salchichas": 8, "huevos": 9, "caña_azucar": 72, "algodon": 40, 
    "leche": 117, "cafe": 118, "vegetales": 120, "pan": 133, "queso": 137,
    # Materiales y Construccion
    "unidades": 110, "acero": 43, "vidrio": 45, "aluminio": 18, "plastico": 19, "cuero": 44,
    "hormigon": 100, "ladrillos": 104, "madera": 106, "tablones": 108, "ventanas": 109, 
    "cemento": 103, "arcilla": 102, "piedra_caliza": 101, "vigas_acero": 107,
    # Electronica y Tecnologia
    "procesadores": 24, "componentes_electronicos": 21, "baterias": 22, 
    "pantallas": 23, "smartphones": 26, "tablets": 25, "laptops": 27, 
    "monitores": 28, "televisores": 29, "software": 65, "robots": 114,
    # Automotriz
    "motores_combustion": 52, "motores_electricos": 53, "carroceria": 51, "neumaticos": 54,
    "interior_lujo": 50, "coche_economico": 55, "coche_lujo": 56, "camiones": 57,
    "e-car_economico": 60, "e-car_lujo": 61, "bulldozer": 112, "computadora_a_bordo": 59,
    # Aeroespacial
    "combustible_cohete": 83, "propulsor_solido": 85, "tanque_propulsor": 84, "motor_cohete": 86,
    "motor_jet": 89, "propulsor_ionico": 88, "fuselaje": 77, "alas": 78, "cabina": 81,
    "computadora_vuelo": 80, "satelite": 99, "avion_lujo": 96, "jumbo_jet": 95, 
    "avion_monomotor": 97, "quadcopter": 98, "starship": 93, "bfr": 94, "escudo_termico": 87,
    "control_actitud": 82, "sub-orbital_2nd_stage": 90, "sub-orbital_rocket": 91,
    # Otros
    "fibra_carbono": 75, "compuesto_carbono": 76, "quimicos": 17, "transporte": 13
}

@bot.event
async def on_ready():
    print(f'Bot conectado como {bot.user}')

@bot.command()
async def precio(ctx, *, producto: str):
    producto_key = producto.lower().replace(" ", "_")
    if producto_key not in PRODUCTOS:
        await ctx.send(f"❌ No encuentro '{producto}'. Usa `!productos` para ver la lista.")
        return

    id_prod = PRODUCTOS[producto_key]
    url = f"https://simcompanies.com{id_prod}/"

    try:
        response = requests.get(url, headers={"User-Agent": "SimCompaniesBot/1.0"})
        data = response.json()

        if not data:
            await ctx.send("📭 No hay ofertas en el mercado ahora mismo.")
            return

        mejor = data[0]
        p_mercado = mejor['price']
        cant = mejor['quantity']
        q = mejor['quality']
        
        # Cálculos de deducciones
        transporte_ud = mejor.get('fees', 0) / cant if cant > 0 else 0
        tasa_mercado = p_mercado * 0.04
        neta_mercado = p_mercado - transporte_ud - tasa_mercado
        precio_contrato = p_mercado * 0.97  # Sugerencia estándar del 3%

        embed = discord.Embed(
            title=f"📊 Mercado: {producto.title()}",
            color=discord.Color.blue(),
            description="Valores calculados para el reino **Magnates**"
        )
        embed.add_field(name="Mejor Precio", value=f"${p_mercado:,.3f} (Q{q})", inline=True)
        embed.add_field(name="Cantidad", value=f"{cant:,} uds", inline=True)
        embed.add_field(name="Costo Transporte", value=f"${transporte_ud:,.3f}/ud", inline=True)
        embed.add_field(name="Neto Mercado (4%)", value=f"**${neta_mercado:,.3f}**", inline=True)
        embed.add_field(name="Sugerencia Contrato (-3%)", value=f"${precio_contrato:,.3f}", inline=True)
        embed.set_footer(text="Datos de Sim Companies API v3")

        await ctx.send(embed=embed)

    except Exception as e:
        await ctx.send("⚠️ Error al consultar la API.")
        print(e)

@bot.command()
async def productos(ctx):
    # Dividido en trozos porque Discord limita los campos de los Embeds
    embed = discord.Embed(title="📦 Productos Soportados", color=discord.Color.green())
    
    categorias = {
        "Minería y Energía": ["agua", "energia", "petroleo", "mineral_hierro", "bauxita", "silicio", "oro", "oro_barras", "carbon", "metano", "arena"],
        "Automotriz": ["motores_combustion", "motores_electricos", "carroceria", "neumaticos", "coche_economico", "coche_lujo", "camiones", "e-car_economico"],
        "Aeroespacial": ["combustible_cohete", "motor_jet", "fuselaje", "alas", "computadora_vuelo", "satelite", "avion_lujo", "starship"],
        "Construcción": ["unidades", "hormigon", "ladrillos", "madera", "tablones", "vigas_acero", "cemento"]
    }

    for cat, items in categorias.items():
        embed.add_field(name=cat, value=", ".join(items), inline=False)
    
    await ctx.send(embed=embed)

if TOKEN:
    bot.run(TOKEN)
else:
    print("Error: No se encontró el TOKEN en las variables de entorno.")
