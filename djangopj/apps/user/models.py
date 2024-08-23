from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser, PermissionsMixin
import ulid


class CustomUserManager(BaseUserManager):
    def create_user(self, staffcode, password=None, **extra_fields):
        """
        staffcodeとパスワードを使用してユーザーを作成
        """
        if not staffcode:
            raise ValueError("ユーザー登録にはスタッフコードが必要です")
        user = self.model(staffcode=staffcode, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, staffcode, password=None, **extra_fields):
        """
        staffcodeとパスワードを使用してスーパーユーザーを作成
        """
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("suはスタッフフラグがTrueである必要があります")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("suはスーパーユーザーフラグがTrueである必要があります")

        return self.create_user(staffcode, password, **extra_fields)


# idのデフォルト値にulid.newを使用するとmigrationファイルが毎回生成されるので
# ulidの生成を関数化することでmigrationファイルが毎回生成されないようにする
def generate_ulid():
    return str(ulid.new())


class CustomUser(AbstractBaseUser, PermissionsMixin):
    id = models.CharField(default=generate_ulid, max_length=26, primary_key=True, editable=False)
    staffcode = models.IntegerField(unique=True, null=False, verbose_name="スタッフコード")
    name = models.CharField(max_length=30, null=True, blank=True, verbose_name="ユーザー名")
    is_staff = models.BooleanField(default=False, verbose_name="スタッフフラグ")
    is_superuser = models.BooleanField(default=False, verbose_name="suフラグ")
    is_active = models.BooleanField(default=True, verbose_name="アクティブフラグ")
    last_login = models.DateTimeField(null=True, blank=True, verbose_name="最終ログイン日時")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="作成日時")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新日時")

    objects = CustomUserManager()

    USERNAME_FIELD = "staffcode"
    REQUIRED_FIELDS = []

    def __str__(self):
        return str(self.staffcode)

    class Meta:
        verbose_name = "販売員マスター"
        verbose_name_plural = "販売員マスター"
