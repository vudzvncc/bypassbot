import os
import re
import time
import asyncio
import requests
import discord
from discord.ext import commands
from flask import Flask
from threading import Thread

# --- 1. SETUP WEB SERVER CHO RENDER (Giữ bot online 24/7) ---
app = Flask('')

@app.route('/')
def home():
    return "Bot Discord Bypass Link đang hoạt động 24/7 trên Render!"

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run_flask)
    t.daemon = True
    t.start()

# --- 2. KHỞI TẠO DISCORD BOT ---
intents = discord.Intents.default()
intents.message_content = True
# Tắt help command mặc định để tạo help command tùy chỉnh không bị xung đột
bot = commands.Bot(command_prefix=['/', '!'], intents=intents, help_command=None)

# --- 3. HÀM TẠO THANH PHẦN TRĂM (PROGRESS BAR) ---
def make_progress_bar(percent):
    total_blocks = 10
    filled_blocks = int(total_blocks * percent // 100)
    bar = '█' * filled_blocks + '░' * (total_blocks - filled_blocks)
    return f"[{bar}] {percent}%"

async def update_progress(message, status_text, percent):
    progress_bar = make_progress_bar(percent)
    embed = discord.Embed(
        title="⏳ **Đang xử lý link...**",
        color=discord.Color.blue()
    )
    embed.add_field(name="📌 Trạng thái", value=status_text, inline=False)
    embed.add_field(name="📊 Tiến độ", value=f"`{progress_bar}`", inline=False)
    try:
        await message.edit(embed=embed)
    except Exception:
        pass

# --- 4. HÀM BYPASS LINK QUA API ---
def bypass_link_service(url):
    """Sử dụng API công khai để giải mã link"""
    try:
        api_url = f"https://api.bypass.vip/bypass?url={url}"
        response = requests.get(api_url, timeout=15)
        if response.status_code == 200:
            data = response.json()
            if data.get("status") == "success":
                return data.get("destination")
    except Exception:
        pass

    try:
        api_url_2 = f"https://bypass.pm/api/bypass?url={url}"
        response2 = requests.get(api_url_2, timeout=15)
        if response2.status_code == 200:
            data2 = response2.json()
            if data2.get("success"):
                return data2.get("destination")
    except Exception:
        pass

    return None

# --- 5. QUY TRÌNH XỬ LÝ LỆNH BYPASS ---
async def process_bypass(ctx, raw_arg, service_name):
    # Trích xuất URL từ cú pháp link:URL
    link = raw_arg.replace("link:", "").strip() if raw_arg else ""

    if not link or not link.startswith("http"):
        embed_err = discord.Embed(
            title="❌ **Lỗi Cú Pháp!**",
            description="Vui lòng cung cấp link hợp lệ!\n👉 **Cú pháp đúng:** `/<command> link:<URL>`",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed_err)
        return

    # Khởi tạo Embed hiển thị tiến trình
    embed_start = discord.Embed(
        title=f"🚀 **Bắt đầu bypass link {service_name}...**",
        color=discord.Color.gold()
    )
    embed_start.add_field(name="📊 Tiến độ", value=f"`{make_progress_bar(0)}`", inline=False)
    status_msg = await ctx.send(embed=embed_start)

    await asyncio.sleep(1)
    await update_progress(status_msg, "🔍 Đang kiểm tra link...", 25)

    await asyncio.sleep(1)
    await update_progress(status_msg, "🔓 Đang giải mã và bypass link...", 65)

    # Thực hiện request API ở background thread
    loop = asyncio.get_event_loop()
    result_link = await loop.run_in_executor(None, bypass_link_service, link)

    await asyncio.sleep(1)
    await update_progress(status_msg, "✅ Hoàn tất xử lý!", 100)
    await asyncio.sleep(0.5)

    if result_link:
        embed_success = discord.Embed(
            title="🎉 **Bypass Thành Công!** 🎉",
            color=discord.Color.green()
        )
        embed_success.add_field(name="🔗 Link Gốc", value=f"`{link}`", inline=False)
        embed_success.add_field(name="✅ Link Đích", value=f"[Nhấn vào đây để truy cập]({result_link})\n`{result_link}`", inline=False)
        embed_success.set_footer(text="✨ Cảm ơn bạn đã sử dụng dịch vụ!")
        await status_msg.edit(embed=embed_success)
    else:
        embed_fail = discord.Embed(
            title="❌ **Bypass Thất Bại!**",
            description="Không thể bypass link này! Link có thể bị hỏng hoặc dịch vụ chưa hỗ trợ.",
            color=discord.Color.red()
        )
        await status_msg.edit(embed=embed_fail)

# --- 6. EVENT VÀ LỆNH BOT (Tất cả đều là async def) ---
@bot.event
async def on_ready():
    print(f"🤖 Bot Discord {bot.user} đã sẵn sàng hoạt động!")
    await bot.change_presence(activity=discord.Game(name="/help để xem hướng dẫn"))

@bot.command(name='help')
async def custom_help(ctx):
    embed = discord.Embed(
        title="🤖 **DISCORD BYPASS LINK BOT** 🤖",
        description="Danh sách các lệnh hỗ trợ:",
        color=discord.Color.blue()
    )
    embed.add_field(name="📜 `/help`", value="Xem hướng dẫn và danh sách lệnh", inline=False)
    embed.add_field(name="✂️ `/cuty link:<URL>`", value="Bypass link cuty.io hoặc cuttty.com", inline=False)
    embed.add_field(name="🔹 `/shrinkme link:<URL>`", value="Bypass link ShrinkMe.io", inline=False)
    embed.add_field(name="⚙️ `/workink link:<URL>`", value="Bypass link Work.ink", inline=False)
    embed.add_field(name="💡 **Ví dụ cú pháp:**", value="`/cuty link:https://cuty.io/example`", inline=False)
    await ctx.send(embed=embed)

@bot.command(name='cuty')
async def cuty_cmd(ctx, *, arg: str = None):
    if not arg:
        await ctx.send("⚠️ **Thiếu link!** Cú pháp đúng: `/cuty link:https://cuty.io/xyz`")
        return
    await process_bypass(ctx, arg, "Cuty.io")

@bot.command(name='shrinkme')
async def shrinkme_cmd(ctx, *, arg: str = None):
    if not arg:
        await ctx.send("⚠️ **Thiếu link!** Cú pháp đúng: `/shrinkme link:https://shrinkme.io/xyz`")
        return
    await process_bypass(ctx, arg, "ShrinkMe.io")

@bot.command(name='workink')
async def workink_cmd(ctx, *, arg: str = None):
    if not arg:
        await ctx.send("⚠️ **Thiếu link!** Cú pháp đúng: `/workink link:https://work.ink/xyz`")
        return
    await process_bypass(ctx, arg, "Work.ink")

# --- 7. CHẠY BOT ---
if __name__ == '__main__':
    keep_alive() # Khởi chạy Flask Server để giữ bot online trên Render
    token = os.environ.get("DISCORD_TOKEN", "YOUR_DISCORD_BOT_TOKEN_HERE")
    bot.run(token)
