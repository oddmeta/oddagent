import requests
import json
from urllib.parse import urljoin
from datetime import datetime, timedelta
import os

from oddagent.config_loader import config
from oddagent.odd_agent_logger import logger

# ======================
# 全局变量 - 账号密码配置
# ======================
class MeetingConfig:
    """会议配置"""
    def __init__(self):

        """初始化会议配置"""
        self.IP = config.APS_CONFIG.get("ip", "10.67.20.14")
        self.USER_NAME = config.APS_CONFIG.get("user_name", "wgh1")
        self.PASSWORD = config.APS_CONFIG.get("password", "888888")
        self.OAUTH_CONSUMER_KEY = config.APS_CONFIG.get("oauth_consumer_key", "1") 
        self.OAUTH_CONSUMER_SECRET = config.APS_CONFIG.get("oauth_consumer_secret", "1")

        # 全局凭证（登录后赋值）
        self.ACCOUNT_TOKEN = config.APS_CONFIG.get("account_token", "")
        self.COOKIE_JAR = config.APS_CONFIG.get("cookie_jar", "")

        self.BASE_API = config.APS_CONFIG.get("base_api", f"http://{self.IP}/api/v1/")

        # 会议ID，入会后更新
        self.CONF_ID = config.APS_CONFIG.get("conf_id", "")

    def dump(self):
        """打印会议配置"""
        print(f"{self.__class__.__name__} dump: {self.__dict__}")

    # FIXME 当前设计里每个tool在识别intent后都会重新加载配置，导致无法存储全局变量。时间关系，先简单处理，后续再优化
    def set_confid(self, conf_id):
        """更新会议ID"""
        # self.CONF_ID = conf_id
        os.environ["odd_agent_meeting_conf_id"] = conf_id

    def get_confid(self):
        """获取会议ID"""
        conf_id = os.environ.get("odd_agent_meeting_conf_id", "")
        return conf_id
    
    def set_meeting_termlist(self, termlist):
        """更新会议终端列表"""
        os.environ["odd_agent_meeting_termlist"] = json.dumps(termlist)
    
    def get_meeting_termlist(self):
        """获取会议终端列表"""
        termlist = os.environ.get("odd_agent_meeting_termlist", "")
        if termlist:
            return json.loads(termlist)
        else:
            return []

