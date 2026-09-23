import os
import time
import asyncio
from threading import Thread
from flask import Flask
import discord
from discord.ext import commands
from discord import app_commands

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
        # Đồng bộ các lệnh Slash Command với Discord
        print("🔄 Đang đồng bộ Slash Commands với Discord...")
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
# 4. EVENT KHỞI ĐỘNG BOT
# ==========================================
@bot.event
async def on_ready():
    print(f"✅ Bot đã đăng nhập thành công: {bot.user.name} (ID: {bot.user.id})")
    await bot.change_presence(activity=discord.Game(name="/help | Bypass Link ⚡"))


# ==========================================
# 5. SLASH COMMAND: /help
# ==========================================
@bot.tree.command(name="help", description="Xem danh sách các lệnh hỗ trợ bypass link")
async def help_command(interaction: discord.Interaction):
    embed = discord.Embed(
        title="🤖 Danh Sách Lệnh Bypass Link",
        description="Dưới đây là các lệnh hỗ trợ bypass link rút gọn:",
        color=discord.Color.blue()
    )
    embed.add_field(
        name="🔗 Danh sách lệnh Slash:",
        value=(
            "• `/cuty link:...` - Bypass link Cuty.io / Cuttty.com\n"
            "• `/shrinkme link:...` - Bypass link ShrinkMe.io\n"
            "• `/workink link:...` - Bypass link Work.ink\n"
            "• `/help` - Xem hướng dẫn này"
        ),
        inline=False
    )
    embed.set_footer(text="⚡ Bypass Bot • Nhanh chóng & Chính xác")
    await interaction.response.send_message(embed=embed)


# ==========================================
# 6. HÀM XỬ LÝ BYPASS DÙNG CHUNG
# ==========================================
async def process_bypass(interaction: discord.Interaction, url: str, service_name: str, icon: str):
    url = url.strip()
    if url.lower().startswith("link:"):
        url = url[5:].strip()

    if not url.startswith("http://") and not url.startswith("https://"):
        await interaction.response.send_message(
            f"❌ Vui lòng nhập link hợp lệ! (Ví dụ: `https://...`)",
            ephemeral=True
        )
        return

    # Gửi phản hồi ban đầu với Embed tiến trình 0%
    embed = discord.Embed(
        title=f"{icon} Đang Bypass Link {service_name}",
        description=f"🔗 **Link nhập:** `{url}`\n\n**Tiến trình:**\n{create_progress_bar(0)}",
        color=discord.Color.gold()
    )
    embed.set_footer(text="⏳ Đang kết nối máy chủ giải mã...")
    await interaction.response.send_message(embed=embed)

    # Chạy cập nhật thanh tiến trình phần trăm %
    progress_steps = [25, 50, 75, 100]
    for p in progress_steps:
        await asyncio.sleep(1)
        embed.description = f"🔗 **Link nhập:** `{url}`\n\n**Tiến trình:**\n{create_progress_bar(p)}"
        
        if p == 100:
            embed.title = f"✅ Bypass Thành Công {service_name}!"
            embed.color = discord.Color.green()
            
            # --- DÁN LOGIC BYPASS THỰC TẾ CỦA BẠN VÀO ĐÂY ---
            bypassed_link = url  
            
            embed.add_field(name="🎉 Kết Quả Link Gốc:", value=f"```{bypassed_link}```", inline=False)
            embed.set_footer(text="✨ Hoàn tất xử lý!")
            
        await interaction.edit_original_response(embed=embed)


# ==========================================
# 7. KHAI BÁO CÁC SLASH COMMAND BYPASS
# ==========================================
@bot.tree.command(name="cuty", description="Bypass liên kết Cuty.io / Cuttty.com")
@app_commands.describe(link="Dán link Cuty.io cần bypass vào đây")
async def cuty_cmd(interaction: discord.Interaction, link: str):
    await process_bypass(interaction, link, "Cuty.io", "✂️")

@bot.tree.command(name="shrinkme", description="Bypass liên kết ShrinkMe.io")
@app_commands.describe(link="Dán link ShrinkMe.io cần bypass vào đây")
async def shrinkme_cmd(interaction: discord.Interaction, link: str):
    await process_bypass(interaction, link, "ShrinkMe.io", "📉")

@bot.tree.command(name="workink", description="Bypass liên kết Work.ink")
@app_commands.describe(link="Dán link Work.ink cần bypass vào đây")
async def workink_cmd(interaction: discord.Interaction, link: str):
    await process_bypass(interaction, link, "Work.ink", "💼")


# ==========================================
# 8. THIẾT LẬP KẾT NỐI & CHẠY BOT
# ==========================================
if __name__ == '__main__':
    keep_alive()
    
    TOKEN = os.environ.get('DISCORD_TOKEN')
    if not TOKEN:
        print("❌ LỖI KHỞI ĐỘNG: Chưa cài đặt biến môi trường DISCORD_TOKEN!")
    else:
        while True:
            try:
                bot.run(TOKEN)
                break
            except discord.errors.HTTPException as e:
                if e.status == 429:
                    print("⚠️ Dính Rate Limit (Lỗi 429). Đang chờ 30 giây...")
                    time.sleep(30)
                else:
                    print(f"⚠️ Lỗi HTTP từ Discord: {e}")
                    time.sleep(10)
            except Exception as e:
                print(f"⚠️ Lỗi kết nối Bot: {e}")
                time.sleep(10)
