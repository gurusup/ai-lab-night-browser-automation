"""
Notificador de Telegram para DevJobScout
"""
import asyncio
from typing import List, Dict, Optional
from telegram import Bot
from telegram.error import TelegramError


class TelegramNotifier:
    """Envía notificaciones de ofertas de trabajo por Telegram"""

    def __init__(self, bot_token: str, chat_id: str):
        """
        Inicializa el notificador de Telegram

        Args:
            bot_token: Token del bot de Telegram
            chat_id: ID del chat donde enviar mensajes
        """
        self.bot = Bot(token=bot_token)
        self.chat_id = chat_id

    async def send_job(self, job: Dict) -> bool:
        """
        Envía una oferta de trabajo individual

        Args:
            job: Diccionario con datos de la oferta

        Returns:
            True si se envió correctamente
        """
        try:
            message = self._format_job_message(job)
            await self.bot.send_message(
                chat_id=self.chat_id,
                text=message,
                parse_mode='HTML',
                disable_web_page_preview=False
            )
            return True
        except TelegramError as e:
            print(f"❌ Error enviando mensaje a Telegram: {e}")
            return False

    async def send_jobs_batch(
        self,
        jobs: List[Dict],
        max_per_message: int = 5
    ) -> int:
        """
        Envía múltiples ofertas de trabajo

        Args:
            jobs: Lista de ofertas
            max_per_message: Máximo de ofertas por mensaje

        Returns:
            Número de ofertas enviadas exitosamente
        """
        if not jobs:
            return 0

        sent_count = 0

        # Enviar resumen inicial
        await self._send_summary(jobs)

        # Enviar ofertas en batches
        for i in range(0, len(jobs), max_per_message):
            batch = jobs[i:i + max_per_message]
            message = self._format_jobs_batch(batch)

            try:
                await self.bot.send_message(
                    chat_id=self.chat_id,
                    text=message,
                    parse_mode='HTML',
                    disable_web_page_preview=True
                )
                sent_count += len(batch)
                await asyncio.sleep(1)  # Rate limiting
            except TelegramError as e:
                print(f"❌ Error enviando batch a Telegram: {e}")

        return sent_count

    async def send_daily_digest(
        self,
        jobs_by_platform: Dict[str, List[Dict]]
    ) -> bool:
        """
        Envía resumen diario con todas las ofertas por plataforma

        Args:
            jobs_by_platform: Diccionario {platform: [jobs]}

        Returns:
            True si se envió correctamente
        """
        try:
            message = self._format_daily_digest(jobs_by_platform)
            await self.bot.send_message(
                chat_id=self.chat_id,
                text=message,
                parse_mode='HTML',
                disable_web_page_preview=True
            )
            return True
        except TelegramError as e:
            print(f"❌ Error enviando digest diario: {e}")
            return False

    def _format_job_message(self, job: Dict) -> str:
        """Formatea una oferta individual para Telegram"""
        title = job.get('title', 'Sin título')
        company = job.get('company', 'Sin empresa')
        location = job.get('location', 'Sin ubicación')
        url = job.get('url', '')
        description = job.get('description', '')
        salary = job.get('salary')
        score = job.get('filter_score')

        message = f"<b>💼 {title}</b>\n"
        message += f"🏢 {company}\n"
        message += f"📍 {location}\n"

        if salary:
            message += f"💰 {salary}\n"

        if score:
            message += f"⭐ Score: {score:.0f}/100\n"

        if description:
            desc_short = description[:150] + "..." if len(description) > 150 else description
            message += f"\n{desc_short}\n"

        if url:
            message += f"\n🔗 <a href='{url}'>Ver oferta completa</a>"

        return message

    def _format_jobs_batch(self, jobs: List[Dict]) -> str:
        """Formatea un batch de ofertas"""
        message = "<b>📋 Nuevas ofertas encontradas:</b>\n\n"

        for i, job in enumerate(jobs, 1):
            title = job.get('title', 'Sin título')
            company = job.get('company', 'Sin empresa')
            url = job.get('url', '')
            score = job.get('filter_score')

            message += f"{i}. <b>{title}</b>\n"
            message += f"   🏢 {company}"

            if score:
                message += f" | ⭐ {score:.0f}/100"

            if url:
                message += f"\n   🔗 <a href='{url}'>Ver oferta</a>"

            message += "\n\n"

        return message

    def _format_daily_digest(self, jobs_by_platform: Dict[str, List[Dict]]) -> str:
        """Formatea el digest diario"""
        total_jobs = sum(len(jobs) for jobs in jobs_by_platform.values())

        message = "<b>🌅 Resumen Diario - DevJobScout</b>\n\n"
        message += f"<b>Total de ofertas encontradas:</b> {total_jobs}\n\n"

        for platform, jobs in jobs_by_platform.items():
            if not jobs:
                continue

            message += f"<b>📌 {platform.upper()}</b> ({len(jobs)} ofertas)\n"

            # Top 3 por score
            top_jobs = sorted(
                jobs,
                key=lambda x: x.get('filter_score', 0),
                reverse=True
            )[:3]

            for job in top_jobs:
                title = job.get('title', 'Sin título')
                company = job.get('company', 'Sin empresa')
                score = job.get('filter_score', 0)
                url = job.get('url', '')

                message += f"  • <b>{title}</b> - {company}"
                if score:
                    message += f" (⭐ {score:.0f})"
                message += "\n"
                if url:
                    message += f"    <a href='{url}'>Ver</a>\n"

            message += "\n"

        return message

    async def _send_summary(self, jobs: List[Dict]):
        """Envía un resumen inicial"""
        total = len(jobs)
        avg_score = sum(j.get('filter_score', 0) for j in jobs) / total if total else 0

        message = f"<b>🔍 DevJobScout - Nueva búsqueda</b>\n\n"
        message += f"✅ Encontradas {total} ofertas relevantes\n"
        message += f"⭐ Score promedio: {avg_score:.1f}/100\n"

        try:
            await self.bot.send_message(
                chat_id=self.chat_id,
                text=message,
                parse_mode='HTML'
            )
        except TelegramError:
            pass


# Función helper para uso rápido
async def notify_jobs_telegram(
    bot_token: str,
    chat_id: str,
    jobs: List[Dict]
) -> int:
    """
    Notifica ofertas por Telegram

    Args:
        bot_token: Token del bot
        chat_id: ID del chat
        jobs: Lista de ofertas

    Returns:
        Número de ofertas enviadas
    """
    notifier = TelegramNotifier(bot_token, chat_id)
    return await notifier.send_jobs_batch(jobs)


if __name__ == "__main__":
    # Test básico (necesitas configurar TELEGRAM_BOT_TOKEN y TELEGRAM_CHAT_ID)
    import os
    from dotenv import load_dotenv

    load_dotenv()

    token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat = os.getenv("TELEGRAM_CHAT_ID")

    if token and chat:
        sample_jobs = [
            {
                "title": "Senior Python Developer",
                "company": "Tech Company",
                "location": "Remote - Spain",
                "url": "https://example.com/job1",
                "filter_score": 85.5,
                "description": "Great opportunity for Python developers..."
            }
        ]

        asyncio.run(notify_jobs_telegram(token, chat, sample_jobs))
    else:
        print("⚠️  Configura TELEGRAM_BOT_TOKEN y TELEGRAM_CHAT_ID en .env para probar")
