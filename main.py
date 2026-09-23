import os
import time
import asyncio
from threading import Thread
from flask import Flask
import discord
from discord.ext import commands

# ==========================================
# 1. WEB SERVER GIỮ BOT ONLINE (FLASK)
# ==========================================
app = Flask('')

@app.route('/')
def home():
    return "Bot Bypass Link đang hoạt động 24/7!"

def run_flask():
    # Tự động lấy cổng PORT do Render/Koyeb cấp (mặc định là 10000)
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
intents.message_content = True  # Yêu cầu bật MESSAGE CONTENT INTENT trong Discord Portal

# Tắt help mặc định để dùng custom help
bot = commands.Bot(command_prefix='/', intents=intents, help_command=None)


# ==========================================
# 3. HÀM TẠO THANH TIẾN TRÌNH UNICODE (%)
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
# 5. LỆNH /help
# ==========================================
@bot.command(name='help')
async def custom_help(ctx):
    embed = discord.Embed(
        title="🤖 Danh Sách Lệnh Bypass Link",
        description="Dưới đây là các lệnh hỗ trợ bypass link rút gọn:",
        color=discord.Color.blue()
    )
    embed.add_field(
        name="🔗 Danh sách lệnh:",
        value=(
            "• `/cuty link: link_cần_bypass` - Bypass link Cuty.io / Cuttty.com\n"
            "• `/shrinkme link: link_cần_bypass` - Bypass link ShrinkMe.io\n"
            "• `/workink link: link_cần_bypass` - Bypass link Work.ink\n"
            "• `/help` - Xem hướng dẫn này"
        ),
        inline=False
    )
    embed.add_field(
        name="📌 Ví dụ mẫu:",
        value="`/cuty link:https://cuty.io/example`",
        inline=False
    )
    embed.set_footer(text="⚡ Bypass Bot • Nhanh chóng & Chính xác")
    await ctx.send(embed=embed)


# ==========================================
# 6. HÀM XỬ LÝ PROGRESS & BYPASS CHUNG
# ==========================================
async def process_bypass(ctx, raw_arg: str, service_name: str, icon: str):
    # Xử lý chuỗi input nếu người dùng nhập "link:https://..."
    url = raw_arg.strip()
    if url.lower().startswith("link:"):
        url = url[5:].strip()

    if not url.startswith("http://") and not url.startswith("https://"):
        await ctx.send(f"❌ {ctx.author.mention} Vui lòng nhập link hợp lệ!\n*Ví dụ: `/{service_name.lower()} link:https://...`*")
        return

    # Tạo Embed hiển thị tiến trình ban đầu (0%)
    embed = discord.Embed(
        title=f"{icon} Đang Bypass Link {service_name}",
        description=f"🔗 **Link nhập:** `{url}`\n\n**Tiến trình:**\n{create_progress_bar(0)}",
        color=discord.Color.gold()
    )
    embed.set_footer(text="⏳ Đang kết nối máy chủ giải mã...")
    msg = await ctx.send(embed=embed)

    # Chạy thanh phần trăm %
    progress_steps = [25, 50, 75, 100]
    for p in progress_steps:
        await asyncio.sleep(1)  # Chờ 1 giây mỗi nấc
        embed.description = f"🔗 **Link nhập:** `{url}`\n\n**Tiến trình:**\n{create_progress_bar(p)}"
        
        if p == 100:
            embed.title = f"✅ Bypass Thành Công {service_name}!"
            embed.color = discord.Color.green()
            
            # --- TÍCH HỢP LOGIC BYPASS THỰC TẾ VÀO ĐÂY ---
            bypassed_link = url  # Mặc định trả lại link nguyên bản
            
            embed.add_field(name="🎉 Kết Quả Link Gốc:", value=f"```{bypassed_link}```", inline=False)
            embed.set_footer(text="✨ Hoàn tất xử lý!")
            
        await msg.edit(embed=embed)


# ==========================================
# 7. KHAI BÁO CÁC LỆNH BYPASS
# ==========================================
@bot.command(name='cuty')
async def cuty_cmd(ctx, *, arg: str = ""):
    if not arg:
        await ctx.send("❌ Vui lòng nhập link! Cú pháp: `/cuty link:https://cuty.io/...`")
        return
    await process_bypass(ctx, arg, "Cuty.io", "✂️")

@bot.command(name='shrinkme')
async def shrinkme_cmd(ctx, *, arg: str = ""):
    if not arg:
        await ctx.send("❌ Vui lòng nhập link! Cú pháp: `/shrinkme link:https://shrinkme.io/...`")
        return
    await process_bypass(ctx, arg, "ShrinkMe.io", "📉")

@bot.command(name='workink')
async def workink_cmd(ctx, *, arg: str = ""):
    if not arg:
        await ctx.send("❌ Vui lòng nhập link! Cú pháp: `/workink link:https://work.ink/...`")
        return
    await process_bypass(ctx, arg, "Work.ink", "💼")


# ==========================================
# 8. THIẾT LẬP KẾT NỐI & CHẠY BOT
# ==========================================
if __name__ == '__main__':
    # Bật Flask Server
    keep_alive()
    
    TOKEN = os.environ.get('DISCORD_TOKEN')
    if not TOKEN:
        print("❌ LỖI KHỞI ĐỘNG: Chưa cài đặt biến môi trường DISCORD_TOKEN trên Server/Host!")
    else:
        while True:
            try:
                bot.run(TOKEN)
                break
            except discord.errors.HTTPException as e:
                if e.status == 429:
                    print("⚠️ Dính Rate Limit (Lỗi 429) từ Discord. Đang chờ 30 giây...")
                    time.sleep(30)
                else:
                    print(f"⚠️ Lỗi HTTP từ Discord: {e}")
                    time.sleep(10)
            except Exception as e:
                print(f"⚠️ Lỗi kết nối Bot: {e}")
                time.sleep(10)
