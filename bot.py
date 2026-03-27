#!/usr/bin/env python3
"""Spirit Shop Telegram Bot — Mini App + Stars payments"""

import json
import logging
import os
from dotenv import load_dotenv
from telegram import (
    Update, InlineKeyboardButton, InlineKeyboardMarkup,
    WebAppInfo, LabeledPrice
)
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    PreCheckoutQueryHandler, ContextTypes, filters
)

load_dotenv()
TOKEN = os.environ["BOT_TOKEN"]
MINI_APP_URL = os.environ.get("MINI_APP_URL", "https://zephyr-m.github.io/digital-atelier/spirit-shop/")
BOT_NAME = os.environ.get("BOT_NAME", "Spirit Shop")
BOT_EMOJI = os.environ.get("BOT_EMOJI", "🍷")
BOT_DESC = os.environ.get("BOT_DESC", "Премиум алкоголь · Доставка · 18+")

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)


async def cmd_start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    kb = [[InlineKeyboardButton(
        f"{BOT_EMOJI} Открыть {BOT_NAME}",
        web_app=WebAppInfo(url=MINI_APP_URL)
    )]]
    await update.message.reply_text(
        f"{BOT_EMOJI} *{BOT_NAME}*\n"
        f"{BOT_DESC}\n\n"
        "Нажми кнопку чтобы открыть:",
        reply_markup=InlineKeyboardMarkup(kb),
        parse_mode="Markdown"
    )


async def web_app_data(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    data = update.message.web_app_data.data
    try:
        order = json.loads(data)
        items_text = "\n".join(
            f"• {i['name']} × {i['qty']} = ⭐{i['price'] * i['qty']}"
            for i in order.get("items", [])
        )
        total = order.get("total", 0)
        await ctx.bot.send_invoice(
            chat_id=update.effective_chat.id,
            title="Spirit Shop — Заказ",
            description=items_text or "Алкогольная продукция",
            payload=data,
            provider_token="",
            currency="XTR",
            prices=[LabeledPrice("Итого", total)],
        )
    except Exception as e:
        log.error(f"web_app_data error: {e}")
        await update.message.reply_text("⚠️ Ошибка оформления заказа")


async def pre_checkout(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.pre_checkout_query.answer(ok=True)


async def successful_payment(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    stars = update.message.successful_payment.total_amount
    await update.message.reply_text(
        f"✅ Оплата {stars} ⭐ прошла!\n"
        "Ваш заказ принят. Ожидайте доставку."
    )


def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(MessageHandler(filters.StatusUpdate.WEB_APP_DATA, web_app_data))
    app.add_handler(PreCheckoutQueryHandler(pre_checkout))
    app.add_handler(MessageHandler(filters.SUCCESSFUL_PAYMENT, successful_payment))
    log.info("Bot started (polling)")
    app.run_polling()


if __name__ == "__main__":
    main()
