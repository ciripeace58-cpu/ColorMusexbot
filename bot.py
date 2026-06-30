import os
import re
import random
import colorsys
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler

# Get token from environment variable
TOKEN = os.environ.get("BOT_TOKEN", "")

if not TOKEN:
    print("❌ ERROR: BOT_TOKEN environment variable not set!")
    print("Please add BOT_TOKEN in Railway Variables tab")
    exit(1)

print(f"✅ Token loaded successfully (length: {len(TOKEN)})")

# ===== Color Generation Functions =====
def hex_to_rgb(hex_color: str) -> tuple:
    """Convert hex color to RGB tuple"""
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def rgb_to_hex(rgb: tuple) -> str:
    """Convert RGB tuple to hex color"""
    return f"#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}"

def generate_random_color() -> dict:
    """Generate a random color with all formats"""
    r = random.randint(0, 255)
    g = random.randint(0, 255)
    b = random.randint(0, 255)
    
    # Convert to hex
    hex_color = rgb_to_hex((r, g, b))
    
    # Convert to HSL
    h, l, s = colorsys.rgb_to_hls(r/255, g/255, b/255)
    hsl = f"({round(h*360)}, {round(s*100)}%, {round(l*100)}%)"
    
    return {
        'hex': hex_color,
        'rgb': f"({r}, {g}, {b})",
        'hsl': hsl,
        'r': r,
        'g': g,
        'b': b
    }

def generate_monochromatic(base_rgb: tuple) -> list:
    """Generate monochromatic palette (5 shades)"""
    palettes = []
    for i in range(5):
        factor = 0.2 + (i * 0.15)
        new_rgb = tuple(min(255, int(c * factor)) for c in base_rgb)
        palettes.append(rgb_to_hex(new_rgb))
    return palettes

def generate_complementary(base_rgb: tuple) -> list:
    """Generate complementary palette (base + complement)"""
    h, l, s = colorsys.rgb_to_hls(base_rgb[0]/255, base_rgb[1]/255, base_rgb[2]/255)
    comp_h = (h + 0.5) % 1.0
    comp_rgb = colorsys.hls_to_rgb(comp_h, l, s)
    comp_rgb = tuple(int(c * 255) for c in comp_rgb)
    return [rgb_to_hex(base_rgb), rgb_to_hex(comp_rgb)]

def generate_analogous(base_rgb: tuple) -> list:
    """Generate analogous palette (base + 2 adjacent colors)"""
    h, l, s = colorsys.rgb_to_hls(base_rgb[0]/255, base_rgb[1]/255, base_rgb[2]/255)
    colors = []
    for offset in [-30/360, 0, 30/360]:
        new_h = (h + offset) % 1.0
        new_rgb = colorsys.hls_to_rgb(new_h, l, s)
        new_rgb = tuple(int(c * 255) for c in new_rgb)
        colors.append(rgb_to_hex(new_rgb))
    return colors

def generate_triad(base_rgb: tuple) -> list:
    """Generate triadic palette (3 colors 120 degrees apart)"""
    h, l, s = colorsys.rgb_to_hls(base_rgb[0]/255, base_rgb[1]/255, base_rgb[2]/255)
    colors = []
    for offset in [0, 1/3, 2/3]:
        new_h = (h + offset) % 1.0
        new_rgb = colorsys.hls_to_rgb(new_h, l, s)
        new_rgb = tuple(int(c * 255) for c in new_rgb)
        colors.append(rgb_to_hex(new_rgb))
    return colors

def generate_tetrad(base_rgb: tuple) -> list:
    """Generate tetradic palette (4 colors 90 degrees apart)"""
    h, l, s = colorsys.rgb_to_hls(base_rgb[0]/255, base_rgb[1]/255, base_rgb[2]/255)
    colors = []
    for offset in [0, 1/4, 1/2, 3/4]:
        new_h = (h + offset) % 1.0
        new_rgb = colorsys.hls_to_rgb(new_h, l, s)
        new_rgb = tuple(int(c * 255) for c in new_rgb)
        colors.append(rgb_to_hex(new_rgb))
    return colors

def generate_split_complementary(base_rgb: tuple) -> list:
    """Generate split complementary palette (base + 2 adjacent to complement)"""
    h, l, s = colorsys.rgb_to_hls(base_rgb[0]/255, base_rgb[1]/255, base_rgb[2]/255)
    comp_h = (h + 0.5) % 1.0
    colors = [rgb_to_hex(base_rgb)]
    for offset in [-20/360, 20/360]:
        new_h = (comp_h + offset) % 1.0
        new_rgb = colorsys.hls_to_rgb(new_h, l, s)
        new_rgb = tuple(int(c * 255) for c in new_rgb)
        colors.append(rgb_to_hex(new_rgb))
    return colors

