#!/usr/bin/env python3
"""Spirit Shop Telegram Bot — Mini App + Stars payments"""

import json
import logging
from telegram import (
    Update, InlineKeyboardButton, InlineKeyboardMarkup,
    WebAppInfo, LabeledPrice
)
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    PreCheckoutQueryHandler, ContextTypes, filters
)

TOKEN = "8753410494:AAHjfgXiPseRoER8LijjRkQbiT0K0Kbmb6c"
MINI_APP_URL = "https://zephyr-m.github.io/digital-atelier/spirit-shop/"

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)


async def cmd_start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    kb = [[InlineKeyboardButton(
        "🍷 Открыть Spirit Shop",
        web_app=WebAppInfo(url=MINI_APP_URL)
    )]]
    await update.message.reply_text(
        "🍷 *Spirit Shop*\n"
        "Премиум алкоголь · Доставка · 18+\n\n"
        "Нажми кнопку чтобы открыть магазин:",
        reply_markup=InlineKeyboardMarkup(kb),
        parse_mode="Markdown"
    )


async def web_app_data(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Получаем данные из Mini App когда пользователь нажал 'Оплатить Stars'"""
    data = update.message.web_app_data.data
    try:
        order = json.loads(data)
        # order = { "items": [...], "total": 1700 }
        items_text = "\n".join(
            f"• {i['name']} × {i['qty']} = ⭐{i['price'] * i['qty']}"
            for i in order.get("items", [])
        )
        total = order.get("total", 0)

        # Создаём Stars инвойс (currency = XTR, provider_token = "")
        await ctx.bot.send_invoice(
            chat_id=update.effective_chat.id,
            title="Spirit Shop — Заказ",
            description=items_text or "Алкогольная продукция",
            payload=data,
            provider_token="",        # для Stars оставить пустым
            currency="XTR",           # Telegram Stars
            prices=[LabeledPrice("Итого", total)],  # Stars (целое число)
        )
    except Exception as e:
        log.error(f"web_app_data error: {e}")
        await update.message.reply_text("⚠️ Ошибка оформления заказа")


async def pre_checkout(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Telegram спрашивает — принимаем ли заказ"""
    await update.pre_checkout_query.answer(ok=True)


async def successful_payment(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Оплата прошла"""
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
