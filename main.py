import os
import re
import time
import asyncio
from threading import Thread
from flask import Flask
import discord
from discord.ext import commands
from discord import app_commands
import aiohttp
from bs4 import BeautifulSoup

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
# 2. CẤU HÌNH DISCORD BOT
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

def create_progress_bar(percent: int, length: int = 10) -> str:
    filled_length = int(length * percent // 100)
    bar = '█' * filled_length + '░' * (length - filled_length)
    return f"`[{bar}] {percent}%`"


# ==========================================
# 3. HÀM XỬ LÝ BYPASS ĐA TẦNG (CHỐNG LỖI)
# ==========================================
async def fetch_universal_bypass(url: str) -> str:
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
    }

    # Tầng 1: Tự bóc tách HTML & Redirect direct
    try:
        async with aiohttp.ClientSession(headers=headers) as session:
            async with session.get(url, allow_redirects=True, timeout=10) as resp:
                final_url = str(resp.url)
                html = await resp.text()

                # Kiểm tra nếu HTTP redirect nhảy thẳng qua trang đích
                if not any(domain in final_url.lower() for domain in ["cuty.io", "cuttty.com", "shrinkme.io", "work.ink"]):
                    return final_url

                # Bóc tách Meta Refresh & JavaScript location
                soup = BeautifulSoup(html, 'html.parser')
                meta_refresh = soup.find('meta', attrs={'http-equiv': re.compile(r'refresh', re.I)})
                if meta_refresh and 'content' in meta_refresh.attrs:
                    content = meta_refresh['content']
                    if 'url=' in content.lower():
                        extracted_url = content.split('url=')[-1].strip('\'"')
                        if extracted_url.startswith("http"):
                            return extracted_url

                js_urls = re.findall(r'window\.location(?:\.href)?\s*=\s*["\']([^"\']+)["\']', html)
                for j_url in js_urls:
                    if j_url.startswith("http") and not any(x in j_url for x in ["cuty", "cuttty", "shrinkme", "work.ink"]):
                        return j_url

                # Thử gửi Token Form nếu có
                inputs = soup.find_all('input')
                data = {inp.get('name'): inp.get('value') for inp in inputs if inp.get('name') and inp.get('value')}
                if data:
                    await asyncio.sleep(1.5)
                    async with session.post(final_url, data=data, timeout=8) as resp2:
                        html2 = await resp2.text()
                        soup2 = BeautifulSoup(html2, 'html.parser')
                        a_tag = soup2.find('a', id='slink') or soup2.find('a', class_='btn-success')
                        if a_tag and a_tag.get('href') and a_tag.get('href').startswith("http"):
                            return a_tag.get('href')

    except Exception as e:
        print(f"⚠️ Lỗi bốc tách nội bộ: {e}")

    # Tầng 2: Xoay vòng API dự phòng
    backup_apis = [
        f"https://api.bypasser.su/api/bypass?url={url}",
        f"https://free-bypass-api.vercel.app/api/bypass?url={url}",
        f"https://ethon.site/api/bypass?url={url}"
    ]

    async with aiohttp.ClientSession(headers=headers) as session:
        for api_endpoint in backup_apis:
            try:
                async with session.get(api_endpoint, timeout=10) as r:
                    if r.status == 200:
                        res = await r.json()
                        result = res.get("destination") or res.get("result") or res.get("bypassed_url") or res.get("url")
                        if result and str(result).startswith("http") and result != url and "bypass.vip" not in str(result):
                            return str(result)
            except Exception:
                continue

    return None


# ==========================================
# 4. LUỒNG XỬ LÝ CHUNG
# ==========================================
async def process_bypass(interaction: discord.Interaction, url: str, service_name: str, icon: str):
    url = url.strip()
    if url.lower().startswith("link:"):
        url = url[5:].strip()

    if not url.startswith("http://") and not url.startswith("https://"):
        await interaction.response.send_message("❌ Link không hợp lệ! Phải bắt đầu bằng `http://` hoặc `https://`", ephemeral=True)
        return

    embed = discord.Embed(
        title=f"{icon} Đang Bypass Link {service_name}",
        description=f"🔗 **Link gốc:** `{url}`\n\n**Tiến trình:**\n{create_progress_bar(0)}",
        color=discord.Color.gold()
    )
    embed.set_footer(text="⏳ Đang phân tích dữ liệu liên kết...")
    await interaction.response.send_message(embed=embed)

    await asyncio.sleep(1)
    embed.description = f"🔗 **Link gốc:** `{url}`\n\n**Tiến trình:**\n{create_progress_bar(45)}"
    await interaction.edit_original_response(embed=embed)

    # Chạy giải mã
    bypassed_result = await fetch_universal_bypass(url)

    await asyncio.sleep(1)
    embed.description = f"🔗 **Link gốc:** `{url}`\n\n**Tiến trình:**\n{create_progress_bar(85)}"
    await interaction.edit_original_response(embed=embed)

    # Kiểm tra xem link trả về có hợp lệ không (tránh link trung gian Cuty/ShrinkMe)
    is_valid = (
        bypassed_result 
        and bypassed_result != url 
        and not any(x in bypassed_result.lower() for x in ["cutty.com", "cuty.io", "shrinkme.io", "work.ink"])
    )

    if is_valid:
        embed.title = f"✅ Bypass Thành Công {service_name}!"
        embed.color = discord.Color.green()
        embed.description = f"🔗 **Link gốc:** `{url}`\n\n**Tiến trình:**\n{create_progress_bar(100)}"
        embed.add_field(name="🎉 Link Đích (Destination URL):", value=f"```{bypassed_result}```", inline=False)
        embed.set_footer(text="✨ Đã giải mã thành công!")
    else:
        embed.title = f"❌ Bypass Thất Bại {service_name}!"
        embed.color = discord.Color.red()
        embed.description = f"🔗 **Link gốc:** `{url}`\n\n**Tiến trình:**\n{create_progress_bar(100)}"
        embed.add_field(name="⚠️ Thông báo:", value="Link dính Captcha Cloudflare bắt buộc xác minh tay hoặc link đã hết hạn.", inline=False)
        embed.set_footer(text="Vui lòng thử lại sau.")

    await interaction.edit_original_response(embed=embed)


# ==========================================
# 5. GIỮ NGUYÊN 4 LỆNH CŨ (/help, /cuty, /shrinkme, /workink)
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


if __name__ == '__main__':
    keep_alive()
    TOKEN = os.environ.get('DISCORD_TOKEN')
    if TOKEN:
        bot.run(TOKEN)
