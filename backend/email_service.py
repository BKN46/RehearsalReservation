from flask_mail import Mail, Message
from flask import current_app, render_template_string
import os

mail = Mail()

def init_mail(app):
    """Initialize Flask-Mail with app configuration"""
    app.config['MAIL_SERVER'] = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
    app.config['MAIL_PORT'] = int(os.environ.get('MAIL_PORT', 587))
    app.config['MAIL_USE_TLS'] = os.environ.get('MAIL_USE_TLS', 'true').lower() == 'true'
    app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
    app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
    app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('MAIL_DEFAULT_SENDER', os.environ.get('MAIL_USERNAME'))
    
    mail.init_app(app)
    return mail

def send_verification_email(user_email, user_name, verification_token):
    """Send email verification link to user"""
    try:
        # 构建验证链接
        # 注意：这里需要根据实际前端部署地址修改
        frontend_url = os.environ.get('FRONTEND_URL', 'http://localhost:5173')
        verification_link = f"{frontend_url}/verify-email?token={verification_token}"
        
        # 邮件主题
        subject = "音协预约 - 邮箱验证"
        
        # 邮件内容（HTML格式）
        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                }}
                .container {{
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                    background-color: #f9f9f9;
                }}
                .content {{
                    background-color: white;
                    padding: 30px;
                    border-radius: 8px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                }}
                .button {{
                    display: inline-block;
                    padding: 12px 30px;
                    background-color: #409eff;
                    color: white;
                    text-decoration: none;
                    border-radius: 4px;
                    margin: 20px 0;
                }}
                .footer {{
                    margin-top: 20px;
                    padding-top: 20px;
                    border-top: 1px solid #eee;
                    font-size: 12px;
                    color: #666;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="content">
                    <h2>欢迎使用音协预约系统！</h2>
                    <p>亲爱的 {user_name}，</p>
                    <p>感谢您注册音协预约系统。为了确保您的账户安全，请点击下方按钮验证您的邮箱地址：</p>
                    <div style="text-align: center;">
                        <a href="{verification_link}" class="button">验证邮箱</a>
                    </div>
                    <p>或者复制以下链接到浏览器中打开：</p>
                    <p style="word-break: break-all; color: #409eff;">{verification_link}</p>
                    <p><strong>注意：</strong>此验证链接将在30分钟后失效。</p>
                    <div class="footer">
                        <p>如果您没有注册音协预约系统，请忽略此邮件。</p>
                        <p>此邮件由系统自动发送，请勿直接回复。</p>
                    </div>
                </div>
            </div>
        </body>
        </html>
        """
        
        # 文本版本（备用）
        text_body = f"""
        欢迎使用音协预约系统！
        
        亲爱的 {user_name}，
        
        感谢您注册音协预约系统。为了确保您的账户安全，请访问以下链接验证您的邮箱地址：
        
        {verification_link}
        
        注意：此验证链接将在30分钟后失效。
        
        如果您没有注册音协预约系统，请忽略此邮件。
        
        ---
        此邮件由系统自动发送，请勿直接回复。
        """
        
        msg = Message(
            subject=subject,
            recipients=[user_email],
            body=text_body,
            html=html_body
        )
        
        mail.send(msg)
        return True
    except Exception as e:
        current_app.logger.error(f"Failed to send verification email: {str(e)}")
        return False

def send_password_reset_email(user_email, user_name, reset_token):
    """Send password reset link to user (future feature)"""
    try:
        frontend_url = os.environ.get('FRONTEND_URL', 'http://localhost:5173')
        reset_link = f"{frontend_url}/reset-password?token={reset_token}"
        
        subject = "音协预约 - 重置密码"
        
        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                }}
                .container {{
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                    background-color: #f9f9f9;
                }}
                .content {{
                    background-color: white;
                    padding: 30px;
                    border-radius: 8px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                }}
                .button {{
                    display: inline-block;
                    padding: 12px 30px;
                    background-color: #f56c6c;
                    color: white;
                    text-decoration: none;
                    border-radius: 4px;
                    margin: 20px 0;
                }}
                .footer {{
                    margin-top: 20px;
                    padding-top: 20px;
                    border-top: 1px solid #eee;
                    font-size: 12px;
                    color: #666;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="content">
                    <h2>密码重置请求</h2>
                    <p>亲爱的 {user_name}，</p>
                    <p>我们收到了您的密码重置请求。请点击下方按钮重置您的密码：</p>
                    <div style="text-align: center;">
                        <a href="{reset_link}" class="button">重置密码</a>
                    </div>
                    <p>或者复制以下链接到浏览器中打开：</p>
                    <p style="word-break: break-all; color: #f56c6c;">{reset_link}</p>
                    <p><strong>注意：</strong>此重置链接将在30分钟后失效。</p>
                    <div class="footer">
                        <p>如果您没有请求重置密码，请忽略此邮件，您的密码不会被更改。</p>
                        <p>此邮件由系统自动发送，请勿直接回复。</p>
                    </div>
                </div>
            </div>
        </body>
        </html>
        """
        
        text_body = f"""
        密码重置请求
        
        亲爱的 {user_name}，
        
        我们收到了您的密码重置请求。请访问以下链接重置您的密码：
        
        {reset_link}
        
        注意：此重置链接将在30分钟后失效。
        
        如果您没有请求重置密码，请忽略此邮件，您的密码不会被更改。
        
        ---
        此邮件由系统自动发送，请勿直接回复。
        """
        
        msg = Message(
            subject=subject,
            recipients=[user_email],
            body=text_body,
            html=html_body
        )
        
        mail.send(msg)
        return True
    except Exception as e:
        current_app.logger.error(f"Failed to send password reset email: {str(e)}")
        return False
