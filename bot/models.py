from django.db import models
from django.utils.timezone import now
from time import sleep
from django.db.models import Count
from django.db import transaction
from telegram import Bot
from telegram.error import TelegramError
from asgiref.sync import sync_to_async

# Create your models here.


class TelegramUser(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
    ]

    user_id = models.BigIntegerField(null=False, unique=True, verbose_name="Telegram User ID")
    first_name = models.CharField(max_length=256, blank=True, null=True, verbose_name="First Name")
    username = models.CharField(max_length=256, blank=True, null=True, verbose_name="Username")
    date_joined = models.DateTimeField(auto_now_add=True, verbose_name="Date Joined")
    last_active = models.DateTimeField(auto_now=True, verbose_name="Last Active")
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='active',
        verbose_name="User Status"
    )
    is_admin = models.BooleanField(default=False, verbose_name="Is Admin")

    class Meta:
        verbose_name = "Telegram User"
        verbose_name_plural = "Telegram Users"
        ordering = ['-last_active']

    def __str__(self):
        return f"{self.first_name} (@{self.username})" if self.username else f"{self.user_id}"

    @classmethod
    async def get_admin_ids(cls):
        """
        Admin bo'lgan userlarning IDlarini qaytaradi.
        """
        return await sync_to_async(
            lambda: list(cls.objects.filter(is_admin=True).values_list('user_id', flat=True))
        )()

    @classmethod
    async def get_today_new_users(cls):
        """
        Bugungi yangi foydalanuvchilarni qaytaradi.
        """
        today = now().date()
        return await sync_to_async(lambda: list(cls.objects.filter(date_joined__date=today)))()

    @classmethod
    async def get_daily_new_users(cls):
        """
        Har bir kun uchun yangi foydalanuvchilar sonini qaytaradi.
        """
        return await sync_to_async(
            lambda: list(cls.objects.values('date_joined__date').annotate(count=Count('id')).order_by('-date_joined__date'))
        )()

    @classmethod
    async def get_total_users(cls):
        """
        Umumiy foydalanuvchilar sonini qaytaradi.
        """
        return await sync_to_async(cls.objects.count)()

    @classmethod
    async def count_admin_users(cls):
        """
        Admin bo'lgan foydalanuvchilar sonini qaytaradi.
        """
        return await sync_to_async(lambda: cls.objects.filter(is_admin=True).count())()



    @classmethod
    async def find_inactive_users(cls, bot_token):
        """
        Nofaol foydalanuvchilarni aniqlaydi.
        :param bot_token: Telegram bot tokeni
        :return: Bloklangan foydalanuvchilar soni
        """
        from telegram import Bot
        from telegram.error import TelegramError

        bot = Bot(token=bot_token)
        blocked_users_count = 0

        # SyncToAsync faqat Django ORM bilan ishlashda kerak
        users = await sync_to_async(lambda: list(cls.objects.all()))()

        for user in users:
            try:
                await bot.send_chat_action(chat_id=user.user_id, action="typing")
            except TelegramError:
                blocked_users_count += 1

        return blocked_users_count

    @classmethod
    async def make_admin(cls, user_id):
        """
        Userni admin qiladi.
        :param user_id: Admin qilinadigan foydalanuvchining Telegram user_id-si
        :return: Yangilangan user obyekti yoki None (user topilmasa)
        """
        try:
            user = await sync_to_async(cls.objects.get)(user_id=user_id)
            user.is_admin = True
            await sync_to_async(user.save)(update_fields=['is_admin'])
            return user
        except cls.DoesNotExist:
            print(f"User with ID {user_id} does not exist.")
            return None

    @classmethod
    async def remove_admin(cls, user_id):
        """
        Userni adminlikdan chiqaradi.
        :param user_id: Adminlikdan chiqariladigan foydalanuvchining Telegram user_id-si
        :return: Yangilangan user obyekti yoki None (user topilmasa)
        """
        try:
            user = await sync_to_async(cls.objects.get)(user_id=user_id)
            user.is_admin = False
            await sync_to_async(user.save)(update_fields=['is_admin'])
            return user
        except cls.DoesNotExist:
            print(f"User with ID {user_id} does not exist.")
            return None



class Channel(models.Model):
    """Kanal yoki guruh haqida ma'lumotlarni saqlash uchun model."""
    CHANNEL_TYPE_CHOICES = [
        ('channel', 'Kanal'),
        ('group', 'Guruh'),
    ]

    channel_id = models.CharField(max_length=255, unique=True)  # Kanal ID
    name = models.CharField(max_length=255)  # Kanal nomi
    type = models.CharField(max_length=10, choices=CHANNEL_TYPE_CHOICES)  # Kanal turi
    url = models.URLField(null=True, blank=True)  # Kanalning URL manzili (agar mavjud bo'lsa)

    def __str__(self):
        return self.name


class JoinRequest(models.Model):
    """Kanalga qo'shilish so'rovi yuborgan foydalanuvchilarni saqlash uchun model."""
    user_id = models.BigIntegerField()  # Foydalanuvchi IDsi
    username = models.CharField(max_length=255, null=True, blank=True)  # Foydalanuvchi username (agar mavjud bo'lsa)
    full_name = models.CharField(max_length=255)  # Foydalanuvchi to'liq ismi
    channel = models.ForeignKey(Channel, on_delete=models.CASCADE)  # Kanalga bog'lanish (kanalga oid ma'lumot)
    request_date = models.DateTimeField(auto_now_add=True)  # So'rov yuborilgan sana va vaqt

    def __str__(self):
        return f"{self.full_name} ({self.user_id}) - {self.channel.name}"


class Referral(models.Model):
    referrer = models.ForeignKey(
        "TelegramUser", on_delete=models.CASCADE, related_name="referred_users", verbose_name="Taklif qiluvchi foydalanuvchi"
    )
    referred_user = models.ForeignKey(
        "TelegramUser", on_delete=models.CASCADE, related_name="referrals", verbose_name="Taklif qilingan foydalanuvchi"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Taklif qilingan sana")
    referral_price = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name="Referral narxi", default=0.0
    )

    class Meta:
        verbose_name = "Referral"
        verbose_name_plural = "Referral"

    def __str__(self):
        return f"{self.referrer} → {self.referred_user}"
