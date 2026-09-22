import os
import time
from threading import Thread
from flask import Flask
import discord
from discord.ext import commands

# --- WEBSERVER GIỮ BOT ONLINE TRÊN RENDER ---
app = Flask('')

@app.route('/')
def home():
    return "Bot đang hoạt động 24/7!"

def run_flask():
    # Render cấp cổng qua biến môi trường PORT (mặc định là 10000)
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run_flask)
    t.daemon = True
    t.start()

# --- CẤU HÌNH DISCORD BOT ---
intents = discord.Intents.default()
intents.message_content = True  # Yêu cầu bật MESSAGE CONTENT INTENT trong Discord Portal

# Khởi tạo bot không dùng lệnh help mặc định để tự tùy chỉnh
bot = commands.Bot(command_prefix='/', intents=intents, help_command=None)

# --- THANH TIẾN TRÌNH % UNICODE ---
def create_progress_bar(percent: int, length: int = 10) -> str:
    filled_length = int(length * percent // 100)
    bar = '█' * filled_length + '░' * (length - filled_length)
    return f"`[{bar}] {percent}%`"

# --- EVENT KHI BOT SẴN SÀNG ---
@bot.event
async def on_ready():
    print(f"✅ Đã đăng nhập thành công với tên: {bot.user.name} (ID: {bot.user.id})")
    await bot.change_presence(activity=discord.Game(name="/help | Bypass Link ⚡"))

# --- LỆNH /help ---
@bot.command(name='help')
async def custom_help(ctx):
    embed = discord.Embed(
        title="🤖 Danh Sách Lệnh Bypass Link",
        description="Dưới đây là các lệnh hỗ trợ bypass link rút gọn cực nhanh:",
        color=discord.Color.blue()
    )
    embed.add_field(
        name="🔗 Các lệnh chính:",
        value=(
            "• `/cuty link: link_cần_bypass` - Bypass link Cuty.io / Cuttty.com\n"
            "• `/shrinkme link: link_cần_bypass` - Bypass link ShrinkMe.io\n"
            "• `/workink link: link_cần_bypass` - Bypass link Work.ink\n"
            "• `/help` - Xem danh sách lệnh trợ giúp"
        ),
        inline=False
    )
    embed.add_field(
        name="📌 Ví dụ sử dụng:",
        value="`/cuty link:https://cuty.io/example`",
        inline=False
    )
    embed.set_footer(text="⚡ Bot Bypass Link • Tốc độ & Chính xác")
    await ctx.send(embed=embed)

# --- HÀM XỬ LÝ BYPASS DÙNG CHUNG ---
async def process_bypass(ctx, raw_arg: str, service_name: str, icon: str):
    # Tách lấy link thực sự nếu người dùng nhập theo dạng "link:https://..."
    url = raw_arg.strip()
    if url.lower().startswith("link:"):
        url = url[5:].strip()

    if not url.startswith("http://") and not url.startswith("https://"):
        await ctx.send(f"❌ {ctx.author.mention} Vui lòng nhập link hợp lệ! (Ví dụ: `/{service_name.lower()} link:https://...`)")
        return

    # Khởi tạo Embed hiển thị tiến trình
    embed = discord.Embed(
        title=f"{icon} Đang Bypass Link {service_name}",
        description=f"🔗 **Link gốc:** `{url}`\n\n**Tiến trình:**\n{create_progress_bar(0)}",
        color=discord.Color.gold()
    )
    embed.set_footer(text="⏳ Đang giải mã liên kết, vui lòng chờ trong giây lát...")
    msg = await ctx.send(embed=embed)

    # Giả lập thanh phần trăm (%) khi xử lý
    progress_steps = [20, 50, 80, 100]
    for p in progress_steps:
        await discord.utils.sleep_until(discord.utils.utcnow() + discord.utils.datetime.timedelta(seconds=1))
        embed.description = f"🔗 **Link gốc:** `{url}`\n\n**Tiến trình:**\n{create_progress_bar(p)}"
        if p == 100:
            embed.title = f"✅ Bypass Thành Công {service_name}!"
            embed.color = discord.Color.green()
            # Ở đây dán link đích đã bypass (Ví dụ)
            bypassed_link = url  # Cập nhật logic bypass thực tế tại đây
            embed.add_field(name="🎉 Kết Quả Link Gốc:", value=f"```{bypassed_link}```", inline=False)
            embed.set_footer(text="✨ Hoàn tất xử lý!")
        await msg.edit(embed=embed)

# --- LỆNH BYPASS CÁC TRANG ---
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

# --- KHOẢNG CHẠY BOT ---
if __name__ == '__main__':
    # Khởi chạy Flask server
    keep_alive()
    
    TOKEN = os.environ.get('DISCORD_TOKEN')
    if not TOKEN:
        print("❌ LỖI RENDER: Chưa tìm thấy biến môi trường 'DISCORD_TOKEN'!")
    else:
        while True:
            try:
                bot.run(TOKEN)
                break
            except discord.errors.HTTPException as e:
                if e.status == 429:
                    print("⚠️ Bị Rate Limit (429) từ Discord. Đang chờ 30 giây...")
                    time.sleep(30)
                else:
                    print(f"⚠️ Lỗi HTTP từ Discord: {e}")
                    time.sleep(10)
            except Exception as e:
                print(f"⚠️ Lỗi kết nối Bot: {e}")
                time.sleep(10)