# class MeetingExecuter(ToolExecuterImpl):
class MeetingExecuter():
    """会议助手"""
    def __init__(self, meeting_config: MeetingConfig):
        if meeting_config is None:
            meeting_config = MeetingConfig()
        else:
            self.meeting_config = meeting_config

    # ======================
    # 通用响应检查函数
    # ======================
    def check_response(self, resp, action_desc):
        """统一检查接口返回结果"""
        try:
            resp.raise_for_status()
            result = resp.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ {action_desc} 请求失败: {e}")
            return result
        except json.JSONDecodeError:
            logger.error(f"❌ {action_desc} 返回非JSON格式: {resp.text}")
            return result

        if isinstance(result, dict) and ("error" in result or "success" in result and result["success"] != 1):
            logger.error(f"❌ {action_desc} 失败: {json.dumps(result, ensure_ascii=False)}")
            return result

        logger.info(f"✅ {action_desc} 成功: {json.dumps(result, ensure_ascii=False)}")
        return result

    def is_login(self):
        """检查是否已登录"""
        return bool(self.meeting_config.ACCOUNT_TOKEN and self.meeting_config.COOKIE_JAR)

    # ======================
    # 1. 登录接口
    # ======================
    def login(self):
        token_url = urljoin(self.meeting_config.BASE_API, "system/token")
        data_key = {
            "oauth_consumer_key": self.meeting_config.OAUTH_CONSUMER_KEY,
            "oauth_consumer_secret": self.meeting_config.OAUTH_CONSUMER_SECRET,
        }

        token_resp = requests.post(token_url, data=data_key, headers={
            'Accept': 'application/json',
            "Content-Type": "application/x-www-form-urlencoded",
            "API-Level": '3'
        })
        token_result = self.check_response(token_resp, "获取token")

        account_token = token_result.get("account_token")
        if not account_token:
            logger.error(f"❌ 解析token失败: {token_result}")
            return {}

        login_url = urljoin(self.meeting_config.BASE_API, "system/login")
        login_data = {
            "username": self.meeting_config.USER_NAME,
            "password": self.meeting_config.PASSWORD,
            "account_token": account_token
        }

        login_resp = requests.post(login_url, data=login_data, headers={
            'Accept': 'application/json',
            "Content-Type": "application/x-www-form-urlencoded",
            "API-Level": '3'
        })
        login_result = self.check_response(login_resp, "登录")

        self.meeting_config.ACCOUNT_TOKEN = account_token
        self.meeting_config.COOKIE_JAR = login_resp.cookies

        return login_result


    # ======================
    # 2. 创建会议
    # ======================
    def create_conference(self, name="测试会议", start_time=None, location="会议室A", duration=240, **extra_params):
        # 该demo创建目前是即时会议，参数name和duration有效
        if not self.meeting_config.ACCOUNT_TOKEN or not self.meeting_config.COOKIE_JAR:
            self.login()

        if start_time is None:
            start_time = datetime.now() + timedelta(minutes=5)
        if isinstance(start_time, datetime):
            start_time = start_time.strftime("%Y-%m-%d %H:%M:%S")

        conf_data = {
            "name": name,
            "start_time": start_time,
            "location": location,
            "duration": duration,
            "conf_type": 0,
        }
        conf_data.update(extra_params)

        create_url = urljoin(self.meeting_config.BASE_API, "mc/confs")
        data = {
            "params": json.dumps(conf_data),
            "account_token": self.meeting_config.ACCOUNT_TOKEN
        }

        resp = requests.post(create_url, data=data, headers={
            'Accept': 'application/json',
            "Content-Type": "application/x-www-form-urlencoded",
            "API-Level": '3'
        }, cookies=self.meeting_config.COOKIE_JAR)

        return self.check_response(resp, "创建会议")


    # ======================
    # 3. 添加终端
    # ======================
    def invite_mt(self, conf_id, mt_list):
        if not self.meeting_config.ACCOUNT_TOKEN or not self.meeting_config.COOKIE_JAR:
            self.login()

        invite_url = urljoin(self.meeting_config.BASE_API, f"vc/confs/{conf_id}/mts")

        params = {
            "from_audiences": 0,
            "mts": mt_list
        }

        data = {
            "params": json.dumps(params),
            "account_token": self.meeting_config.ACCOUNT_TOKEN
        }

        resp = requests.post(invite_url, data=data, headers={
            'Accept': 'application/json',
            "Content-Type": "application/x-www-form-urlencoded",
            "API-Level": '3'
        }, cookies=self.meeting_config.COOKIE_JAR)

        return self.check_response(resp, "添加终端")

    # ======================
    # 4. 移除终端
    # ======================
    def hangup_mt(self, conf_id, mt_list):
        if not self.meeting_config.ACCOUNT_TOKEN or not self.meeting_config.COOKIE_JAR:
            self.login()

        hangup_url = urljoin(self.meeting_config.BASE_API, f"vc/confs/{conf_id}/mts")

        params = {
            "mts": mt_list
        }

        data = {
            "params": json.dumps(params),
            "account_token": self.meeting_config.ACCOUNT_TOKEN
        }

        resp = requests.delete(hangup_url, data=data, headers={
            'Accept': 'application/json',
            "Content-Type": "application/x-www-form-urlencoded",
            "API-Level": '3'
        }, cookies=self.meeting_config.COOKIE_JAR)

        return self.check_response(resp, f"移除终端 {mt_list}")

    # ======================
    # 5. 指定会议双流源
    # ======================
    def send_dual_stream(self,conf_id, mt_id):
        """
        指定会议双流源（异步操作）
        :param conf_id: 会议ID
        :param mt_id: 发双流的终端ID；为空则取消会议双流源
        """
        if not self.meeting_config.ACCOUNT_TOKEN or not self.meeting_config.COOKIE_JAR:
            self.login()

        # 接口URL
        stream_url = urljoin(self.meeting_config.BASE_API, f"vc/confs/{conf_id}/dualstream")

        params = {"mt_id": mt_id}
        data = {
            "params": json.dumps(params),
            "account_token": self.meeting_config.ACCOUNT_TOKEN
        }

        resp = requests.put(stream_url, data=data, headers={
            'Accept': 'application/json',
            "Content-Type": "application/x-www-form-urlencoded",
            "API-Level": '3'
        }, cookies=self.meeting_config.COOKIE_JAR)

        return self.check_response(resp, "指定会议双流源")



    # ======================
    # 6. 取消会议双流源
    # ======================
    def stop_dual_stream(self, conf_id, mt_id):
        """
        取消会议双流源（异步操作）
        :param conf_id: 会议ID
        :param mt_id: 要取消双流的终端ID
        """
        if not self.meeting_config.ACCOUNT_TOKEN or not self.meeting_config.COOKIE_JAR:
            self.login()

        stream_url = urljoin(self.meeting_config.BASE_API, f"vc/confs/{conf_id}/dualstream")

        # DELETE 请求允许带参数（部分接口要求附带双流源终端）
        params = {
            "mt_id": mt_id
        }
        data = {
            "params": json.dumps(params),
            "account_token": self.meeting_config.ACCOUNT_TOKEN
        }

        resp = requests.delete(stream_url, data=data, headers={
            'Accept': 'application/json',
            "Content-Type": "application/x-www-form-urlencoded",
            "API-Level": '3'
        }, cookies=self.meeting_config.COOKIE_JAR)

        return self.check_response(resp, "取消会议双流源")

    # ======================
    # 7. 结束会议
    # ======================
    def end_conference(self, conf_id):
        if not self.meeting_config.ACCOUNT_TOKEN or not self.meeting_config.COOKIE_JAR:
            self.login()

        end_url = urljoin(self.meeting_config.BASE_API, f"mc/confs/{conf_id}")
        params = {"account_token": self.meeting_config.ACCOUNT_TOKEN}

        resp = requests.delete(end_url, params=params, headers={
            'Accept': 'application/json',
            "API-Level": '3'
        }, cookies=self.meeting_config.COOKIE_JAR)

        return self.check_response(resp, "结束会议")

    # ======================
    # 8.获取所有账号信息
    # ======================
    def get_all_accounts(self, start=0, count=0, account_filter=None):
        if not self.meeting_config.ACCOUNT_TOKEN or not self.meeting_config.COOKIE_JAR:
            self.login()

        logger.info(f"获取所有账号信息, start={start}, count={count}, account_filter={account_filter}, token={self.meeting_config.ACCOUNT_TOKEN}, cookie={self.meeting_config.COOKIE_JAR}")

        # 构建URL和参数
        accounts_url = urljoin(self.meeting_config.BASE_API, "amc/accounts")
        params = {"account_token": self.meeting_config.ACCOUNT_TOKEN}
        params["start"] = start
        params["count"] = count
        if account_filter:
            params["account"] = account_filter

        # 发送请求
        resp = requests.get(accounts_url, params=params, headers={
            'Accept': 'application/json',
            "Content-Type": "application/x-www-form-urlencoded",
            "API-Level": '3'
        }, cookies=self.meeting_config.COOKIE_JAR)

        return self.check_response(resp, "获取会议成员")

    # ======================
    # 9.根据别名获取账号信息
    # ======================
    def search_accounts_by_alias(self, alias):
        if not self.meeting_config.ACCOUNT_TOKEN or not self.meeting_config.COOKIE_JAR:
            self.login()

        # 获取所有账号信息
        all_accounts = self.get_all_accounts()  # 获取所有账号
        results = []

        print(f"搜索别名: {alias}, 所有账号: {all_accounts}")

        # 搜索字段列表，从真实姓名搜索
        # search_fields = ['account', 'name']
        search_fields = ['name']

        # 遍历每个账号信息
        for account in all_accounts.get("accounts", []):
            for field in search_fields:
                if field in account and account[field] and alias.lower() in account[field].lower():
                    results.append(account)
                    break

        return {"total": len(results), "accounts": results}

    # ======================
    # 获取与会终端列表
    # ======================
    def get_mts_in_meetings(self, conf_id):
        """
        获取指定会议的终端列表
        :param conf_id: 会议ID
        :return: 成功时返回: {"success": 1, "mts": [
        {"protocol": 1, "inspection": 0, "ip": "", "poll": 0, "account_type": 5, "silence": 0, 
        "alias": "wgh1", "type": 1, "mix": 0, "v_rcv_chn_num": 0, "upload": 0, "product_id": "", 
        "v_snd_chn_num": 0, "call_mode": 0, "bitrate": 2048, "online": 0, "mt_id": "1", "mute": 0, 
        "rec": 0, "vmp": 0, "e164": "5406260000209", "account": "5406260000209"}]}
        """
        if not self.meeting_config.ACCOUNT_TOKEN or not self.meeting_config.COOKIE_JAR:
            self.login()
    
        # 构建URL和参数
        endpoints_url = urljoin(self.meeting_config.BASE_API, f"vc/confs/{conf_id}/mts")
        params = {"account_token": self.meeting_config.ACCOUNT_TOKEN}
    
        # 发送请求
        resp = requests.get(endpoints_url, params=params, headers={
            'Accept': 'application/json',
            "Content-Type": "application/x-www-form-urlencoded",
            "API-Level": '3'
        }, cookies=self.meeting_config.COOKIE_JAR)
    
        return self.check_response(resp, f"获取会议{conf_id}的终端列表")

