# -*- coding: utf-8 -*-

class ToolExecuter:
    def execute(self, tool_name, slots_data, tool_cfg):
        """
        执行指定工具，返回处理结果
        :param tool_name: 工具名称
        :param slots_data: 槽位数据
        :return: 处理结果
        """
        raise NotImplementedError
