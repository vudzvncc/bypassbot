import os
import time
import asyncio
from threading import Thread
from flask import Flask
import discord
from discord.ext import commands
from discord import app_commands
import aiohttp  # Thư viện gửi request async cực nhanh

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
# 4. HÀM GIẢI MÃ LINK BẰNG API BYPASS
# ==========================================
async def fetch_bypassed_url(target_url: str) -> str:
    """
    Gửi request tới API bypass chuyên dụng để lấy link đích cuối cùng.
    """
    # Sử dụng API Bypass miễn phí hỗ trợ Cuty, ShrinkMe, Work.ink
    api_endpoint = f"https://api.bypass.vip/bypass?url={target_url}"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(api_endpoint, headers=headers, timeout=15) as response:
                if response.status == 200:
                    data = await response.json()
                    # Lấy kết quả link đích từ phản hồi JSON
                    if data.get("status") == "success" or "destination" in data:
                        return data.get("destination") or data.get("result")
                    elif "result" in data:
                        return data["result"]
    except Exception as e:
        print(f"❌ Lỗi khi gọi API Bypass: {e}")

    # Phương án dự phòng: Nếu API lỗi, tự theo dõi Redirect của URL
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(target_url, headers=headers, allow_redirects=True, timeout=10) as resp:
                final_url = str(resp.url)
                if final_url != target_url:
                    return final_url
    except Exception:
        pass

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
    embed.set_footer(text="⏳ Đang gửi request giải mã...")
    await interaction.response.send_message(embed=embed)

    # 2. Chạy tiến trình 30% -> 70%
    await asyncio.sleep(1)
    embed.description = f"🔗 **Link gốc:** `{url}`\n\n**Tiến trình:**\n{create_progress_bar(35)}"
    await interaction.edit_original_response(embed=embed)

    # 3. Gọi hàm bypass thực tế
    bypassed_result = await fetch_bypassed_url(url)

    await asyncio.sleep(1)
    embed.description = f"🔗 **Link gốc:** `{url}`\n\n**Tiến trình:**\n{create_progress_bar(80)}"
    await interaction.edit_original_response(embed=embed)

    # 4. Trả kết quả 100%
    if bypassed_result and bypassed_result != url:
        embed.title = f"✅ Bypass Thành Công {service_name}!"
        embed.color = discord.Color.green()
        embed.description = f"🔗 **Link gốc:** `{url}`\n\n**Tiến trình:**\n{create_progress_bar(100)}"
        embed.add_field(name="🎉 Link Đích (Destination URL):", value=f"```{bypassed_result}```", inline=False)
        embed.set_footer(text="✨ Đã giải mã thành công!")
    else:
        embed.title = f"❌ Bypass Thất Bại {service_name}!"
        embed.color = discord.Color.red()
        embed.description = f"🔗 **Link gốc:** `{url}`\n\n**Tiến trình:**\n{create_progress_bar(100)}"
        embed.add_field(name="⚠️ Thông báo:", value="Không thể giải mã link này hoặc link không hỗ trợ/đã hết hạn.", inline=False)
        embed.set_footer(text="Vui lòng kiểm tra lại liên kết.")

    await interaction.edit_original_response(embed=embed)


# ==========================================
# 6. KHAI BÁO LỆNH /help VÀ CÁC LỆNH BYPASS
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
# 7. KHỞI CHẠY
# ==========================================
if __name__ == '__main__':
    keep_alive()
    TOKEN = os.environ.get('DISCORD_TOKEN')
    if TOKEN:
        bot.run(TOKEN)