def generate_hsl(r: int, g: int, b: int) -> str:
    """Generate HSL string from RGB"""
    h, l, s = colorsys.rgb_to_hls(r/255, g/255, b/255)
    return f"({round(h*360)}, {round(s*100)}%, {round(l*100)}%)"

# ===== Command Handlers =====
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command"""
    user = update.effective_user
    welcome_msg = (
        f"🎨 *Hello {user.first_name}!*\n\n"
        "Welcome to *ColorMusexBot* - your color generation companion!\n\n"
        "I can generate beautiful colors and palettes for your projects.\n\n"
        "*How to use:*\n"
        "• Send any message to generate a random color\n"
        "• Use /palette to create color schemes\n"
        "• Use /hex [color] to analyze a color\n"
        "• Use /help to see all commands\n\n"
        "*Example:*\n"
        "• Send: `hello` for a random color\n"
        "• Send: `/palette` for a color scheme\n"
        "• Send: `/hex #FF5733` to analyze\n\n"
        "Let's create some beautiful colors!"
    )
    await update.message.reply_text(welcome_msg, parse_mode='Markdown')

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help command"""
    help_msg = (
        "📖 *ColorMusexBot Help*\n\n"
        "*Commands:*\n"
        "/start - Welcome message\n"
        "/help - Show this help\n"
        "/palette - Generate a color palette\n"
        "/hex [color] - Analyze a hex color\n"
        "/random - Generate a random color\n"
        "/about - About this bot\n\n"
        "*Color Schemes:*\n"
        "With /palette you can generate:\n"
        "• Monochromatic\n"
        "• Complementary\n"
        "• Analogous\n"
        "• Triadic\n"
        "• Tetradic\n"
        "• Split Complementary\n\n"
        "*Example:*\n"
        "• `/hex #FF5733` - Shows RGB, HSL, and details\n"
        "• `/palette` - Creates a random color scheme"
    )
    await update.message.reply_text(help_msg, parse_mode='Markdown')

async def about_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /about command"""
    about_msg = (
        "🎨 *About ColorMusexBot*\n\n"
        "This bot generates beautiful colors and palettes.\n\n"
        "*Features:*\n"
        "✓ Random color generation\n"
        "✓ 6 different color schemes\n"
        "✓ Color analysis (RGB, HSL)\n"
        "✓ Fast and responsive\n"
        "✓ Free and unlimited\n"
        "✓ Privacy-focused\n\n"
        "*Powered by:*\n"
        "• python-telegram-bot\n"
        "• colorsys (Python built-in)\n"
        "• Deployed on Railway\n\n"
        "Built with ❤️ using open-source tools."
    )
    await update.message.reply_text(about_msg, parse_mode='Markdown')

async def random_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /random command - generate a random color"""
    color = generate_random_color()
    await send_color_response(update, color)

