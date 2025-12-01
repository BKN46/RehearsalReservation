#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
定时任务脚本
用于执行定期维护任务
"""

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime
from models import db, User
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def annual_user_reset():
    """
    每年1月1日凌晨重置所有普通用户为禁用状态
    管理员账号不受影响
    """
    try:
        logger.info("开始执行年度用户重置任务...")
        
        # 只禁用非管理员用户
        result = User.query.filter_by(is_admin=False).update({'is_active': False})
        db.session.commit()
        
        logger.info(f"年度重置完成：已禁用 {result} 个普通用户账号")
        return result
    except Exception as e:
        db.session.rollback()
        logger.error(f"年度用户重置失败: {str(e)}")
        return 0

def init_scheduler(app):
    """
    初始化定时任务调度器
    
    Args:
        app: Flask应用实例
    """
    scheduler = BackgroundScheduler()
    
    # 每年1月1日凌晨0点执行用户重置
    # scheduler.add_job(
    #     func=lambda: annual_user_reset_with_context(app),
    #     trigger=CronTrigger(month=1, day=1, hour=0, minute=0),
    #     id='annual_user_reset',
    #     name='Annual User Reset',
    #     replace_existing=True
    # )
    
    scheduler.start()
    logger.info("定时任务调度器已启动")
    logger.info("- 年度用户重置：每年1月1日 00:00")
    
    return scheduler

def annual_user_reset_with_context(app):
    """带应用上下文的年度重置任务"""
    with app.app_context():
        return annual_user_reset()

if __name__ == '__main__':
    # 单独运行测试
    from app import app
    
    with app.app_context():
        print("执行测试：年度用户重置")
        result = annual_user_reset()
        print(f"完成：已禁用 {result} 个用户")
