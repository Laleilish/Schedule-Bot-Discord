import discord
from discord.ext import commands
import json
from datetime import datetime
import os 
from keep_alive import keep_alive

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

FILE = "tugas.json"


def load_tugas():
    try:
        with open(FILE, "r") as f:
            return json.load(f)["tugas"]
    except:
        return []


def save_tugas(tugas):
    with open(FILE, "w") as f:
        json.dump({"tugas": tugas}, f, indent=4)


@bot.event
async def on_ready():
    print(f"✅ Bot aktif {bot.user}")


@bot.command(name="addtugas")
async def tambahtugas(ctx, *, arg):
    try:
        nama, deadline = [x.strip() for x in arg.split("|")]
        dt = datetime.strptime(deadline, "%Y-%m-%d %H:%M")
        tugas = load_tugas()
        tugas.append({
            "nama": nama,
            "deadline": dt.strftime("%Y-%m-%d"),
            "waktu": dt.strftime("%H:%M")
        })
        save_tugas(tugas)
        await ctx.send(
            f"✅ Tugas **'{nama}'** ditambahkan!\n📅 Deadline: `{dt.strftime('%Y-%m-%d %H:%M')}`"
        )
    except:
        await ctx.send(
            "⚠️ Format salah! Contoh: `!addtugas PBO Bab 5 | 2025-04-15 23:59`"
        )


@bot.command(name="deltugas")
async def hapustugas(ctx, *, nama):
    tugas = load_tugas()
    baru = [t for t in tugas if t["nama"].lower() != nama.lower()]
    if len(baru) < len(tugas):
        save_tugas(baru)
        await ctx.send(f"🗑️ Tugas **'{nama}'** berhasil dihapus.")
    else:
        await ctx.send(f"⚠️ Tugas **'{nama}'** gak ditemukan.")


@bot.command(name="tugas")
async def tugaskelas(ctx):
    tugas = load_tugas()
    if not tugas:
        await ctx.send("📭 Belum ada tugas yang dicatat.")
        return

    now = datetime.now()
    bulan_ini = now.month
    tahun_ini = now.year

    tugas_bulan_ini = [
        t for t in tugas
        if datetime.strptime(t["deadline"], "%Y-%m-%d").month == bulan_ini
        and datetime.strptime(t["deadline"], "%Y-%m-%d").year == tahun_ini
    ]

    if not tugas_bulan_ini:
        await ctx.send("🎉 Tidak ada tugas untuk bulan ini!")
        return

    tugas_bulan_ini = sorted(tugas_bulan_ini,
                             key=lambda x: x["deadline"] + " " + x["waktu"])
    embed = discord.Embed(
        title="📅 TUGAS BULAN INI",
        description="These are your upcoming scheduled tasks!",
        color=0x2ecc71)

    for t in tugas_bulan_ini:
        tanggal = datetime.strptime(t["deadline"],
                                    "%Y-%m-%d").strftime("%d/%m/%Y")
        waktu = t.get("waktu", "23:59")
        nama_tugas = t["nama"]
        embed.add_field(name=f"🗓️ {tanggal}",
                        value=f"`{waktu}` | **{nama_tugas}**",
                        inline=False)

    await ctx.send(embed=embed)

keep_alive()
bot.run(os.getenv("SECRET_TOKEN"))
