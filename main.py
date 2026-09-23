import os
import time
import asyncio
from threading import Thread
from flask import Flask
import discord
from discord.ext import commands
from discord import app_commands
import aiohttp

# ==========================================
# 1. WEB SERVER GIỮ BOT ONLINE (FLASK)
# ==========================================
app = Flask('')

@app.route('/')
def home():
    return "Bot Bypass Link đang hoạt động 24/7!"

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run_flask)
    t.daemon = True
    t.start()


# ==========================================
# 2. CẤU HÌNH DISCORD BOT & SLASH COMMANDS
# ==========================================
intents = discord.Intents.default()
intents.message_content = True

class BypassBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        print("🔄 Đang đồng bộ Slash Commands...")
        synced = await self.tree.sync()
        print(f"✅ Đã đồng bộ thành công {len(synced)} lệnh Slash!")

bot = BypassBot()


# ==========================================
# 3. THANH TIẾN TRÌNH UNICODE (%)
# ==========================================
def create_progress_bar(percent: int, length: int = 10) -> str:
    filled_length = int(length * percent // 100)
    bar = '█' * filled_length + '░' * (length - filled_length)
    return f"`[{bar}] {percent}%`"


# ==========================================
# 4. HÀM BYPASS TỔNG HỢP (MULTI-API)
# ==========================================
async def fetch_bypassed_url(target_url: str) -> str:
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    # Danh sách các API bypass chuyên dụng
    api_sources = [
        f"https://api.bypasser.su/api/bypass?url={target_url}",
        f"https://free-bypass-api.vercel.app/api/bypass?url={target_url}",
        f"https://ethon.site/api/bypass?url={target_url}"
    ]

    async with aiohttp.ClientSession(headers=headers) as session:
        # Thử từng API trong danh sách
        for api_url in api_sources:
            try:
                async with session.get(api_url, timeout=12) as response:
                    if response.status == 200:
                        data = await response.json()
                        # Tìm field kết quả trong các dạng JSON khác nhau
                        result = (
                            data.get("destination") or 
                            data.get("result") or 
                            data.get("bypassed_url") or 
                            data.get("url")
                        )
                        # Nếu kết quả hợp lệ và khác link gốc ban đầu
                        if result and str(result).startswith("http") and result != target_url and "bypass.vip" not in str(result):
                            return str(result)
            except Exception as e:
                print(f"⚠️ API {api_url} không phản hồi: {e}")
                continue

    return None


# ==========================================
# 5. HÀM XỬ LÝ VÀ HIỂN THỊ KẾT QUẢ
# ==========================================
async def process_bypass(interaction: discord.Interaction, url: str, service_name: str, icon: str):
    url = url.strip()
    if url.lower().startswith("link:"):
        url = url[5:].strip()

    if not url.startswith("http://") and not url.startswith("https://"):
        await interaction.response.send_message("❌ Link không hợp lệ! Phải bắt đầu bằng `http://` hoặc `https://`", ephemeral=True)
        return

    # 1. Tạo Embed ban đầu (0%)
    embed = discord.Embed(
        title=f"{icon} Đang Bypass Link {service_name}",
        description=f"🔗 **Link gốc:** `{url}`\n\n**Tiến trình:**\n{create_progress_bar(0)}",
        color=discord.Color.gold()
    )
    embed.set_footer(text="⏳ Đang kết nối server giải mã...")
    await interaction.response.send_message(embed=embed)

    # 2. Cập nhật tiến trình (35%)
    await asyncio.sleep(1)
    embed.description = f"🔗 **Link gốc:** `{url}`\n\n**Tiến trình:**\n{create_progress_bar(35)}"
    await interaction.edit_original_response(embed=embed)

    # 3. Gọi hàm bypass
    bypassed_result = await fetch_bypassed_url(url)

    await asyncio.sleep(1)
    embed.description = f"🔗 **Link gốc:** `{url}`\n\n**Tiến trình:**\n{create_progress_bar(80)}"
    await interaction.edit_original_response(embed=embed)

    # 4. Trả kết quả cuối cùng (100%)
    if bypassed_result:
        embed.title = f"✅ Bypass Thành Công {service_name}!"
        embed.color = discord.Color.green()
        embed.description = f"🔗 **Link gốc:** `{url}`\n\n**Tiến trình:**\n{create_progress_bar(100)}"
        embed.add_field(name="🎉 Link Đích (Destination URL):", value=f"```{bypassed_result}```", inline=False)
        embed.set_footer(text="✨ Đã giải mã thành công!")
    else:
        embed.title = f"❌ Bypass Thất Bại {service_name}!"
        embed.color = discord.Color.red()
        embed.description = f"🔗 **Link gốc:** `{url}`\n\n**Tiến trình:**\n{create_progress_bar(100)}"
        embed.add_field(name="⚠️ Thông báo:", value="Không thể giải mã tự động link này. Server bypass đang quá tải hoặc link yêu cầu Captcha thủ công.", inline=False)
        embed.set_footer(text="Vui lòng thử lại sau.")

    await interaction.edit_original_response(embed=embed)


# ==========================================
# 6. KHAI BÁO CÁC LỆNH SLASH
# ==========================================
@bot.event
async def on_ready():
    print(f"✅ Bot đã đăng nhập: {bot.user.name}")
    await bot.change_presence(activity=discord.Game(name="/help | Bypass Link ⚡"))

@bot.tree.command(name="help", description="Hướng dẫn sử dụng bot bypass")
async def help_cmd(interaction: discord.Interaction):
    embed = discord.Embed(
        title="🤖 Lệnh Bypass Link Rút Gọn",
        description="Gõ `/` và chọn các lệnh sau:",
        color=discord.Color.blue()
    )
    embed.add_field(name="Lệnh", value="• `/cuty` - Bypass Cuty.io\n• `/shrinkme` - Bypass ShrinkMe.io\n• `/workink` - Bypass Work.ink", inline=False)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="cuty", description="Bypass link Cuty.io")
@app_commands.describe(link="Dán link Cuty.io")
async def cuty_cmd(interaction: discord.Interaction, link: str):
    await process_bypass(interaction, link, "Cuty.io", "✂️")

@bot.tree.command(name="shrinkme", description="Bypass link ShrinkMe.io")
@app_commands.describe(link="Dán link ShrinkMe.io")
async def shrinkme_cmd(interaction: discord.Interaction, link: str):
    await process_bypass(interaction, link, "ShrinkMe.io", "📉")

@bot.tree.command(name="workink", description="Bypass link Work.ink")
@app_commands.describe(link="Dán link Work.ink")
async def workink_cmd(interaction: discord.Interaction, link: str):
    await process_bypass(interaction, link, "Work.ink", "💼")


# ==========================================
# 7. KHỞI CHẠY BOT
# ==========================================
if __name__ == '__main__':
    keep_alive()
    TOKEN = os.environ.get('DISCORD_TOKEN')
    if TOKEN:
        bot.run(TOKEN)
