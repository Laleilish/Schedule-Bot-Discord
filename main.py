import discord
from discord import app_commands
from discord.ext import commands
import json
from datetime import datetime
import os
from keep_alive import keep_alive

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

FILE = "tugas.json"
ALLOWED_CHANNEL_ID = "Channel ID"


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
    try:
        synced = await bot.tree.sync()
        print(f"✅ {len(synced)} slash command berhasil disinkronisasi.")
    except Exception as e:
        print(f"❌ Gagal sync: {e}")


# ========== /addtugas ==========
@bot.tree.command(name="addtugas", description="Tambah tugas ke daftar")
@app_commands.describe(nama="Nama tugas",
                       deadline="Deadline format YYYY-MM-DD HH:MM")
async def addtugas(interaction: discord.Interaction, nama: str, deadline: str):
    if interaction.channel.id != ALLOWED_CHANNEL_ID:
        await interaction.response.send_message(
            "Di sini bang <Channel ID>", ephemeral=True)
        return

    try:
        dt = datetime.strptime(deadline, "%Y-%m-%d %H:%M")
        tugas = load_tugas()
        tugas.append({
            "nama": nama,
            "deadline": dt.strftime("%Y-%m-%d"),
            "waktu": dt.strftime("%H:%M")
        })
        save_tugas(tugas)

        await interaction.response.send_message(
            f"✅ Tugas **'{nama}'** ditambahkan!\n📅 Deadline: `{dt.strftime('%Y-%m-%d %H:%M')}`",
            ephemeral=True)
    except:
        await interaction.response.send_message(
            "⚠️ Format deadline salah! Contoh: `2025-04-15 23:59`",
            ephemeral=True)


# ========== /deltugas ==========
@bot.tree.command(name="deltugas", description="Hapus tugas dari daftar")
@app_commands.describe(nama="Nama tugas yang mau dihapus")
async def deltugas(interaction: discord.Interaction, nama: str):
    if interaction.channel.id != ALLOWED_CHANNEL_ID:
        await interaction.response.send_message(
            "Di sini bang <Channel ID>", ephemeral=True)
        return

    tugas = load_tugas()
    baru = [t for t in tugas if t["nama"].lower() != nama.lower()]
    if len(baru) < len(tugas):
        save_tugas(baru)
        await interaction.response.send_message(
            f"🗑️ Tugas **'{nama}'** berhasil dihapus.", ephemeral=True)
    else:
        await interaction.response.send_message(
            f"⚠️ Tugas **'{nama}'** gak ditemukan.", ephemeral=True)


# ========== /tugas ==========
@bot.tree.command(name="tugas", description="Lihat daftar tugas bulan ini")
async def tugaskelas(interaction: discord.Interaction):
    if interaction.channel.id != ALLOWED_CHANNEL_ID:
        await interaction.response.send_message(
            "Di sini bang <Channel ID>", ephemeral=True)
        return

    tugas = load_tugas()
    if not tugas:
        await interaction.response.send_message(
            "📭 Belum ada tugas yang dicatat.", ephemeral=True)
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
        await interaction.response.send_message(
            "🎉 Tidak ada tugas untuk bulan ini!", ephemeral=True)
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

    await interaction.response.send_message(embed=embed)


keep_alive()
bot.run(os.getenv("SECRET_TOKEN"))
