"""
清理 Jenkins Job 的 cron_enabled 字段

使用方法:
python manage.py clean_jenkins_cron
"""
from django.core.management.base import BaseCommand
from jenkins_integration.models import JenkinsJob


class Command(BaseCommand):
    help = '清理所有 Jenkins Job 的 cron_enabled 字段，将其设置为 False'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='仅查看将要清理的数据，不实际执行',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        # 查询所有启用了 cron 的 Jobs
        jobs_with_cron = JenkinsJob.objects.filter(cron_enabled=True)
        count = jobs_with_cron.count()
        
        self.stdout.write(self.style.WARNING(f'\n找到 {count} 个启用了定时任务的 Jenkins Jobs:\n'))
        
        for job in jobs_with_cron:
            self.stdout.write(
                f'  - ID: {job.id}, Name: {job.name}, '
                f'Schedule: {job.cron_schedule or "(空)"}'
            )
        
        if count == 0:
            self.stdout.write(self.style.SUCCESS('\n✅ 没有需要清理的数据'))
            return
        
        if dry_run:
            self.stdout.write(self.style.WARNING('\n⚠️  Dry-run 模式，不执行实际清理'))
            self.stdout.write(f'如需执行清理，运行: python manage.py clean_jenkins_cron')
            return
        
        # 确认操作
        self.stdout.write(self.style.WARNING(f'\n将清理 {count} 个 Jobs 的定时任务配置'))
        confirm = input('确认执行? (yes/no): ')
        
        if confirm.lower() != 'yes':
            self.stdout.write(self.style.ERROR('❌ 操作已取消'))
            return
        
        # 执行清理
        updated = jobs_with_cron.update(
            cron_enabled=False,
            cron_schedule=''
        )
        
        self.stdout.write(self.style.SUCCESS(f'\n✅ 成功清理 {updated} 个 Jobs 的定时任务配置'))
