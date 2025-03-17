import asyncio
# 管理上下文

def LimitMessagesHistoryLength(ctx, limit):
    """
    限制消息历史记录长度，不删除prompt（即role=system的消息）
    
    args:
    - ctx: 上下文列表
    - limit: 限制的消息历史记录长度
    """
    # 获取当前消息历史记录， 并删除prompt消息
    ctx = list(ctx)
    prompt = ctx.pop(0)
    # 限制消息历史记录长度
    if len(ctx) > limit:
        ctx = ctx[-limit:]
    # 加回去Prompt消息
    ctx.insert(0, prompt)
    
    return ctx