# ======================
# 测试用例
# ======================
if __name__ == '__main__':
    assist = MeetingExecuter()
    try:
        print("=== 登录系统 ===")
        login_result = assist.login()

        print("\n=== 创建会议 ===")
        create_result = assist.create_conference(
            name="应急调度会议",
            start_time=datetime.now() + timedelta(minutes=10),
            location="指挥中心A",
            duration=180
        )
        conf_id = create_result.get("conf_id")
        if not conf_id:
            raise Exception("创建会议返回中未找到 conf_id")

        print(f"\n✅ 会议创建成功，ID: {conf_id}")

        print("\n=== 添加终端 ===")
        # mt_list = [
        #     {
        #         "account": "5406260000002",
        #         "account_type": 5,
        #         "bitrate": 2048,
        #         "protocol": 1,
        #         "forced_call": 0,
        #         "call_mode": 0
        #     },
        #     {
        #         "account": "5406260000209",
        #         "account_type": 5,
        #         "bitrate": 2048,
        #         "protocol": 1,
        #         "forced_call": 0,
        #         "call_mode": 0
        #         }
        #     ]
        mt_list = [
            {
                "account": "5406260000009",
                "account_type": 5,
                "bitrate": 2048,
                "protocol": 1,
                "forced_call": 0,
                "call_mode": 0
            }
        ]
        assist.invite_mt(conf_id, mt_list)

        print("\n=== 指定会议双流源 ===")
        assist.send_dual_stream(conf_id, "1")

        print("\n=== 取消会议双流源 ===")
        assist.stop_dual_stream(conf_id, "1")

        print("\n=== 移除终端 ===")
        mt_list = [
            {"mt_id": "1"}
        ]
        assist.hangup_mt(conf_id, mt_list)

        print("\n=== 结束会议 ===")
        assist.end_conference(conf_id)

        print("\n🎯 全部测试执行完成！")

    except Exception as e:
        print(f"\n❌ 测试执行出错: {e}")
        assist.end_conference(conf_id)