async def hex_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /hex command - analyze a hex color"""
    parts = update.message.text.split(' ', 1)
    if len(parts) < 2:
        await update.message.reply_text(
            "⚠️ Please provide a hex color.\n"
            "Example: `/hex #FF5733`",
            parse_mode='Markdown'
        )
        return
    
    hex_input = parts[1].strip()
    
    # Clean hex input
    if not hex_input.startswith('#'):
        hex_input = f"#{hex_input}"
    
    # Validate hex
    if not re.match(r'^#[0-9a-fA-F]{6}$', hex_input):
        await update.message.reply_text(
            "⚠️ Invalid hex color. Please use format: `#FF5733`",
            parse_mode='Markdown'
        )
        return
    
    try:
        r, g, b = hex_to_rgb(hex_input)
        color = {
            'hex': hex_input,
            'rgb': f"({r}, {g}, {b})",
            'hsl': generate_hsl(r, g, b),
            'r': r,
            'g': g,
            'b': b
        }
        await send_color_response(update, color, analyze=True)
    except:
        await update.message.reply_text("⚠️ Invalid hex color. Please use format: `#FF5733`", parse_mode='Markdown')

async def send_color_response(update: Update, color: dict, analyze: bool = False):
    """Send color response with formatting"""
    response = (
        f"🎨 *Your Color*\n\n"
        f"• *HEX:* `{color['hex']}`\n"
        f"• *RGB:* `{color['rgb']}`\n"
        f"• *HSL:* `{color['hsl']}`\n"
    )
    
    if analyze:
        # Calculate color temperature
        r, g, b = color['r'], color['g'], color['b']
        brightness = (r * 299 + g * 587 + b * 114) / 1000
        is_dark = brightness < 128
        
        response += (
            f"\n*Details:*\n"
            f"• *Brightness:* {round(brightness)}/255\n"
            f"• *Type:* {'Dark' if is_dark else 'Light'}\n"
            f"• *Temp:* {'Warm' if r > b else 'Cool' if b > r else 'Neutral'}"
        )
    
    await update.message.reply_text(response, parse_mode='Markdown')

async def palette_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /palette command - generate color palette"""
    keyboard = [
        [
            InlineKeyboardButton("🌈 Monochromatic", callback_data="scheme_mono"),
            InlineKeyboardButton("🎯 Complementary", callback_data="scheme_comp")
        ],
        [
            InlineKeyboardButton("🎨 Analogous", callback_data="scheme_analog"),
            InlineKeyboardButton("🔺 Triadic", callback_data="scheme_triad")
        ],
        [
            InlineKeyboardButton("🔷 Tetradic", callback_data="scheme_tetrad"),
            InlineKeyboardButton("🔶 Split Comp", callback_data="scheme_split")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "🎨 *Select Color Scheme*\n\n"
        "Choose a scheme for your palette:",
        parse_mode='Markdown',
        reply_markup=reply_markup
    )

async def palette_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle palette scheme selection"""
    query = update.callback_query
    await query.answer()
    
    scheme = query.data.replace("scheme_", "")
    base_color = generate_random_color()
    base_rgb = (base_color['r'], base_color['g'], base_color['b'])
    
    # Generate palette based on scheme
    if scheme == "mono":
        palette = generate_monochromatic(base_rgb)
        scheme_name = "Monochromatic"
    elif scheme == "comp":
        palette = generate_complementary(base_rgb)
        scheme_name = "Complementary"
    elif scheme == "analog":
        palette = generate_analogous(base_rgb)
        scheme_name = "Analogous"
    elif scheme == "triad":
        palette = generate_triad(base_rgb)
        scheme_name = "Triadic"
    elif scheme == "tetrad":
        palette = generate_tetrad(base_rgb)
        scheme_name = "Tetradic"
    elif scheme == "split":
        palette = generate_split_complementary(base_rgb)
        scheme_name = "Split Complementary"
    else:
        await query.edit_message_text("⚠️ Unknown scheme.")
        return
    
    # Format palette response
    palette_display = "\n".join([f"• `{color}`" for color in palette])
    response = (
        f"🎨 *{scheme_name} Palette*\n\n"
        f"{palette_display}\n\n"
        f"💡 Try /palette for more schemes\n"
        f"📐 Based on: `{base_color['hex']}`"
    )
    
    await query.edit_message_text(response, parse_mode='Markdown')

# ===== Message Handler =====
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle regular text messages - generate random color"""
    text = update.message.text
    
    if text.startswith('/'):
        return
    
    if len(text.strip()) < 1:
        return
    
    # Generate random color
    color = generate_random_color()
    await send_color_response(update, color)

# ===== Error Handler =====
async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Log errors"""
    print(f"❌ Error: {context.error}")
    try:
        if update and update.message:
            await update.message.reply_text(
                "⚠️ An error occurred. Please try again later."
            )
    except:
        pass

# ===== Main Function =====
def main():
    """Start the bot"""
    print("🚀 Starting ColorMusexBot...")
    
    try:
        application = Application.builder().token(TOKEN).build()
        print("✅ Application built successfully")
        
        # Command handlers
        application.add_handler(CommandHandler("start", start_command))
        application.add_handler(CommandHandler("help", help_command))
        application.add_handler(CommandHandler("about", about_command))
        application.add_handler(CommandHandler("random", random_command))
        application.add_handler(CommandHandler("hex", hex_command))
        application.add_handler(CommandHandler("palette", palette_command))
        
        # Callback handler for palette schemes
        application.add_handler(CallbackQueryHandler(palette_callback, pattern="scheme_"))
        
        # Message handler
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
        
        # Error handler
        application.add_error_handler(error_handler)
        
        print("✅ Bot is running! Waiting for messages...")
        application.run_polling(allowed_updates=Update.ALL_TYPES)
        
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        raise

if __name__ == "__main__":
    main()
